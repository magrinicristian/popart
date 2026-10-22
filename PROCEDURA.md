# Procedura quotidiana — pop art su Instagram @magrinicristian

Ogni giorno alle 18:30 circa (Europe/Rome) Claude inventa una nuova pop art, la rende in 3 visioni e la pubblica su Instagram tramite Make in due formati: un **Reel animato** (per raggiungere chi non segue il profilo) e il **carosello** delle 3 visioni.

## Rubriche settimanali (dal 2026-10-23)
Il giorno della settimana (Europe/Rome) decide tema e stile:

| Giorno | Rubrica | Stile |
| --- | --- | --- |
| Lunedì | Italia a pois — oggetti, cibi e simboli della vita italiana | Pois |
| Martedì | Animali | Pop art classica |
| Mercoledì | Stagione e ricorrenze | Pois |
| Giovedì | In cucina — cibi e piatti | Pop art classica |
| Venerdì | Oggetti quotidiani e vintage | Pois |
| Sabato | In viaggio — veicoli, paesaggi, luoghi immaginari | Pop art classica |
| Domenica | Piante, fiori e natura | Pois |

Ricorrenze: se oggi o domani cade una ricorrenza (es. Halloween 31/10, San Martino 11/11, Immacolata 8/12, Natale 24–26/12, Capodanno, Befana 6/1, San Valentino 14/2, Carnevale, Pasqua, 1 maggio, Ferragosto 15/8), il tema diventa la ricorrenza, mantenendo lo stile del giorno. Soggetti generici e inventati, mai marchi o personaggi.

## Regole dell'immagine
- Originale, disegnata da Claude come SVG **1080×1350 verticale 4:5** (`width="1080" height="1350" viewBox="0 0 1080 1350"`), nessuna foto, nessun asset esterno.
- Soggetto centrato: la griglia del profilo ritaglia in 3:4 e taglia ~35 px per lato; lì solo sfondo o pattern. Il Reel mostra l'opera intera al centro di una tela 9:16.
- **Nessun testo**: niente `<text>`, lettere, numeri, loghi, balloon con parole, marchi o personaggi protetti, persone reali.
- Contorni neri spessi sempre.
- **Stile "pois"** (ispirato a Yayoi Kusama): pois ossessivi e ripetuti su soggetto e sfondo, reti infinite di archi o anelli, pattern che continuano oltre i bordi, punti di diametro variabile, poche tinte sature in forte contrasto, forme che si moltiplicano. Solo lo stile: niente zucche a pois, stanze a specchi o altre opere riconoscibili; il nome dell'artista non compare mai.
- **Stile "pop art classica"**: colori piatti saturi, retino Ben-Day, raggi pop, ombra piena fuori registro, stelle e scintille, tratteggio obliquo nelle ombre, gocce a contorno spesso. Nessuna copia di opere esistenti (niente Campbell's, Marilyn, pannelli di Lichtenstein).
- Soggetto e tecnica diversi da tutti quelli già in `art/*.json`.
- Colori solo tramite i segnaposto `{{BG}} {{DOT}} {{C1}} {{C2}} {{C3}} {{INK}}` (bianco `#FFFFFF` ammesso).

## Le tre visioni
Le 3 palette in `art/AAAA-MM-GG.json` danno tre atmosfere nettamente diverse della stessa scena (es. giorno / notte neon / tramonto). Nel Reel diventano le tre scene unite dalle transizioni a pois: la prima palette deve essere la più luminosa e leggibile, perché fa da copertina.

## Didascalia
Campo `caption` nel JSON, in italiano: 3–5 frasi evocative che descrivono la scena, una riga vuota, una frase che nomina le tre visioni, una riga vuota e **3–5 hashtag** in minuscolo senza accenti: sempre `#popart #popartitaliana #illustrazione`, più 1–2 legati al soggetto o alla rubrica (es. `#carciofo #halloween`). Mai nomi di artisti o marchi. Max 2200 caratteri. La stessa didascalia va sul Reel e sul carosello.

## Passi
1. `pip install --break-system-packages -q -r requirements.txt` (serve anche `ffmpeg`).
2. `D=AAAA-MM-GG` (Europe/Rome). Se `art/$D.json` ha `published` con sia `reel_execution` sia `make_execution`, fermarsi.
3. Scrivere `art/$D.svg` e `art/$D.json` (`subject`, `technique`, `rubric`, `style`, `palettes` ×3, `caption`).
4. `python3 tools/render.py art/$D.svg art/$D.json images/$D` → 3 JPEG 1080×1350.
5. `python3 tools/reel.py art/$D.svg art/$D.json reels/$D.mp4` → MP4 1080×1920, 11 s, audio originale.
6. Controllare le 3 immagini e 3–4 fotogrammi del Reel: nessun testo, soggetto leggibile, visioni diverse.
7. Commit e push su `main`; `SHA=$(git rev-parse HEAD)`.
8. URL: immagini `https://raw.githubusercontent.com/magrinicristian/popart/main/images/$D/{1,2,3}.jpg`; Reel `https://cdn.jsdelivr.net/gh/magrinicristian/popart@$SHA/reels/$D.mp4` (jsDelivr serve `video/mp4`; il raw di GitHub risponde `application/octet-stream`).
9. Reel: scenario Make **6733394** con `{"video_url": <URL Reel>, "caption": <caption>}`, `responsive: true`.
10. Carosello: scenario Make **6457518** con `{"date": D, "caption": <caption>}`, `responsive: true`.
11. Aggiungere al JSON `published: {at, reel_execution, make_execution}` e fare commit e push. Se un passo fallisce, leggere il dettaglio dell'esecuzione; riprovare una sola volta e solo se il post non è stato creato.
