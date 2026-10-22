# Pop art quotidiana

Ogni giorno una nuova pop art originale, senza testi, in tre visioni di colore: un Reel animato e un carosello Instagram su @magrinicristian.

- `art/AAAA-MM-GG.svg` — sorgente con segnaposto di colore `{{BG}} {{DOT}} {{C1}} {{C2}} {{C3}} {{INK}}`
- `art/AAAA-MM-GG.json` — soggetto, tecnica, rubrica, stile, le 3 palette e la didascalia
- `images/AAAA-MM-GG/1.jpg … 3.jpg` — JPEG del carosello: 1080×1350 (4:5) dal 2026-10-01, 1080×1080 prima
- `reels/AAAA-MM-GG.mp4` — Reel 1080×1920, 11 s, dal 2026-10-23
- `tools/render.py` — `python3 tools/render.py art/X.svg art/X.json images/X`
- `tools/reel.py` — `python3 tools/reel.py art/X.svg art/X.json reels/X.mp4`
- `PROCEDURA.md` — rubriche, stili e passi di ogni giorno
- Pubblicazione: scenari Make "Pop art quotidiana Reel → Instagram @magrinicristian" (6733394, input `video_url`, `caption`) e "Pop art quotidiana → Instagram @magrinicristian" (6457518, input `date`, `caption`)
