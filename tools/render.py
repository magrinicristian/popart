#!/usr/bin/env python3
"""Rende una pop art SVG in 3 varianti di colore JPEG per un carosello Instagram.

Uso: python3 tools/render.py art/AAAA-MM-GG.svg art/AAAA-MM-GG.json images/AAAA-MM-GG
- l'SVG usa segnaposto {{BG}}, {{DOT}}, {{C1}}, {{C2}}, {{C3}}, {{INK}}
- il JSON contiene {"palettes": [ {BG,DOT,C1,C2,C3,INK}, x3 ]}
- formato preso da width/height dell'SVG: dal 2026-10-01 è 1080x1350 (4:5 verticale);
  le pop art precedenti restano 1080x1080
Scrive 1.jpg, 2.jpg, 3.jpg (JPEG < 8 MB) nella cartella di output.
"""
import io, json, os, re, sys
import cairosvg
from PIL import Image

svg_path, pal_path, out_dir = sys.argv[1:4]
tpl = open(svg_path, encoding="utf-8").read()
palettes = json.load(open(pal_path, encoding="utf-8"))["palettes"]
if len(palettes) != 3:
    sys.exit("servono esattamente 3 palette")

root = re.search(r"<svg\b[^>]*>", tpl).group(0)
w = int(float(re.search(r'\bwidth="([\d.]+)', root).group(1)))
h = int(float(re.search(r'\bheight="([\d.]+)', root).group(1)))
if not 0.8 <= w / h <= 1.91:
    sys.exit("proporzioni %dx%d fuori dal range Instagram 4:5 – 1.91:1" % (w, h))
if w != 1080:
    sys.exit("la larghezza deve essere 1080 px")

os.makedirs(out_dir, exist_ok=True)
for i, pal in enumerate(palettes, 1):
    svg = tpl
    for k, v in pal.items():
        svg = svg.replace("{{%s}}" % k, v)
    if "{{" in svg:
        sys.exit("segnaposto non sostituito nella palette %d" % i)
    png = cairosvg.svg2png(bytestring=svg.encode(), output_width=w, output_height=h)
    img = Image.open(io.BytesIO(png)).convert("RGB")
    path = os.path.join(out_dir, "%d.jpg" % i)
    img.save(path, "JPEG", quality=92, optimize=True)
    size = os.path.getsize(path)
    if size > 8 * 1024 * 1024:
        sys.exit("%s supera 8 MB" % path)
    print(path, img.size, size)
