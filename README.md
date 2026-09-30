# Pop art quotidiana

Ogni giorno una nuova pop art originale, senza testi, in tre varianti di colore per un carosello Instagram.

- `art/AAAA-MM-GG.svg` — sorgente con segnaposto di colore `{{BG}} {{DOT}} {{C1}} {{C2}} {{C3}} {{INK}}`
- `art/AAAA-MM-GG.json` — soggetto, tecnica e le 3 palette
- `images/AAAA-MM-GG/1.jpg … 3.jpg` — JPEG pubblicati: 1080×1350 (4:5) dal 2026-10-01, 1080×1080 prima
- `tools/render.py` — `python3 tools/render.py art/X.svg art/X.json images/X`
- `PROCEDURA.md` — come viene creato e pubblicato il post di ogni giorno
- Pubblicazione: scenario Make "Pop art quotidiana → Instagram @magrinicristian" (carosello da `images/AAAA-MM-GG/`, input `date` e `caption`)
