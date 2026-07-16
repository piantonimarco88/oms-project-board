# OMS Project Board

Strumento di project management per la valutazione di un nuovo Order Management System (OMS) a supporto della strategia omnichannel.

## Contenuto

- **`OMS_Project_Board.html`** — app locale interattiva (nessun server richiesto): Stakeholder, Sistemi & Pain Point, KPI, Roadmap, Gantt, Registro Rischi, Matrice RACI, Business Case, Vendor/Opzioni, Log Decisioni. Apri il file con un doppio click nel browser.
- **`generate_project_pdf.py`** — genera `OMS_Project_Summary.pdf` a partire dall'ultimo backup JSON esportato dall'app (richiede `reportlab`: `pip install reportlab`).
- **`oms_project_backup_*.json`** — ultimo export dei dati (bottone "💾 Salva Dati" nell'app). È la fonte dati per il PDF.
- **`OMS_Project_Summary.pdf`** — riepilogo stampabile generato dallo script.

## Come usarlo

1. Apri `OMS_Project_Board.html` nel browser. I dati che modifichi si salvano automaticamente nel tuo browser (localStorage) — **restano locali al tuo dispositivo**, non si sincronizzano automaticamente con GitHub.
2. Per allineare il tuo stato a quello più recente condiviso qui: apri l'app, clicca **"📂 Carica Dati Salvati"** e seleziona il file `oms_project_backup_*.json` più recente presente in questo repository.
3. Per condividere un aggiornamento con gli altri: nell'app clicca **"💾 Salva Dati (backup)"**, poi fai il commit/push del nuovo file JSON generato (sostituendo o affiancando quello precedente).
4. Per rigenerare il PDF dopo un aggiornamento dati: `python generate_project_pdf.py` (usa automaticamente il backup JSON più recente nella cartella).

## Nota

Questo repository contiene nomi e ruoli di persone reali coinvolte nel progetto. Verifica che il livello di visibilità del repository sia coerente con le policy aziendali sulla riservatezza.
