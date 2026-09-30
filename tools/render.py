#!/usr/bin/env python3
"""Rende una pop art SVG in 3 varianti di colore JPEG 1080x1080 per un carosello Instagram.

Uso: python3 tools/render.py art/AAAA-MM-GG.svg art/AAAA-MM-GG.json images/AAAA-MM-GG
- l'SVG usa segnaposto {{BG}}, {{DOT}}, {{C1}}, {{C2}}, {{C3}}, {{INK}}
- il JSON contiene {"palettes": [ {BG,DOT,C1,C2,C3,INK}, x3 ]}
Scrive 1.jpg, 2.jpg, 3.jpg (JPEG, < 8 MB, 1080x1080) nella cartella di output.
"""
import io, json, os, sys
import cairosvg
from PIL import Image

svg_path, pal_path, out_dir = sys.argv[1:4]
tpl = open(svg_path, encoding="utf-8").read()
palettes = json.load(open(pal_path, encoding="utf-8"))["palettes"]
if len(palettes) != 3:
    sys.exit("servono esattamente 3 palette")
os.makedirs(out_dir, exist_ok=True)
for i, pal in enumerate(palettes, 1):
    svg = tpl
    for k, v in pal.items():
        svg = svg.replace("{{%s}}" % k, v)
    if "{{" in svg:
        sys.exit("segnaposto non sostituito nella palette %d" % i)
    png = cairosvg.svg2png(bytestring=svg.encode(), output_width=1080, output_height=1080)
    img = Image.open(io.BytesIO(png)).convert("RGB")
    path = os.path.join(out_dir, "%d.jpg" % i)
    img.save(path, "JPEG", quality=92, optimize=True)
    print(path, img.size, os.path.getsize(path))
