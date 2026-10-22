#!/usr/bin/env python3
"""Crea il Reel animato (MP4 9:16) di una pop art a partire da SVG + palette.

Uso: python3 tools/reel.py art/AAAA-MM-GG.svg art/AAAA-MM-GG.json reels/AAAA-MM-GG.mp4

- Rende le 3 palette a 1080x1350 e le centra su una tela 1080x1920: le fasce sopra
  e sotto sono un campo di pois nei colori della palette (BG + DOT).
- Animazione di 11 s a 30 fps: apertura a iride dal centro, poi le tre visioni con uno
  zoom lento, unite da transizioni "a pois" (cerchi che crescono a griglia), e ritorno
  alla prima visione per un loop pulito.
- Audio originale sintetizzato (arpeggio pentatonico morbido + "pop" sulle transizioni),
  AAC 48 kHz stereo 128 kbps.
- Video H.264, yuv420p, GOP chiuso, moov in testa (faststart): requisiti dell'API Reel.
Stampa durata, dimensione del file e la posizione consigliata per la copertina (ms).
"""
import io, json, math, os, re, subprocess, sys, tempfile, wave

import cairosvg
import numpy as np
from PIL import Image, ImageDraw

W, H = 1080, 1920
FPS = 30
DUR = 11.0
TR = 0.4  # durata di una transizione a pois (s)
IRIS = 0.6
# (inizio, palette) delle tre visioni + ritorno alla prima
SEGMENTS = [(0.0, 0), (3.6, 1), (6.8, 2), (10.0, 0)]
COVER_MS = 2000


def render_palettes(svg_path, pal_path):
    tpl = open(svg_path, encoding="utf-8").read()
    palettes = json.load(open(pal_path, encoding="utf-8"))["palettes"]
    if len(palettes) != 3:
        sys.exit("servono esattamente 3 palette")
    root = re.search(r"<svg\b[^>]*>", tpl).group(0)
    w = int(float(re.search(r'\bwidth="([\d.]+)', root).group(1)))
    h = int(float(re.search(r'\bheight="([\d.]+)', root).group(1)))
    frames = []
    for pal in palettes:
        svg = tpl
        for k, v in pal.items():
            svg = svg.replace("{{%s}}" % k, v)
        png = cairosvg.svg2png(bytestring=svg.encode(), output_width=w, output_height=h)
        art = Image.open(io.BytesIO(png)).convert("RGB")
        if art.width != W:
            art = art.resize((W, round(art.height * W / art.width)), Image.LANCZOS)
        frames.append(compose(art, pal))
    return frames


def compose(art, pal):
    """Tela 9:16: campo di pois in alto e in basso, opera al centro."""
    canvas = Image.new("RGB", (W, H), pal["BG"])
    d = ImageDraw.Draw(canvas)
    top = (H - art.height) // 2
    step = 54
    for row, y in enumerate(range(step // 2, H, step)):
        # i pois crescono avvicinandosi all'opera, come se il pattern continuasse
        dist = min(abs(y - top), abs(y - (top + art.height)))
        r = max(4, 15 - dist / 30)
        off = step // 2 if row % 2 else 0
        for x in range(off - step, W + step, step):
            d.ellipse([x - r, y - r, x + r, y + r], fill=pal["DOT"])
    canvas.paste(art, (0, top))
    # filo nero sopra e sotto l'opera, come i contorni pop
    d.rectangle([0, top - 6, W, top - 1], fill=pal["INK"])
    d.rectangle([0, top + art.height, W, top + art.height + 5], fill=pal["INK"])
    return canvas


def zoomed(img, z):
    if z <= 1.0001:
        return img
    cw, ch = W / z, H / z
    x0, y0 = (W - cw) / 2, (H - ch) / 2
    return img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch))


def dot_mask(p):
    """Maschera a pois: cerchi su griglia sfalsata che crescono fino a coprire tutto."""
    m = Image.new("L", (W, H), 0)
    if p <= 0:
        return m
    d = ImageDraw.Draw(m)
    step = 96
    rmax = step * 0.75
    for row, y in enumerate(range(0, H + step, step)):
        off = step // 2 if row % 2 else 0
        for x in range(off - step, W + step, step):
            # ritardo radiale dal centro: l'onda parte dal soggetto
            delay = math.hypot(x - W / 2, y - H / 2) / math.hypot(W / 2, H / 2) * 0.45
            q = min(1.0, max(0.0, (p - delay) / 0.55))
            r = rmax * (q ** 0.8)
            if r > 0.5:
                d.ellipse([x - r, y - r, x + r, y + r], fill=255)
    return m


def iris_mask(p):
    m = Image.new("L", (W, H), 0)
    r = math.hypot(W / 2, H / 2) * (1 - (1 - p) ** 3)
    ImageDraw.Draw(m).ellipse([W / 2 - r, H / 2 - r, W / 2 + r, H / 2 + r], fill=255)
    return m


def frame_at(t, imgs, first_bg):
    # segmento corrente e zoom lento dentro il segmento
    idx = max(i for i, (s, _) in enumerate(SEGMENTS) if t >= s)
    start, pal = SEGMENTS[idx]
    end = SEGMENTS[idx + 1][0] if idx + 1 < len(SEGMENTS) else DUR
    z = 1.0 + 0.05 * (t - start) / (end - start)
    cur = zoomed(imgs[pal], z)
    if idx == 0 and t < IRIS:
        bg = Image.new("RGB", (W, H), first_bg)
        return Image.composite(cur, bg, iris_mask(t / IRIS))
    if idx > 0 and t < start + TR:
        prev_start, prev_pal = SEGMENTS[idx - 1]
        prev = zoomed(imgs[prev_pal], 1.05)
        return Image.composite(cur, prev, dot_mask((t - start) / TR))
    return cur


def synth_audio(path):
    sr = 48000
    n = int(DUR * sr)
    t = np.arange(n) / sr
    out = np.zeros(n)

    def pluck(at, freq, amp, decay=5.0, length=1.2):
        i0 = int(at * sr)
        k = np.arange(int(length * sr))
        tt = k / sr
        env = np.exp(-decay * tt) * np.minimum(1, tt * 400)
        tone = np.sin(2 * np.pi * freq * tt) + 0.35 * np.sin(2 * np.pi * 2 * freq * tt) + 0.12 * np.sin(2 * np.pi * 3 * freq * tt)
        seg = amp * env * tone
        i1 = min(n, i0 + len(seg))
        out[i0:i1] += seg[: i1 - i0]

    # arpeggio pentatonico (Do maggiore) a 100 bpm, croma = 0.3 s
    notes = [523.25, 659.25, 783.99, 880.00, 783.99, 659.25, 587.33, 659.25]
    beat = 0.3
    k = 0
    tt = 0.6
    while tt < DUR - 0.3:
        pluck(tt, notes[k % len(notes)], 0.10 if k % 2 else 0.14)
        if k % 8 == 0:
            pluck(tt, 130.81, 0.12, decay=2.5, length=2.0)  # basso
        k += 1
        tt += beat
    # "pop" sulle aperture e sulle transizioni
    for s, _ in SEGMENTS:
        i0 = int(s * sr)
        L = int(0.12 * sr)
        tt2 = np.arange(L) / sr
        f = 900 * np.exp(-tt2 * 25) + 300
        pop = 0.22 * np.exp(-tt2 * 40) * np.sin(2 * np.pi * np.cumsum(f) / sr)
        i1 = min(n, i0 + L)
        out[i0:i1] += pop[: i1 - i0]
    # dissolvenza finale breve per il loop
    fade = int(0.25 * sr)
    out[-fade:] *= np.linspace(1, 0, fade)
    out = out / max(1e-9, np.max(np.abs(out))) * 0.8
    pcm = (out * 32767).astype(np.int16)
    stereo = np.column_stack([pcm, pcm]).ravel()
    with wave.open(path, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(stereo.tobytes())


def main():
    svg_path, pal_path, out_path = sys.argv[1:4]
    pal0 = json.load(open(pal_path, encoding="utf-8"))["palettes"][0]
    imgs = render_palettes(svg_path, pal_path)
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        wav = os.path.join(tmp, "a.wav")
        synth_audio(wav)
        cmd = [
            "ffmpeg", "-y", "-loglevel", "error",
            "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % (W, H), "-r", str(FPS), "-i", "-",
            "-i", wav,
            "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p", "-r", str(FPS),
            "-b:v", "3800k", "-maxrate", "4800k", "-bufsize", "9600k",
            "-g", str(FPS), "-keyint_min", str(FPS), "-sc_threshold", "0", "-flags", "+cgop",
            "-c:a", "aac", "-b:a", "128k", "-ar", "48000", "-ac", "2",
            "-shortest", "-movflags", "+faststart", out_path,
        ]
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        total = int(DUR * FPS)
        for i in range(total):
            p.stdin.write(frame_at(i / FPS, imgs, pal0["BG"]).tobytes())
        p.stdin.close()
        if p.wait() != 0:
            sys.exit("ffmpeg non è riuscito a creare il video")
    size = os.path.getsize(out_path)
    if size > 50 * 1024 * 1024:
        sys.exit("%s troppo grande (%d byte)" % (out_path, size))
    print(out_path, "%.1fs" % DUR, size, "cover_ms=%d" % COVER_MS)


if __name__ == "__main__":
    main()
