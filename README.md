# Pop art quotidiana

Ogni giorno una nuova pop art originale, senza testi, in tre varianti di colore per un carosello Instagram.

- `art/AAAA-MM-GG.svg` — sorgente con segnaposto di colore `{{BG}} {{DOT}} {{C1}} {{C2}} {{C3}} {{INK}}`
- `art/AAAA-MM-GG.json` — soggetto, tecnica e le 3 palette
- `images/AAAA-MM-GG/1.jpg … 3.jpg` — JPEG 1080×1080 pubblicati
- `tools/render.py` — `python3 tools/render.py art/X.svg art/X.json images/X`
