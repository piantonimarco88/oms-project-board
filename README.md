# OMS Project Board

Strumento di project management per la valutazione di un nuovo Order Management System (OMS) a supporto della strategia omnichannel.

## Contenuto

- **`OMS_Project_Board.html`** — app interattiva: Stakeholder, Sistemi & Pain Point, KPI, Roadmap, Gantt, Registro Rischi, Matrice RACI, Business Case, Vendor/Opzioni, Log Decisioni. Aggiungere/rimuovere uno Stakeholder aggiorna automaticamente l'elenco nomi selezionabile in tutti i menu owner (KPI, Roadmap, Rischi, RACI).
- **`oms_project_data.json`** — dati "pubblicati": è il file che l'app carica automaticamente quando viene aperta dal link GitHub Pages (vedi sotto). Va tenuto aggiornato manualmente quando si vuole condividere un nuovo stato.
- **`oms_project_backup_*.json`** — export puntuali con data (bottone "💾 Salva Dati" nell'app), utili come cronologia/backup personale.
- **`generate_project_pdf.py`** — genera `OMS_Project_Summary.pdf` a partire dall'ultimo backup JSON presente nella cartella (richiede `reportlab`: `pip install reportlab`).
- **`OMS_Project_Summary.pdf`** — riepilogo stampabile generato dallo script.

## Come usarlo

**Link diretto (consigliato per i colleghi):** https://piantonimarco88.github.io/oms-project-board/
Chi apre questo link vede automaticamente lo stato pubblicato in `oms_project_data.json` — **nessun passaggio manuale richiesto**. Se ha già aperto l'app in precedenza dallo stesso browser, restano invece le sue modifiche locali (localStorage ha sempre priorità, così non si perde lavoro in corso).

**Se apri il file in locale** (doppio click su `OMS_Project_Board.html`): i dati che modifichi si salvano nel tuo browser (localStorage) e restano locali al tuo dispositivo — non si sincronizzano da soli con GitHub.

**Per pubblicare un aggiornamento visibile a tutti sul link GitHub Pages:**
1. Nell'app, clicca **"💾 Salva Dati (backup)"** → scarica un nuovo `oms_project_backup_<data>.json`.
2. Sostituisci il contenuto di `oms_project_data.json` con quello del nuovo export (stesso nome file, stesso posto).
3. Fai commit/push. Dopo qualche minuto (tempo di build di GitHub Pages) chiunque apra il link vede lo stato aggiornato, senza dover importare nulla manualmente.

**Per rigenerare il PDF** dopo un aggiornamento dati: `python generate_project_pdf.py` (usa automaticamente il backup JSON più recente nella cartella).

## Nota

Questo repository contiene nomi e ruoli di persone reali coinvolte nel progetto. Verifica che il livello di visibilità del repository sia coerente con le policy aziendali sulla riservatezza.
