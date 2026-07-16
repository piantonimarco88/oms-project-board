# -*- coding: utf-8 -*-
"""
Genera OMS_Project_Summary.pdf.

Fonte dati: l'ultimo file "oms_project_backup_*.json" esportato dalla Project Board
HTML (bottone "Salva Dati") presente in questa cartella. Se non ne trova nessuno,
usa i dati di default qui sotto (allineati ai default della Board HTML) come fallback,
cosi' lo script funziona anche prima del primo export.

Per aggiornare il PDF ad ogni novita':
    1. Nella Project Board HTML, clicca "Salva Dati (backup)" per esportare l'ultimo JSON.
    2. Rilancia: python generate_project_pdf.py
    (Lo script prende automaticamente il backup piu' recente in questa cartella.)
"""

import glob
import json
import os

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
)

NAVY = colors.HexColor("#18376a")
NAVY_DARK = colors.HexColor("#0f2547")
GRAY_BG = colors.HexColor("#eef1f6")
LIGHT_BORDER = colors.HexColor("#dfe4ec")

LAST_UPDATE = "15/07/2026"
NEXT_MEETING = "WK31 (27/07-02/08/2026)"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# ---- Mappe etichette (allineate a quelle della Project Board HTML) ----
LEVEL_LABELS = {"alta": "Alta", "media": "Media", "bassa": "Bassa"}
STATUS_LABELS = {"da-avviare": "Da avviare", "in-corso": "In corso", "completato": "Completato"}
RISK_CATEGORY_LABELS = {"tecnico": "Tecnico", "organizzativo": "Organizzativo", "dati": "Dati", "fornitore": "Fornitore"}
RISK_STATUS_LABELS = {"aperto": "Aperto", "mitigato": "Mitigato", "chiuso": "Chiuso"}
VENDOR_STATUS_LABELS = {"da-valutare": "Da valutare", "in-valutazione": "In valutazione", "shortlist": "Shortlist", "scartato": "Scartato"}
BC_CATEGORY_LABELS = {"capex": "CAPEX", "opex": "OPEX", "kpi": "KPI"}

# ---- Default (fallback se non esiste ancora nessun backup JSON esportato) ----
DEFAULT_STAKEHOLDERS = [
    {"nome": "Luigi Barra", "ruolo": "Chief Supply Chain Officer", "coinvolgimento": "Convocatore kick-off / Sponsor de facto"},
    {"nome": "Marco Piantoni", "ruolo": "Project Leader (in conferma)", "coinvolgimento": "Leadership analisi KPI - conferma attesa entro WK30, previo accordo con Paolo Zanco"},
    {"nome": "Eugenio Frescura", "ruolo": "Proponente KPI", "coinvolgimento": "Ha definito la proposta di KPI minimi da monitorare"},
    {"nome": "Paolo Zanco", "ruolo": "Stakeholder", "coinvolgimento": "Validazione assegnazione leadership"},
    {"nome": "Marco Benasedo", "ruolo": "Stakeholder", "coinvolgimento": "Partecipante kick-off"},
    {"nome": "Claudia Sogus", "ruolo": "Business Input", "coinvolgimento": "Intervista dedicata per spunti di business aggiuntivo (WK31)"},
    {"nome": "Raul Simon", "ruolo": "Da chiarire", "coinvolgimento": "Owner KPI (pool assegnazione)"},
    {"nome": "Alberto Sala", "ruolo": "Da chiarire", "coinvolgimento": "Owner KPI (pool assegnazione)"},
    {"nome": "Maja Sztekiel", "ruolo": "Da chiarire", "coinvolgimento": "Owner KPI (pool assegnazione)"},
]

DEFAULT_SISTEMI = [
    {"sistema": "OMS attuale", "ruolo": "Orchestrazione ordini omnichannel - oggetto della valutazione di sostituzione/upgrade"},
    {"sistema": ".com / Marketplace (MKT)", "ruolo": "Canali di vendita online da sincronizzare con lo stock"},
    {"sistema": "WMS", "ruolo": "Gestione magazzino - stock fisico teorico"},
    {"sistema": "Sistema negozi (\"XY\" / \"St3k\")", "ruolo": "Stock fisico negozio - nome sistema da confermare"},
]

DEFAULT_KPIS = [
    {"area": "Giacenze", "kpi": "Overselling Rate", "formula": "N. ordini annullati/rimborsati per mancanza stock nel giorno / Tot. ordini acquisiti nel giorno", "fonte": "OMS", "baseline": "", "target": "", "owners": [], "deadline": "WK31"},
    {"area": "Giacenze", "kpi": "Inventory Sync Time", "formula": "Tempo (media + p95) tra vendita/reso e aggiornamento stock pubblicato su .com/MKT", "fonte": "OMS log", "baseline": "", "target": "", "owners": [], "deadline": "WK31"},
    {"area": "Giacenze", "kpi": "Disallineamento Inventariale", "formula": "N. SKU con discrepanza fisico-teorica nel giorno / Tot. SKU verificati nel giorno", "fonte": "Conteggi negozio + WMS", "baseline": "", "target": "", "owners": [], "deadline": "WK31"},
    {"area": "Routing", "kpi": "Split Order Rate", "formula": "N. ordini splittati in due o piu spedizioni nel giorno / Tot. ordini gestiti nel giorno", "fonte": "OMS", "baseline": "", "target": "", "owners": [], "deadline": "WK31"},
    {"area": "Routing", "kpi": "Store Rejection Rate", "formula": "N. rifiuti da personale negozio nel giorno / Tot. ordini indirizzati a negozio", "fonte": "OMS + store ops", "baseline": "", "target": "", "owners": [], "deadline": "WK31"},
    {"area": "Routing", "kpi": "Routing Time", "formula": "Tempo (media + p95) per applicare le regole di business e determinare il nodo logistico ottimale", "fonte": "OMS", "baseline": "", "target": "", "owners": [], "deadline": "WK31"},
    {"area": "Logistica", "kpi": "Order Lead Time", "formula": "Tempo (media + dev.std.) da conferma ordine sul sito a drop verso WMS/negozio", "fonte": "OMS/WMS", "baseline": "", "target": "", "owners": [], "deadline": "WK31"},
    {"area": "Logistica", "kpi": "Order Touch Rate", "formula": "N. ordini bloccati/modificati manualmente nel giorno / Tot. ordini gestiti dall'OMS", "fonte": "OMS", "baseline": "", "target": "", "owners": [], "deadline": "WK31"},
    {"area": "Cliente", "kpi": "OTIF", "formula": "N. ordini consegnati integri entro data promessa / Tot. ordini con consegna prevista nel giorno", "fonte": "OMS/WMS", "baseline": "", "target": "", "owners": [], "deadline": "WK31"},
    {"area": "Economico", "kpi": "Costo per Ordine Gestito", "formula": "(Costi OMS + costi operativi gestione ordine) / Tot. ordini gestiti", "fonte": "Finance/IT", "baseline": "", "target": "", "owners": [], "deadline": "Dopo business case"},
]

DEFAULT_ROADMAP = [
    {"task": "Conferma incarico leadership", "owners": ["Marco Piantoni"], "dependsOn": [], "priority": "alta", "start": "2026-07-15", "end": "2026-07-26", "status": "in-corso"},
    {"task": "Assegnazione owner KPI (pool 7 nominativi)", "owners": ["Marco Piantoni"], "dependsOn": [], "priority": "alta", "start": "2026-07-15", "end": "2026-07-26", "status": "in-corso"},
    {"task": "Raccolta e consolidamento dati KPI", "owners": [], "dependsOn": ["Assegnazione owner KPI (pool 7 nominativi)"], "priority": "alta", "start": "2026-07-20", "end": "2026-12-31", "status": "da-avviare"},
    {"task": "Intervista Claudia Sogus (business input)", "owners": ["Marco Piantoni", "Claudia Sogus"], "dependsOn": [], "priority": "media", "start": "2026-07-27", "end": "2026-08-02", "status": "da-avviare"},
    {"task": "Verifica completezza dati raccolti (riunione)", "owners": [], "dependsOn": ["Raccolta e consolidamento dati KPI"], "priority": "alta", "start": "2026-07-27", "end": "2026-08-02", "status": "da-avviare"},
    {"task": "Prima analisi dati raccolti", "owners": [], "dependsOn": ["Verifica completezza dati raccolti (riunione)"], "priority": "alta", "start": "2026-09-14", "end": "2026-09-20", "status": "da-avviare"},
]

DEFAULT_RISKS = [
    {"rischio": "Sistema negozi non identificato con certezza (\"XY\" / \"St3k\")", "categoria": "dati", "impatto": "media", "probabilita": "alta", "mitigazione": "Confermare nome e owner del sistema entro WK31", "owners": [], "stato": "aperto"},
    {"rischio": "Ritardo nella conferma della leadership di progetto", "categoria": "organizzativo", "impatto": "media", "probabilita": "media", "mitigazione": "Sollecitare accordo Piantoni/Zanco entro WK30", "owners": ["Marco Piantoni", "Paolo Zanco"], "stato": "aperto"},
    {"rischio": "Dati storici KPI non disponibili o incompleti", "categoria": "dati", "impatto": "alta", "probabilita": "media", "mitigazione": "Setup dedicato di raccolta per i KPI privi di storico affidabile", "owners": [], "stato": "aperto"},
]

DEFAULT_RACI = [
    {"decisione": "Conferma incarico leadership progetto", "responsible": ["Marco Piantoni"], "accountable": ["Paolo Zanco"], "consulted": ["Luigi Barra"], "informed": ["Marco Benasedo", "Claudia Sogus"]},
    {"decisione": "Approvazione budget OMS", "responsible": [], "accountable": ["Luigi Barra"], "consulted": ["Marco Piantoni"], "informed": []},
    {"decisione": "Scelta vendor/soluzione OMS", "responsible": ["Marco Piantoni"], "accountable": ["Luigi Barra"], "consulted": ["Eugenio Frescura", "Paolo Zanco"], "informed": ["Marco Benasedo", "Claudia Sogus"]},
]

DEFAULT_BUSINESS = [
    {"voce": "Implementazione / System Integration", "categoria": "capex", "asis": "-", "tobe": "Da benchmark mercato"},
    {"voce": "Licenza software OMS (annua)", "categoria": "opex", "asis": "Dato mancante", "tobe": "Da benchmark mercato"},
    {"voce": "Manutenzione e supporto (annuo)", "categoria": "opex", "asis": "Dato mancante", "tobe": "Da benchmark mercato"},
    {"voce": "Volume ordini/giorno", "categoria": "kpi", "asis": "Dato mancante", "tobe": "-"},
    {"voce": "Costo per Ordine Gestito", "categoria": "kpi", "asis": "Dato mancante", "tobe": "Da stimare post KPI"},
    {"voce": "Overselling Rate", "categoria": "kpi", "asis": "In raccolta (WK31->)", "tobe": "Target da definire"},
    {"voce": "OTIF", "categoria": "kpi", "asis": "In raccolta (WK31->)", "tobe": "Target da definire"},
]

DEFAULT_VENDORS = [
    {"vendor": "Da definire", "fit": "media", "integrazione": "media", "costo": "Da definire", "note": "Sezione da popolare dopo lo studio di fattibilita'", "stato": "da-valutare"},
]

LOG = [
    ("15/07/2026",
     "Ristrutturata la Project Board: aggiunte le sezioni Registro Rischi, Matrice RACI e Vendor/Opzioni OMS; "
     "aggiunte colonne Baseline/Target ai KPI e Dipendenze al Roadmap; Stakeholder e Sistemi resi editabili come "
     "le altre sezioni; Business Case riorganizzato in ottica CAPEX/OPEX/KPI."),
    ("15/07/2026",
     "Definito il pool di 9 risorse assegnabili come owner (KPI, Roadmap, Rischi, RACI): Paolo Zanco, Luigi Barra, "
     "Marco Benasedo, Raul Simon, Alberto Sala, Claudia Sogus, Maja Sztekiel, Eugenio Frescura, Marco Piantoni."),
    ("14/07/2026",
     "Kick-off OMS: avviata analisi KPI proposti da Eugenio Frescura. Leadership assegnata (in attesa di conferma) "
     "a Marco Piantoni, previo accordo con Paolo Zanco. Coinvolgimento di Claudia Sogus per input di business aggiuntivo."),
]


def find_latest_backup():
    pattern = os.path.join(SCRIPT_DIR, "oms_project_backup_*.json")
    candidates = glob.glob(pattern)
    if not candidates:
        return None
    return max(candidates, key=os.path.getmtime)


def load_project_data():
    backup_path = find_latest_backup()
    data = {
        "stakeholders": DEFAULT_STAKEHOLDERS,
        "sistemi": DEFAULT_SISTEMI,
        "kpis": DEFAULT_KPIS,
        "roadmap": DEFAULT_ROADMAP,
        "risks": DEFAULT_RISKS,
        "raci": DEFAULT_RACI,
        "business": DEFAULT_BUSINESS,
        "vendor": DEFAULT_VENDORS,
    }
    if backup_path:
        try:
            with open(backup_path, encoding="utf-8") as f:
                backup = json.load(f)
            for key in data:
                if isinstance(backup.get(key), list) and backup[key]:
                    data[key] = backup[key]
            print(f"Dati caricati dal backup: {os.path.basename(backup_path)}")
        except Exception as e:
            print(f"Impossibile leggere il backup ({e}), uso i dati di default.")
    else:
        print("Nessun backup trovato, uso i dati di default.")
    return data


def owners_join(values):
    return ", ".join(values) if values else "Da assegnare"


def make_table(data, col_widths, header_bg=NAVY, font_size=8.5):
    style = getSampleStyleSheet()
    cell_style = ParagraphStyle("cell", parent=style["Normal"], fontSize=font_size, leading=font_size + 3)
    header_style = ParagraphStyle("header", parent=style["Normal"], fontSize=font_size,
                                   leading=font_size + 3, textColor=colors.white, fontName="Helvetica-Bold")

    wrapped = []
    for r, row in enumerate(data):
        wrapped_row = []
        for cell in row:
            s = header_style if r == 0 else cell_style
            wrapped_row.append(Paragraph(str(cell), s))
        wrapped.append(wrapped_row)

    t = Table(wrapped, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), header_bg),
        ("GRID", (0, 0), (-1, -1), 0.5, LIGHT_BORDER),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, GRAY_BG]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def build_pdf(output_path="OMS_Project_Summary.pdf"):
    data = load_project_data()

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleCustom", parent=styles["Title"], textColor=NAVY_DARK, fontSize=20, spaceAfter=4)
    subtitle_style = ParagraphStyle("Subtitle", parent=styles["Normal"], textColor=colors.HexColor("#5b6479"), fontSize=11, spaceAfter=14)
    meta_style = ParagraphStyle("Meta", parent=styles["Normal"], textColor=colors.HexColor("#5b6479"), fontSize=9, spaceAfter=18)
    h2_style = ParagraphStyle("H2", parent=styles["Heading2"], textColor=NAVY, spaceBefore=16, spaceAfter=8, fontSize=13)
    note_style = ParagraphStyle("Note", parent=styles["Normal"], fontSize=8.5,
                                 textColor=colors.HexColor("#5b6479"), spaceBefore=6)
    log_date_style = ParagraphStyle("LogDate", parent=styles["Normal"], fontSize=9.5,
                                     textColor=NAVY, fontName="Helvetica-Bold")
    log_text_style = ParagraphStyle("LogText", parent=styles["Normal"], fontSize=9.5, spaceAfter=10, leading=13)

    doc = SimpleDocTemplate(output_path, pagesize=A4,
                             topMargin=1.8 * cm, bottomMargin=1.8 * cm,
                             leftMargin=1.6 * cm, rightMargin=1.6 * cm)

    story = []
    story.append(Paragraph("OMS - Valutazione Nuovo Order Management System", title_style))
    story.append(Paragraph("Allineamento OMS e analisi KPI - Strategia Omnichannel", subtitle_style))
    story.append(Paragraph(f"Ultimo aggiornamento: <b>{LAST_UPDATE}</b> &nbsp;|&nbsp; Prossimo meeting: <b>{NEXT_MEETING}</b>", meta_style))

    # --- Stakeholder ---
    story.append(Paragraph("Stakeholder", h2_style))
    rows = [["Nome", "Ruolo", "Coinvolgimento nel progetto"]]
    rows += [[s["nome"], s["ruolo"], s["coinvolgimento"]] for s in data["stakeholders"]]
    story.append(make_table(rows, [3.5 * cm, 4.5 * cm, 8.7 * cm]))

    # --- Sistemi ---
    story.append(Paragraph("Sistemi Attuali &amp; Pain Point", h2_style))
    rows = [["Sistema", "Ruolo nel flusso"]]
    rows += [[s["sistema"], s["ruolo"]] for s in data["sistemi"]]
    story.append(make_table(rows, [5.5 * cm, 11.2 * cm]))
    story.append(Paragraph(
        "Pain point identificati (fonte: proposta KPI di Eugenio Frescura, mail 13/07/2026): overselling, "
        "latenza sync inventario, disallineamento stock teorico/fisico, split order, rifiuti store, routing time "
        "elevato, lead time lungo, alto tasso di interventi manuali, OTIF sotto target.", note_style))

    story.append(PageBreak())

    # --- KPI ---
    story.append(Paragraph("KPI &amp; Assegnazione Owner", h2_style))
    rows = [["Area", "KPI", "Formula", "Fonte", "Baseline", "Target", "Owner", "Deadline"]]
    for k in data["kpis"]:
        rows.append([k["area"], k["kpi"], k["formula"], k["fonte"], k.get("baseline") or "-",
                     k.get("target") or "-", owners_join(k.get("owners")), k["deadline"]])
    story.append(make_table(rows, [1.7 * cm, 2.2 * cm, 4.6 * cm, 1.8 * cm, 1.6 * cm, 1.6 * cm, 2.4 * cm, 1.5 * cm], font_size=7.2))

    # --- Roadmap ---
    story.append(Paragraph("Roadmap / Action Plan", h2_style))
    rows = [["Attivita", "Owner", "Dipende da", "Priorita", "Inizio", "Fine", "Stato"]]
    for r in data["roadmap"]:
        rows.append([r["task"], owners_join(r.get("owners")), owners_join(r.get("dependsOn")),
                     LEVEL_LABELS.get(r["priority"], r["priority"]), r["start"], r["end"],
                     STATUS_LABELS.get(r["status"], r["status"])])
    story.append(make_table(rows, [3.4 * cm, 2.4 * cm, 2.8 * cm, 1.6 * cm, 1.8 * cm, 1.8 * cm, 1.8 * cm], font_size=7.5))

    story.append(PageBreak())

    # --- Rischi ---
    story.append(Paragraph("Registro Rischi", h2_style))
    rows = [["Rischio", "Categoria", "Impatto", "Probabilita", "Mitigazione", "Owner", "Stato"]]
    for r in data["risks"]:
        rows.append([r["rischio"], RISK_CATEGORY_LABELS.get(r["categoria"], r["categoria"]),
                     LEVEL_LABELS.get(r["impatto"], r["impatto"]), LEVEL_LABELS.get(r["probabilita"], r["probabilita"]),
                     r["mitigazione"], owners_join(r.get("owners")), RISK_STATUS_LABELS.get(r["stato"], r["stato"])])
    story.append(make_table(rows, [3.3 * cm, 1.8 * cm, 1.5 * cm, 1.7 * cm, 3.6 * cm, 2.2 * cm, 1.5 * cm], font_size=7.2))

    # --- RACI ---
    story.append(Paragraph("Matrice RACI", h2_style))
    rows = [["Decisione / Area", "R - Responsible", "A - Accountable", "C - Consulted", "I - Informed"]]
    for r in data["raci"]:
        rows.append([r["decisione"], owners_join(r.get("responsible")), owners_join(r.get("accountable")),
                     owners_join(r.get("consulted")), owners_join(r.get("informed"))])
    story.append(make_table(rows, [4.6 * cm, 2.7 * cm, 2.7 * cm, 2.7 * cm, 2.7 * cm], font_size=7.5))

    story.append(PageBreak())

    # --- Business Case ---
    story.append(Paragraph("Business Case (As-Is / To-Be)", h2_style))
    rows = [["Voce", "Categoria", "As-Is (attuale)", "To-Be (con nuovo OMS)"]]
    for b in data["business"]:
        rows.append([b["voce"], BC_CATEGORY_LABELS.get(b["categoria"], b["categoria"]), b["asis"], b["tobe"]])
    story.append(make_table(rows, [4.8 * cm, 2.2 * cm, 4.4 * cm, 4.4 * cm]))
    story.append(Paragraph(
        "Metodologia break-even (indicativa): l'investimento iniziale (CAPEX) si considera ammortizzato quando i "
        "risparmi operativi annui - differenza OPEX As-Is/To-Be piu i benefici quantificabili dai KPI (es. riduzione "
        "overselling, minori interventi manuali) - superano l'investimento sostenuto. Nessuna stima numerica viene "
        "inserita senza dati reali confermati o senza esplicita richiesta di usare benchmark di mercato.", note_style))

    # --- Vendor ---
    story.append(Paragraph("Vendor / Opzioni OMS", h2_style))
    rows = [["Vendor / Opzione", "Fit Funzionale", "Complessita Integrazione", "Costo Stimato", "Note", "Stato"]]
    for v in data["vendor"]:
        rows.append([v["vendor"], LEVEL_LABELS.get(v["fit"], v["fit"]), LEVEL_LABELS.get(v["integrazione"], v["integrazione"]),
                     v["costo"], v["note"], VENDOR_STATUS_LABELS.get(v["stato"], v["stato"])])
    story.append(make_table(rows, [2.6 * cm, 1.9 * cm, 2.6 * cm, 2.2 * cm, 4.5 * cm, 2.0 * cm], font_size=7.5))

    story.append(PageBreak())

    # --- Log Decisioni ---
    story.append(Paragraph("Log Decisioni", h2_style))
    for date, text in LOG:
        block = [Paragraph(date, log_date_style), Paragraph(text, log_text_style)]
        story.append(KeepTogether(block))

    doc.build(story)
    print(f"PDF generato: {output_path}")


if __name__ == "__main__":
    build_pdf()
