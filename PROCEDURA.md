# Procedura quotidiana — pop art su Instagram @magrinicristian

Ogni giorno Claude inventa una nuova pop art, la rende in 3 varianti e la pubblica come carosello su Instagram tramite Make.

## Regole dell'immagine
- Originale, disegnata da Claude come SVG **1080×1350 verticale 4:5** (`width="1080" height="1350" viewBox="0 0 1080 1350"`), nessuna foto, nessun asset esterno. È il formato più grande che Instagram accetta via API (il 3:4 viene rifiutato).
- Soggetto centrato: la griglia del profilo ritaglia in 3:4, quindi le fasce alte e basse (~45 px ciascuna) devono contenere solo sfondo, retino o raggi.
- **Nessun testo**: niente `<text>`, lettere, numeri, loghi, balloon con parole, marchi o personaggi protetti.
- Stile pop art: contorni neri spessi, colori piatti saturi, retino Ben-Day, raggi, stelle, gocce.
- Soggetto diverso da tutti quelli già in `art/*.json` (campo `subject`).
- Colori solo tramite i segnaposto `{{BG}} {{DOT}} {{C1}} {{C2}} {{C3}} {{INK}}` (bianco `#FFFFFF` ammesso per i riflessi).

## Le tre visioni
Le 3 palette in `art/AAAA-MM-GG.json` devono dare tre atmosfere nettamente diverse della stessa scena (es. giorno / notte neon / tramonto), non semplici ritocchi.

## Didascalia
Campo `caption` nel JSON, in italiano: la rappresentazione immaginata, 3–5 frasi evocative che descrivono la scena, poi una riga vuota e una frase che nomina le tre visioni. Niente hashtag salvo richiesta. Max 2200 caratteri.

## Passi
1. `pip install --break-system-packages -q -r requirements.txt`
2. Data di oggi (Europe/Rome) → `D=AAAA-MM-GG`. Se `art/$D.json` ha già `published`, fermarsi: oggi è già pubblicato.
3. Scrivere `art/$D.svg` e `art/$D.json` (`subject`, `technique`, `palettes` ×3, `caption`).
4. `python3 tools/render.py art/$D.svg art/$D.json images/$D`
5. Guardare le 3 immagini: nessun testo, soggetto leggibile, varianti diverse. Se no, correggere e rifare il passo 4.
6. Commit e push su `main`.
7. Verificare che `https://raw.githubusercontent.com/magrinicristian/popart/main/images/$D/{1,2,3}.jpg` rispondano 200 `image/jpeg` (attendere e riprovare se il push è appena avvenuto).
8. Lanciare lo scenario Make **6457518** (team 3071710) con `{"date": D, "caption": <caption>}`, `responsive: true`.
9. Se riesce, aggiungere al JSON `published: {at, make_execution}` e fare commit e push. Se fallisce, leggere il dettaglio dell'esecuzione e riportare l'errore; non ripubblicare due volte.
