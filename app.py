"""
Roig Fleet Manager — DATOS REALES 16 Jun 2026
Son Oms · ROIG, HASSO, AVIS y MARASON
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import io, csv
from collections import defaultdict, OrderedDict

st.set_page_config(
    page_title="Roig Fleet Manager",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────
# CSS
# ─────────────────────────────────────────
st.markdown("""
<style>
#MainMenu, footer, header { visibility: hidden; }
.rfm-header {
    background: linear-gradient(135deg, #0A4A39 0%, #0F6E56 100%);
    color: white; padding: 14px 22px; border-radius: 10px;
    margin-bottom: 16px; display: flex; align-items: center;
    justify-content: space-between;
    box-shadow: 0 4px 16px rgba(15,110,86,0.25);
}
.rfm-header h1 { font-size: 1.1rem; margin:0; font-weight:800; }
.rfm-header .sub { font-size:.72rem; opacity:.7; margin-top:2px; }
.rfm-header .clock { font-size:1.2rem; font-weight:800; font-family:monospace; }
.rfm-header .date  { font-size:.68rem; opacity:.6; text-align:right; margin-top:2px; }

/* ── SELL BOARD — main feature ── */
.sell-board {
    background: white; border: 1px solid #E5E7EB;
    border-radius: 12px; padding: 0;
    box-shadow: 0 2px 8px rgba(0,0,0,.07);
    overflow: hidden; margin-bottom: 16px;
}
.sell-board-head {
    background: #0A4A39; color: white;
    padding: 12px 18px;
    display: flex; align-items: center; justify-content: space-between;
}
.sell-board-head h2 { font-size:.95rem; font-weight:800; margin:0; }
.sell-board-head .ts { font-size:.72rem; opacity:.7; }

.sell-row {
    display: grid;
    grid-template-columns: 110px 1fr 90px 90px 90px 90px 110px;
    align-items: center;
    padding: 0;
    border-bottom: 1px solid #F1F5F9;
    transition: background .08s;
}
.sell-row:last-child { border-bottom: none; }
.sell-row:hover { background: #F8FAFC; }
.sell-row.header {
    background: #F1F5F9;
    font-size:.67rem; font-weight:700; text-transform:uppercase;
    letter-spacing:.06em; color:#64748B;
    padding: 8px 0; border-bottom: 2px solid #E2E8F0;
}
.sell-row.header:hover { background:#F1F5F9; }
.sell-col {
    padding: 10px 12px;
    font-size: .82rem;
}
.sell-col.right { text-align: right; }
.sell-col.center { text-align: center; }

/* Cat badge */
.cat-badge {
    display: inline-block; font-size:.78rem; font-weight:800;
    padding: 3px 10px; border-radius: 6px; letter-spacing:.02em;
}
.cat-A  { background:#FEF9C3; color:#713F12; border:1px solid #FDE047; }
.cat-B  { background:#FEF3C7; color:#92400E; border:1px solid #FCD34D; }
.cat-C  { background:#FFEDD5; color:#C2410C; border:1px solid #FED7AA; }
.cat-BA { background:#DBEAFE; color:#1E3A8A; border:1px solid #93C5FD; }
.cat-CA { background:#E0E7FF; color:#3730A3; border:1px solid #A5B4FC; }
.cat-KA { background:#EDE9FE; color:#5B21B6; border:1px solid #C4B5FD; }
.cat-HA { background:#FCE7F3; color:#831843; border:1px solid #F9A8D4; }
.cat-FA { background:#D1FAE5; color:#064E3B; border:1px solid #6EE7B7; }
.cat-GA { background:#F3F4F6; color:#374151; border:1px solid #D1D5DB; }

/* Avail number — the BIG sell number */
.avail-big {
    font-size: 1.6rem; font-weight: 900; line-height: 1;
    font-variant-numeric: tabular-nums;
}
.av-great { color: #059669; }
.av-ok    { color: #0F6E56; }
.av-low   { color: #D97706; }
.av-zero  { color: #DC2626; }
.av-neg   { color: #991B1B; background:#FEE2E2; padding:2px 8px; border-radius:6px; }

/* Retorno pill */
.ret-pill {
    font-size:.68rem; font-weight:700; padding:2px 7px;
    border-radius:4px; display:inline-block; margin-top:2px;
    background:#DBEAFE; color:#1E40AF; border:1px solid #BFDBFE;
}
.ret-pill.pending { background:#FEF3C7; color:#92400E; border-color:#FCD34D; }

/* Section sub-header */
.sec-head {
    font-size:.7rem; font-weight:700; text-transform:uppercase;
    letter-spacing:.08em; color:#6B7280;
    padding: 6px 12px; background:#F8FAFC;
    border-bottom:1px solid #E2E8F0;
    display:flex; align-items:center; gap:8px;
}

/* Summary strip */
.sum-strip {
    display:flex; gap:0; background:white;
    border:1px solid #E5E7EB; border-radius:10px;
    overflow:hidden; margin-bottom:14px;
    box-shadow:0 1px 3px rgba(0,0,0,.06);
}
.sum-cell {
    flex:1; padding:12px 10px; text-align:center;
    border-right:1px solid #F1F5F9;
}
.sum-cell:last-child { border-right:none; }
.sum-num { font-size:1.5rem; font-weight:900; line-height:1; }
.sum-lbl { font-size:.62rem; text-transform:uppercase; letter-spacing:.06em;
           color:#6B7280; font-weight:700; margin-top:3px; }
.s-green  { color:#059669; }
.s-blue   { color:#1D4ED8; }
.s-orange { color:#EA580C; }
.s-red    { color:#DC2626; }
.s-gray   { color:#6B7280; }
.s-purple { color:#7C3AED; }

/* Reservation list */
.res-row {
    display:flex; align-items:center; gap:0;
    border-left:1px solid #E2E8F0; border-right:1px solid #E2E8F0;
    border-bottom:1px solid #F1F5F9;
    padding:6px 12px; font-size:.79rem; background:white;
}
.res-row:hover { background:#FAFAFA; }
.res-row.overlap { background:#FFFBEB; }
.strip { width:4px; height:32px; border-radius:3px; flex-shrink:0; margin-right:10px; }
.strip-ok     { background:#059669; }
.strip-err    { background:#DC2626; }
.strip-pre    { background:#0284C7; }
.strip-overlap{ background:#D97706; }
.res-time { font-family:monospace; font-weight:700; color:#374151; min-width:50px; }
.zona-pill { font-size:.62rem; font-weight:700; padding:1px 6px; border-radius:3px; min-width:48px; text-align:center; display:inline-block; }
.z-aerop { background:#FEE2E2; color:#991B1B; }
.z-shutt { background:#E0E7FF; color:#3730A3; }
.z-other { background:#F3F4F6; color:#374151; }
.chip { font-size:.7rem; font-weight:700; padding:2px 8px; border-radius:20px; white-space:nowrap; display:inline-flex; align-items:center; gap:4px; }
.chip-ret  { background:#DBEAFE; color:#1D4ED8; border:1px solid #BFDBFE; }
.chip-gar  { background:#FFEDD5; color:#C2410C; border:1px solid #FED7AA; }
.chip-pre  { background:#E0E7FF; color:#3730A3; border:1px solid #A5B4FC; }
.chip-alt  { background:#FEF3C7; color:#92400E; border:1px solid #FDE68A; }
.chip-none { background:#FEE2E2; color:#991B1B; border:1px solid #FECACA; }
.chip-man  { background:#DCFCE7; color:#166534; border:1px solid #86EFAC; }
.chip-dup  { background:#FEF3C7; color:#92400E; border:1px solid #FCD34D; font-size:.62rem; padding:1px 5px; }

/* Model group header */
.model-header {
    background:#F8FAFC; border:1px solid #E2E8F0;
    border-radius:8px 8px 0 0; padding:7px 12px;
    margin-top:10px; display:flex; align-items:center; gap:8px;
}
.model-name { font-weight:800; font-size:.88rem; color:#0F6E56; }

/* Overlap alert */
.overlap-alert {
    background:#FFFBEB; border:1.5px solid #FCD34D; border-radius:8px;
    padding:9px 14px; margin-bottom:10px; font-size:.79rem; color:#92400E;
}

/* Impact banner */
.impact-banner {
    background:#FFF7ED; border:1px solid #FED7AA; border-radius:8px;
    padding:8px 14px; font-size:.77rem; color:#92400E; margin-bottom:10px;
}

/* Truck */
.truck-card {
    background:white; border:1.5px solid #E5E7EB; border-radius:10px;
    padding:12px 14px; margin-bottom:8px;
    box-shadow:0 1px 3px rgba(0,0,0,.05);
}
.truck-header { display:flex; align-items:center; gap:8px; margin-bottom:8px; padding-bottom:8px; border-bottom:1px solid #F1F5F9; }
.truck-name  { font-size:.9rem; font-weight:800; color:#111827; }
.truck-badge { font-size:.7rem; font-weight:700; padding:2px 9px; border-radius:20px; }
.truck-out   { background:#FEE2E2; color:#991B1B; border:1px solid #FECACA; }
.truck-in    { background:#D1FAE5; color:#065F46; border:1px solid #A7F3D0; }
.traslado-row { display:flex; align-items:center; gap:8px; padding:4px 8px; border-radius:5px; font-size:.76rem; margin-bottom:3px; background:#F9FAFB; }
.traslado-row.out { border-left:3px solid #DC2626; }
.traslado-row.in  { border-left:3px solid #059669; }

/* Timeline */
.tl-wrap {
    background:white; border:1px solid #E5E7EB; border-radius:10px;
    padding:14px 16px; overflow-x:auto; margin-bottom:12px;
    box-shadow:0 1px 3px rgba(0,0,0,.05);
}
.tl-row { display:flex; align-items:center; gap:0; margin-bottom:5px; min-width:750px; }
.tl-cat { font-size:.7rem; font-weight:800; min-width:46px; text-align:right; padding-right:8px; }
.tl-track { flex:1; height:26px; background:#F1F5F9; border-radius:5px; position:relative; }
.tl-block { position:absolute; height:20px; top:3px; border-radius:3px; font-size:.58rem; font-weight:700; display:flex; align-items:center; justify-content:center; white-space:nowrap; overflow:hidden; padding:0 3px; cursor:default; border:1px solid rgba(0,0,0,.08); }
.tl-ret { background:#DBEAFE; color:#1E40AF; }
.tl-sal { background:#FEE2E2; color:#991B1B; }
.tl-now { position:absolute; top:0; bottom:0; width:2px; background:#0F6E56; z-index:10; }
.tl-now-lbl { position:absolute; top:-16px; font-size:.58rem; font-weight:700; color:#0F6E56; transform:translateX(-50%); white-space:nowrap; }

/* Metric box */
.metric-box { background:white; border:1px solid #E5E7EB; border-radius:10px; padding:14px; text-align:center; border-top:4px solid #0F6E56; box-shadow:0 1px 3px rgba(0,0,0,.05); }
.metric-box.warn    { border-top-color:#D97706; }
.metric-box.crit    { border-top-color:#DC2626; }
.metric-box.neutral { border-top-color:#9CA3AF; }
.metric-box.blue    { border-top-color:#0284C7; }
.metric-box.purple  { border-top-color:#7C3AED; }
.mv { font-size:2rem; font-weight:900; line-height:1; color:#111827; }
.mv.ok   { color:#059669; } .mv.warn { color:#D97706; } .mv.crit { color:#DC2626; } .mv.blue { color:#0284C7; } .mv.purple { color:#7C3AED; }
.ml { font-size:.66rem; font-weight:700; text-transform:uppercase; letter-spacing:.06em; color:#6B7280; margin-bottom:6px; }
.ms { font-size:.69rem; color:#9CA3AF; margin-top:3px; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] { gap:3px; background:#F1F5F9; padding:4px; border-radius:10px; margin-bottom:14px; }
.stTabs [data-baseweb="tab"] { border-radius:7px !important; font-weight:700 !important; }
.stTabs [aria-selected="true"] { background:white !important; box-shadow:0 1px 3px rgba(0,0,0,.1) !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# CONSTANTS & MAPPINGS
# ─────────────────────────────────────────
CATS_MANU = ["A","B","C"]
CATS_AUTO = ["BA","CA","KA","HA","FA"]
ALL_CATS  = CATS_MANU + CATS_AUTO + ["GA"]
CAT_LABELS = {
    "A":"Manual pequeño","B":"Manual compacto","C":"Manual mediano/SUV",
    "BA":"Auto pequeño","CA":"Auto compacto","KA":"Auto mediano/Premium",
    "HA":"Especial/Cabrio","FA":"Furgoneta/Van","GA":"Especial",
}
CAT_MODELS = {
    "A":["Hyundai i10"],"B":["Hyundai i20","Renault Clio","Citroën C3","Peugeot 208"],
    "C":["Peugeot 2008","Renault Captur","Nissan Juke","Ford Puma"],
    "BA":["Peugeot 208 Auto","Audi A1 Auto","Citroën C4X Aut","C3 Aircross Aut","Peugeot 2008 Auto"],
    "CA":["BMW Serie 1 Aut","Audi Q2 Aut"],"KA":["Leapmotor C10","Mercedes Clase A","BMW X1","Mercedes GLA","BMW iX2","Porsche Cayenne Hybrid"],
    "HA":["Mini Cabrio","BMW Z4 Aut","Peugeot 5008 7p Aut","P7"],
    "FA":["Citroën Berlingo","Renault Kangoo","Ford Transit Auto"],"GA":["Especial"],
}
ZONA_OFFSET = {"AEROP":60,"SHUTT":45}
BASES       = ["Cala d'Or","Calas","Cala Millor","Alcudia","Andra","Maga","Solle","Vida"]
CONDUCTORES = ["LOMBA","JOSE","DIEGO"]
TRAVEL_MINS = 60

# ─────────────────────────────────────────
# REAL DATA — Son Oms 16 Jun 2026
# ─────────────────────────────────────────
GARAJE = [
    # A — Manual pequeño (Hyundai i10)
    {"cod":"A3","cat":"A","modelo":"Hyundai i10","matricula":"9012NJH"},
    {"cod":"A3","cat":"A","modelo":"Hyundai i10","matricula":"9005NJH"},
    {"cod":"A3","cat":"A","modelo":"Hyundai i10","matricula":"4287NJN"},
    {"cod":"A3","cat":"A","modelo":"Hyundai i10","matricula":"4774NJN"},
    {"cod":"A3","cat":"A","modelo":"Hyundai i10","matricula":"4754NJN"},
    # B — Manual compacto
    {"cod":"B3","cat":"B","modelo":"Renault Clio","matricula":"6422NLZ"},
    {"cod":"B3","cat":"B","modelo":"Renault Clio","matricula":"6411NLZ"},
    {"cod":"B3","cat":"B","modelo":"Renault Clio","matricula":"1837NMT"},
    {"cod":"B5","cat":"B","modelo":"Citroën C3","matricula":"7662NLR"},
    {"cod":"B5","cat":"B","modelo":"Citroën C3","matricula":"7661NLR"},
    {"cod":"B5","cat":"B","modelo":"Citroën C3","matricula":"8212NLR"},
    {"cod":"B5","cat":"B","modelo":"Citroën C3","matricula":"8214NLR"},
    {"cod":"B6","cat":"B","modelo":"Peugeot 208","matricula":"8978NJD"},
    {"cod":"B6","cat":"B","modelo":"Peugeot 208","matricula":"1052NJL"},
    # C — Manual mediano
    {"cod":"C1","cat":"C","modelo":"Peugeot 2008","matricula":"9482NNN"},
    {"cod":"C14","cat":"C","modelo":"Ford Puma","matricula":"0283MYP"},
    {"cod":"C3","cat":"C","modelo":"Renault Captur","matricula":"1065MYB"},
    {"cod":"C3","cat":"C","modelo":"Renault Captur","matricula":"3617NLM"},
    {"cod":"C3","cat":"C","modelo":"Renault Captur","matricula":"3624NLM"},
    {"cod":"C3","cat":"C","modelo":"Renault Captur","matricula":"3485NLM"},
    {"cod":"C9","cat":"C","modelo":"Nissan Juke","matricula":"9825NMY"},
    # FA — Furgonetas
    {"cod":"D1","cat":"FA","modelo":"Renault Kangoo","matricula":"2266MYB"},
    {"cod":"D2","cat":"FA","modelo":"Citroën Berlingo","matricula":"0769NLS"},{"cod":"D2","cat":"FA","modelo":"Citroën Berlingo","matricula":"0786NLS"},
    {"cod":"D2","cat":"FA","modelo":"Citroën Berlingo","matricula":"1108NLS"},{"cod":"D2","cat":"FA","modelo":"Citroën Berlingo","matricula":"0783NLS"},
    {"cod":"D2","cat":"FA","modelo":"Citroën Berlingo","matricula":"1105NLS"},{"cod":"D2","cat":"FA","modelo":"Citroën Berlingo","matricula":"8798NLS"},
    {"cod":"D2","cat":"FA","modelo":"Citroën Berlingo","matricula":"0782NLS"},{"cod":"D2","cat":"FA","modelo":"Citroën Berlingo","matricula":"2378NLS"},
    {"cod":"D2","cat":"FA","modelo":"Citroën Berlingo","matricula":"0773NLS"},{"cod":"D2","cat":"FA","modelo":"Citroën Berlingo","matricula":"1119NLS"},
    {"cod":"D2","cat":"FA","modelo":"Citroën Berlingo","matricula":"0835NLS"},{"cod":"D2","cat":"FA","modelo":"Citroën Berlingo","matricula":"0767NLS"},
    {"cod":"D2","cat":"FA","modelo":"Citroën Berlingo","matricula":"0788NLS"},{"cod":"D2","cat":"FA","modelo":"Citroën Berlingo","matricula":"1111NLS"},
    {"cod":"D2","cat":"FA","modelo":"Citroën Berlingo","matricula":"2379NLS"},
    {"cod":"P10","cat":"FA","modelo":"Ford Transit Auto","matricula":"4731NNX"},{"cod":"P10","cat":"FA","modelo":"Ford Transit Auto","matricula":"4720NNX"},
    # BA — Auto pequeño
    {"cod":"E0","cat":"BA","modelo":"Peugeot 208 Auto","matricula":"2534NLN"},{"cod":"E0","cat":"BA","modelo":"Peugeot 208 Auto","matricula":"2460NLN"},
    {"cod":"E2","cat":"BA","modelo":"Audi A1 Auto","matricula":"0672MZH"},{"cod":"E2","cat":"BA","modelo":"Audi A1 Auto","matricula":"0665MZH"},{"cod":"E2","cat":"BA","modelo":"Audi A1 Auto","matricula":"5036NLT"},
    {"cod":"E3","cat":"BA","modelo":"Citroën C4X Aut","matricula":"9460NLN"},{"cod":"E3","cat":"BA","modelo":"Citroën C4X Aut","matricula":"9450NLN"},{"cod":"E3","cat":"BA","modelo":"Citroën C4X Aut","matricula":"2006NLP"},{"cod":"E3","cat":"BA","modelo":"Citroën C4X Aut","matricula":"9219NLN"},
    {"cod":"E6","cat":"BA","modelo":"C3 Aircross Aut","matricula":"7834NJD"},{"cod":"E6","cat":"BA","modelo":"C3 Aircross Aut","matricula":"5408NLN"},{"cod":"E6","cat":"BA","modelo":"C3 Aircross Aut","matricula":"6210NLN"},
    # CA — Auto compacto
    {"cod":"F3","cat":"CA","modelo":"BMW Serie 1 Aut","matricula":"4428NMN"},{"cod":"F3","cat":"CA","modelo":"BMW Serie 1 Aut","matricula":"4449NMN"},
    {"cod":"K1","cat":"CA","modelo":"Audi Q2 Aut","matricula":"0985MYP"},{"cod":"K1","cat":"CA","modelo":"Audi Q2 Aut","matricula":"5213MZH"},
    {"cod":"K1","cat":"CA","modelo":"Audi Q2 Aut","matricula":"6508NLT"},{"cod":"K1","cat":"CA","modelo":"Audi Q2 Aut","matricula":"6513NLT"},{"cod":"K1","cat":"CA","modelo":"Audi Q2 Aut","matricula":"6399NLT"},
    # KA — Auto mediano/premium
    {"cod":"I13","cat":"KA","modelo":"BMW iX2","matricula":"3578MPG"},
    {"cod":"I5","cat":"KA","modelo":"Leapmotor C10","matricula":"6391NMT"},{"cod":"I5","cat":"KA","modelo":"Leapmotor C10","matricula":"6362NMT"},
    {"cod":"I5","cat":"KA","modelo":"Leapmotor C10","matricula":"6373NMT"},{"cod":"I5","cat":"KA","modelo":"Leapmotor C10","matricula":"1983NMW"},
    {"cod":"I5","cat":"KA","modelo":"Leapmotor C10","matricula":"1985NMW"},{"cod":"I5","cat":"KA","modelo":"Leapmotor C10","matricula":"8347NMT"},
    {"cod":"I5","cat":"KA","modelo":"Leapmotor C10","matricula":"8348NMT"},{"cod":"I5","cat":"KA","modelo":"Leapmotor C10","matricula":"6417NMT"},
    {"cod":"I5","cat":"KA","modelo":"Leapmotor C10","matricula":"6368NMT"},{"cod":"I5","cat":"KA","modelo":"Leapmotor C10","matricula":"6480NMT"},
    {"cod":"I5","cat":"KA","modelo":"Leapmotor C10","matricula":"8342NMT"},{"cod":"I5","cat":"KA","modelo":"Leapmotor C10","matricula":"8343NMT"},
    {"cod":"I5","cat":"KA","modelo":"Leapmotor C10","matricula":"8355NMT"},{"cod":"I5","cat":"KA","modelo":"Leapmotor C10","matricula":"8349NMT"},
    {"cod":"I5","cat":"KA","modelo":"Leapmotor C10","matricula":"8350NMT"},{"cod":"I5","cat":"KA","modelo":"Leapmotor C10","matricula":"8354NMT"},
    {"cod":"I5","cat":"KA","modelo":"Leapmotor C10","matricula":"8357NMT"},{"cod":"I5","cat":"KA","modelo":"Leapmotor C10","matricula":"8353NMT"},
    {"cod":"I5","cat":"KA","modelo":"Leapmotor C10","matricula":"6377NMT"},
    {"cod":"I9","cat":"KA","modelo":"Porsche Cayenne Hybrid","matricula":"1636NJF"},
    {"cod":"T0","cat":"KA","modelo":"Mercedes Clase A","matricula":"6426NLW"},
    {"cod":"T1","cat":"KA","modelo":"BMW X1","matricula":"9852NNC"},{"cod":"T1","cat":"KA","modelo":"BMW X1","matricula":"2737NNL"},
    {"cod":"T2","cat":"KA","modelo":"Mercedes GLA","matricula":"8224NLW"},{"cod":"T2","cat":"KA","modelo":"Mercedes GLA","matricula":"7755NLW"},{"cod":"T2","cat":"KA","modelo":"Mercedes GLA","matricula":"7750NLW"},
    # HA — Especial/Cabrio/7p
    {"cod":"O4","cat":"HA","modelo":"Mini Cabrio","matricula":"3878NBM"},
    {"cod":"O8","cat":"HA","modelo":"BMW Z4 Aut","matricula":"0369MPR"},
    {"cod":"P5","cat":"HA","modelo":"Peugeot 5008 7p Aut","matricula":"8964NJD"},{"cod":"P5","cat":"HA","modelo":"Peugeot 5008 7p Aut","matricula":"4185NPB"},
    {"cod":"P5","cat":"HA","modelo":"Peugeot 5008 7p Aut","matricula":"4192NPB"},{"cod":"P5","cat":"HA","modelo":"Peugeot 5008 7p Aut","matricula":"4186NPB"},
]

RETORNOS = [
    {"hora":"12:00","cod":"A","cat":"A","modelo":"Manual pequeño","matricula":"","zona":"AVIPM"},
    {"hora":"18:30","cod":"A3","cat":"A","modelo":"Hyundai i10","matricula":"4791NJN","zona":"AEROP"},
    {"hora":"20:30","cod":"A3","cat":"A","modelo":"Hyundai i10","matricula":"5685NJN","zona":"AEROP"},
    {"hora":"17:43","cod":"B1","cat":"B","modelo":"Hyundai i20","matricula":"1395NJJ","zona":"AEROP"},
    {"hora":"20:00","cod":"B3","cat":"B","modelo":"Renault Clio","matricula":"0769MYB","zona":"SHUTT"},
    {"hora":"22:30","cod":"B3","cat":"B","modelo":"Renault Clio","matricula":"3943NMT","zona":"AEROP"},
    {"hora":"18:02","cod":"B5","cat":"B","modelo":"Citroën C3","matricula":"8209NLR","zona":"AEROP"},
    {"hora":"19:30","cod":"B5","cat":"B","modelo":"Citroën C3","matricula":"7665NLR","zona":"SHUTT"},
    {"hora":"20:00","cod":"B5","cat":"B","modelo":"Citroën C3","matricula":"7650NLR","zona":"SHUTT"},
    {"hora":"23:00","cod":"B5","cat":"B","modelo":"Citroën C3","matricula":"7651NLR","zona":"PALMA"},
    {"hora":"19:00","cod":"B6","cat":"B","modelo":"Peugeot 208","matricula":"8991NJD","zona":"CALVI"},
    {"hora":"19:00","cod":"C3","cat":"C","modelo":"Renault Captur","matricula":"3618NLM","zona":"PASTI"},
    {"hora":"19:00","cod":"C9","cat":"C","modelo":"Nissan Juke","matricula":"9815NMY","zona":"PASTI"},
    {"hora":"17:54","cod":"E0","cat":"BA","modelo":"Peugeot 208 Auto","matricula":"9477NNN","zona":"AEROP"},
    {"hora":"18:00","cod":"E0","cat":"BA","modelo":"Peugeot 208 Auto","matricula":"2465NLN","zona":"AEROP"},
    {"hora":"19:00","cod":"E0","cat":"BA","modelo":"Peugeot 208 Auto","matricula":"6355NLM","zona":"ILLET"},
    {"hora":"19:30","cod":"E0","cat":"BA","modelo":"Peugeot 208 Auto","matricula":"2447NLN","zona":"AEROP"},
    {"hora":"19:30","cod":"E0","cat":"BA","modelo":"Peugeot 208 Auto","matricula":"6221NLM","zona":"SHUTT"},
    {"hora":"19:00","cod":"E2","cat":"BA","modelo":"Audi A1 Auto","matricula":"5070NLT","zona":"CALVI"},
    {"hora":"20:00","cod":"E2","cat":"BA","modelo":"Audi A1 Auto","matricula":"0657MZH","zona":"SHUTT"},
    {"hora":"19:00","cod":"E3","cat":"BA","modelo":"Citroën C4X Aut","matricula":"2011NLP","zona":"PALMA"},
    {"hora":"23:00","cod":"E3","cat":"BA","modelo":"Citroën C4X Aut","matricula":"9544NLN","zona":"SOLLE"},
    {"hora":"19:30","cod":"E6","cat":"BA","modelo":"C3 Aircross Aut","matricula":"3926NLN","zona":"AEROP"},
    {"hora":"23:30","cod":"E6","cat":"BA","modelo":"C3 Aircross Aut","matricula":"5274NLN","zona":"AEROP"},
    {"hora":"23:00","cod":"F3","cat":"CA","modelo":"BMW Serie 1 Aut","matricula":"4436NMN","zona":"PORTA"},
    {"hora":"23:00","cod":"F3","cat":"CA","modelo":"BMW Serie 1 Aut","matricula":"7609NLR","zona":"PALMA"},
    {"hora":"19:00","cod":"K1","cat":"CA","modelo":"Audi Q2 Aut","matricula":"6506NLT","zona":"ARENA"},
    {"hora":"19:00","cod":"O4","cat":"HA","modelo":"Mini Cabrio","matricula":"3877NBM","zona":"PALMA"},
    {"hora":"19:30","cod":"O4","cat":"HA","modelo":"Mini Cabrio","matricula":"0036MZT","zona":"AEROP"},
    {"hora":"23:59","cod":"O7","cat":"HA","modelo":"O7","matricula":"7604NLR","zona":"PORTA"},
    {"hora":"18:00","cod":"P5","cat":"HA","modelo":"Peugeot 5008 7p","matricula":"9183NLR","zona":"SOLLE"},
    {"hora":"19:00","cod":"P7","cat":"HA","modelo":"P7","matricula":"1448NGC","zona":"SHUTT"},
    {"hora":"23:00","cod":"T0","cat":"KA","modelo":"Mercedes Clase A","matricula":"6446NLW","zona":"PORTA"},
    {"hora":"23:00","cod":"T2","cat":"KA","modelo":"Mercedes GLA","matricula":"7744NLW","zona":"PALMA"},
]

RESERVAS = [
    # A
    {"hora":"11:15","cat":"A","cod":"A","matricula":"","num":601,"zona":"PASTI","agencia":"GARAJE","hotel":"1501 CHALET","obs":"IRA A SON OMS"},
    {"hora":"18:00","cat":"A","cod":"A3","matricula":"5436NJN","num":499,"zona":"AEROP","agencia":"OFFUGO","hotel":"1504"},
    {"hora":"22:30","cat":"A","cod":"A","matricula":"","num":582,"zona":"SHUTT","agencia":"GARAJE","hotel":"1501"},
    # B
    {"hora":"18:30","cat":"B","cod":"B3","matricula":"3957NMT","num":522,"zona":"SHUTT","agencia":"GARAJE","hotel":"1501 CASA PRIVADA"},
    {"hora":"18:30","cat":"B","cod":"B3","matricula":"1549NMT","num":587,"zona":"AEROP","agencia":"OFFUGO","hotel":"1504"},
    {"hora":"18:30","cat":"B","cod":"B3","matricula":"5034NMT","num":588,"zona":"AEROP","agencia":"OFFUGO","hotel":"1504"},
    {"hora":"21:00","cat":"B","cod":"B","matricula":"","num":482,"zona":"SHUTT","agencia":"OFFUGO","hotel":"1504"},
    {"hora":"21:30","cat":"B","cod":"B","matricula":"","num":538,"zona":"SHUTT","agencia":"OFFUGO","hotel":"1504"},
    {"hora":"21:30","cat":"B","cod":"B","matricula":"","num":579,"zona":"SHUTT","agencia":"GARAJE","hotel":"1501 Privat Cala Mondragó"},
    {"hora":"22:30","cat":"B","cod":"B","matricula":"","num":526,"zona":"SHUTT","agencia":"OFFUGO","hotel":"1504"},
    {"hora":"22:30","cat":"B","cod":"B","matricula":"","num":556,"zona":"AEROP","agencia":"GARAJE","hotel":"1501"},
    # BA
    {"hora":"19:00","cat":"BA","cod":"E0","matricula":"7045NLM","num":474,"zona":"SHUTT","agencia":"OFFUGO","hotel":"1504"},
    {"hora":"19:00","cat":"BA","cod":"BA","matricula":"","num":488,"zona":"AEROP","agencia":"OFFUGO","hotel":"1504"},
    {"hora":"19:30","cat":"BA","cod":"BA","matricula":"","num":466,"zona":"AEROP","agencia":"OFFUGO","hotel":"1504"},
    {"hora":"19:30","cat":"BA","cod":"BA","matricula":"","num":473,"zona":"AEROP","agencia":"GARAJE","hotel":"1501"},
    {"hora":"23:30","cat":"BA","cod":"BA","matricula":"","num":520,"zona":"AEROP","agencia":"OFFUGO","hotel":"1504"},
    {"hora":"23:30","cat":"BA","cod":"BA","matricula":"","num":502,"zona":"SHUTT","agencia":"OFFUGO","hotel":"1504"},
    # C
    {"hora":"20:00","cat":"C","cod":"C","matricula":"","num":563,"zona":"AEROP","agencia":"OFFUGO","hotel":"1504"},
    # CA
    {"hora":"19:00","cat":"CA","cod":"E6","matricula":"5403NLN","num":461,"zona":"SHUTT","agencia":"SANTANYI RENT","hotel":"1501"},
    {"hora":"19:30","cat":"CA","cod":"CA","matricula":"","num":452,"zona":"SHUTT","agencia":"OFFUGO","hotel":"1504"},
    {"hora":"19:30","cat":"CA","cod":"CA","matricula":"","num":508,"zona":"SHUTT","agencia":"OFFUGO","hotel":"1504"},
    {"hora":"19:30","cat":"CA","cod":"I5","matricula":"","num":506,"zona":"SHUTT","agencia":"GARAJE","hotel":"1501","tipo":"H"},
    {"hora":"23:30","cat":"CA","cod":"CA","matricula":"","num":491,"zona":"AEROP","agencia":"OFFUGO","hotel":"1504"},
    # KA
    {"hora":"20:00","cat":"KA","cod":"I5","matricula":"","num":496,"zona":"SHUTT","agencia":"GARAJE","hotel":"1501","tipo":"H"},
    {"hora":"20:00","cat":"KA","cod":"I5","matricula":"","num":495,"zona":"SHUTT","agencia":"GARAJE","hotel":"1501","tipo":"H"},
    # HA
    {"hora":"18:00","cat":"HA","cod":"O4","matricula":"0034MZT","num":539,"zona":"SHUTT","agencia":"OFFUGO","hotel":"1504"},
    # GA / Especial
    {"hora":"15:30","cat":"GA","cod":"MC1","matricula":"1019MXM","num":605,"zona":"SHUTT","agencia":"CDW","hotel":"OFICINA SON OMS","obs":"RELACIONES PUB"},
    {"hora":"23:00","cat":"GA","cod":"GA","matricula":"","num":546,"zona":"SHUTT","agencia":"GARAJE","hotel":"1501 Villa calador"},
]

# ─────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────
def to_dt(hora):
    t = datetime.strptime(hora, "%H:%M")
    return datetime.now().replace(hour=t.hour, minute=t.minute, second=0, microsecond=0)

def avail_dt(hora, zona):
    return to_dt(hora) + timedelta(minutes=ZONA_OFFSET.get(zona.upper().strip(), 0))

def avail_str(hora, zona):
    return avail_dt(hora, zona).strftime("%H:%M")

def arrival_dt(hora_salida):
    return to_dt(hora_salida) + timedelta(minutes=TRAVEL_MINS)

def arrival_str(hora_salida):
    return arrival_dt(hora_salida).strftime("%H:%M")

def pct_tl(hora_str, offset_mins=0):
    DAY_START, DAY_END = 11, 24
    h, m = map(int, hora_str.split(":"))
    total = h*60 + m + offset_mins
    return max(0, min(100, (total - DAY_START*60) / ((DAY_END-DAY_START)*60) * 100))

# ─────────────────────────────────────────
# TRASLADO IMPACT
# ─────────────────────────────────────────
def compute_traslado_impacts(traslados, sim_now):
    removed = set()
    added   = []
    for t in traslados:
        if t["direction"] == "out":
            for c in t["cars"]:
                if c["matricula"]: removed.add(c["matricula"])
        else:
            arr_dt = arrival_dt(t["hora"])
            arr_s  = arr_dt.strftime("%H:%M")
            avail  = arr_dt <= sim_now
            for c in t["cars"]:
                if c["cat"] and c["matricula"]:
                    added.append({**c,"avail_dt":arr_dt,"avail_str":arr_s,"disponible":avail,"conductor":t["conductor"],"base":t["base"]})
    return removed, added

# ─────────────────────────────────────────
# ASSIGNMENT ENGINE
# ─────────────────────────────────────────
def auto_assign(reservas, garaje, retornos, sim_now, removed, added_cars):
    garaje_pool = [dict(c, used=False) for c in garaje if c["matricula"] not in removed]
    ret_pool    = []
    for r in retornos:
        if r["matricula"] in removed: continue
        av = avail_dt(r["hora"], r["zona"])
        ret_pool.append(dict(r, avail_dt=av, avail_str=avail_str(r["hora"],r["zona"]), used=False))
    for ac in added_cars:
        if ac["disponible"]:
            garaje_pool.append({"cat":ac["cat"],"modelo":ac["modelo"],"matricula":ac["matricula"],"cod":ac["cat"],"used":False})
        else:
            ret_pool.append({"cat":ac["cat"],"modelo":ac["modelo"],"matricula":ac["matricula"],
                             "avail_dt":ac["avail_dt"],"avail_str":ac["avail_str"],"zona":"TRASLADO","hora":ac["avail_str"],"cod":ac["cat"],"used":False})

    assignments = []
    for res in reservas:
        res_dt = to_dt(res["hora"])
        cat    = res["cat"]
        assigned = source = None
        note = ""; mod_chip = ""; alt_sugg = []

        # Pre-assigned in PDF
        if res.get("matricula"):
            assigned = res["matricula"]
            source   = "preasignado"
            mod_chip = res.get("cod","")
            note     = f"Asignado en PDF · {res['cod']}"
            # Mark as used if in pools
            for c in garaje_pool:
                if c["matricula"] == assigned: c["used"] = True
            for r in ret_pool:
                if r["matricula"] == assigned: r["used"] = True
        else:
            # 1. Return exact cat
            cands = sorted([r for r in ret_pool if not r["used"] and r["cat"]==cat and r["avail_dt"]<=res_dt], key=lambda x: x["avail_dt"])
            if cands:
                r2=cands[0]; r2["used"]=True
                assigned=r2["matricula"]; source="retorno"; mod_chip=r2.get("cod",r2["modelo"])
                note=f"Retorno {r2['hora']} · {r2['zona']} · disp. {r2['avail_str']}"

            # 2. Garaje exact cat
            if not assigned:
                for c in garaje_pool:
                    if not c["used"] and c["cat"]==cat:
                        c["used"]=True; assigned=c["matricula"]; source="garaje"; mod_chip=c.get("cod",c["modelo"]); break

            # 3. Garaje adjacent cat
            if not assigned:
                ci = ALL_CATS.index(cat) if cat in ALL_CATS else -1
                for c in garaje_pool:
                    if not c["used"] and c["cat"] in ALL_CATS and ALL_CATS.index(c["cat"])==ci+1:
                        c["used"]=True; assigned=c["matricula"]; source="garaje_alt"
                        mod_chip=c.get("cod",c["modelo"]); note=f"Alt: {c['cat']} ({c['modelo']})"; break

            # 4. Return adjacent cat
            if not assigned:
                ci = ALL_CATS.index(cat) if cat in ALL_CATS else -1
                cands = sorted([r for r in ret_pool if not r["used"] and r["cat"] in ALL_CATS
                                and ALL_CATS.index(r["cat"])==ci+1 and r["avail_dt"]<=res_dt], key=lambda x: x["avail_dt"])
                if cands:
                    r2=cands[0]; r2["used"]=True
                    assigned=r2["matricula"]; source="retorno_alt"; mod_chip=r2.get("cod","")
                    note=f"Alt {r2['cat']} · ret {r2['hora']} disp. {r2['avail_str']}"

            if not assigned:
                for c in garaje_pool:
                    if not c["used"]:
                        alt_sugg.append(f"{c['cat']} · {c['modelo']} · {c['matricula']}")
                        if len(alt_sugg)>=3: break
                if len(alt_sugg)<3:
                    for r2 in ret_pool:
                        if not r2["used"]:
                            alt_sugg.append(f"{r2['cat']} · {r2['modelo']} · {r2['matricula']} (ret {r2.get('hora','—')}→{r2['avail_str']})")
                            if len(alt_sugg)>=3: break

        assignments.append({**res,"assigned":assigned,"source":source,"note":note,"mod_chip":mod_chip,"sugg":alt_sugg})
    return assignments, garaje_pool, ret_pool

def detect_overlaps(assignments):
    cnt = defaultdict(int)
    for a in assignments:
        if a["assigned"]: cnt[a["assigned"]] += 1
    return {m for m,c in cnt.items() if c>1}

# ─────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────
now = datetime.now()
for k,v in {"sim_h":now.hour,"sim_m":now.minute,"use_sim":False,"threshold":2,
             "overrides":{},"filter_state":"todos","traslados":[]}.items():
    if k not in st.session_state: st.session_state[k] = v

sim_now = now.replace(hour=st.session_state.sim_h,minute=st.session_state.sim_m,second=0) \
    if st.session_state.use_sim else now

# ─────────────────────────────────────────
# COMPUTE
# ─────────────────────────────────────────
removed, added_cars = compute_traslado_impacts(st.session_state.traslados, sim_now)
base_asgn, gp, rp  = auto_assign(RESERVAS, GARAJE, RETORNOS, sim_now, removed, added_cars)

all_cars_sel = []
for c in GARAJE:
    if c["matricula"] not in removed:
        all_cars_sel.append({"label":f"[{c['cat']}] {c['matricula']} — {c['modelo']} · GARAJE","matricula":c["matricula"],"cat":c["cat"]})
for r in RETORNOS:
    if r["matricula"] and r["matricula"] not in removed:
        av=avail_str(r["hora"],r["zona"])
        all_cars_sel.append({"label":f"[{r['cat']}] {r['matricula']} — {r['modelo']} · RET {r['hora']}→{av}","matricula":r["matricula"],"cat":r["cat"]})
for ac in added_cars:
    all_cars_sel.append({"label":f"[{ac['cat']}] {ac['matricula']} — {ac['modelo']} · TRASLADO {ac['avail_str']}","matricula":ac["matricula"],"cat":ac["cat"]})

assignments = []
for i,a in enumerate(base_asgn):
    if i in st.session_state.overrides:
        mat=st.session_state.overrides[i]
        car=next((c for c in all_cars_sel if c["matricula"]==mat),None)
        if car:
            assignments.append({**a,"assigned":mat,"source":"manual","note":f"Manual · {mat}"})
            continue
    assignments.append(a)

overlapped = detect_overlaps(assignments)

# ─────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────
st.markdown(f"""
<div class="rfm-header">
  <div>
    <h1>🚗 Roig Fleet Manager</h1>
    <div class="sub">Son Oms · ROIG · HASSO · AVIS · MARASON</div>
  </div>
  <div>
    <div class="clock">{now.strftime('%H:%M:%S')}</div>
    <div class="date">{now.strftime('%d %b %Y').upper()} · Son Oms</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Controles")
    st.session_state.threshold = st.number_input("Umbral alerta stock",0,10,st.session_state.threshold)
    st.divider()
    st.markdown("### ⏱ Simular hora")
    st.session_state.sim_h   = st.slider("Hora",0,23,st.session_state.sim_h)
    st.session_state.sim_m   = st.slider("Minuto",0,59,st.session_state.sim_m)
    st.session_state.use_sim = st.checkbox("Activar simulación",st.session_state.use_sim)
    if st.session_state.use_sim:
        st.info(f"⏱ Simulando **{st.session_state.sim_h:02d}:{st.session_state.sim_m:02d}**")
    st.divider()
    if st.button("🔄 Resetear asignaciones manuales",use_container_width=True):
        st.session_state.overrides={}; st.rerun()
    st.divider()
    st.markdown("**Leyenda:**")
    st.markdown("🔵 Retorno · 🟠 Garaje · 📋 Preasignado PDF")
    st.markdown("🟡 Alternativa · 🔴 Sin coche · ⚠️ Duplicada")

# ─────────────────────────────────────────
# TABS
# ─────────────────────────────────────────
tab_sell, tab_asgn, tab_trucks, tab_tl = st.tabs([
    "🟢  Qué puedo vender",
    "📋  Asignación de reservas",
    "🚛  Traslados",
    "📅  Línea de tiempo",
])

# ══════════════════════════════════════════
# TAB 0 — SELL BOARD (main feature)
# ══════════════════════════════════════════
with tab_sell:

    # Compute per-category stock
    eff_garaje = [c for c in GARAJE if c["matricula"] not in removed]
    for ac in added_cars:
        if ac["disponible"]: eff_garaje.append({"cat":ac["cat"],"modelo":ac["modelo"],"matricula":ac["matricula"],"cod":ac["cat"]})

    ret_proc = []
    for r in RETORNOS:
        if r["matricula"] in removed: continue
        av = avail_dt(r["hora"], r["zona"])
        ret_proc.append({**r,"avail_dt":av,"avail_str":avail_str(r["hora"],r["zona"]),"disponible":av<=sim_now})
    for ac in added_cars:
        ret_proc.append({**ac,"zona":"TRASLADO","hora":ac["avail_str"],"cod":ac["cat"]})

    res_proc = [{**s,"realizada":to_dt(s["hora"])<=sim_now} for s in RESERVAS]

    thr = st.session_state.threshold

    st.markdown(f"""
    <div class="sell-board">
      <div class="sell-board-head">
        <h2>📦 Stock disponible para vender — Son Oms · {sim_now.strftime('%H:%M')} {'🕐 simulado' if st.session_state.use_sim else '⏱ tiempo real'}</h2>
        <span class="ts">16 Jun 2026 · Datos PDF 18:03</span>
      </div>
    """, unsafe_allow_html=True)

    # Table header
    st.markdown("""
    <div class="sell-row header">
      <div class="sell-col">Categoría</div>
      <div class="sell-col">Descripción · modelos</div>
      <div class="sell-col right">Garaje</div>
      <div class="sell-col right">Retornos<br>disponibles</div>
      <div class="sell-col right">Salidas<br>hechas</div>
      <div class="sell-col right">Res.<br>pend.</div>
      <div class="sell-col center">🟢 DISPONIBLE<br>AHORA</div>
    </div>
    """, unsafe_allow_html=True)

    total_now = 0
    total_eod = 0
    cat_data  = []

    for cat in ALL_CATS:
        g_gar  = [c for c in eff_garaje if c["cat"]==cat]
        g_retd = [r for r in ret_proc if r["cat"]==cat and r["disponible"]]
        g_rett = [r for r in ret_proc if r["cat"]==cat]
        g_rets_pend = [r for r in ret_proc if r["cat"]==cat and not r["disponible"]]
        g_salh = [s for s in res_proc if s["cat"]==cat and s["realizada"]]
        g_salp = [s for s in res_proc if s["cat"]==cat and not s["realizada"]]

        sn = len(g_gar) + len(g_retd) - len(g_salh)
        se = len(g_gar) + len(g_rett) - len(g_salh) - len(g_salp)

        if not g_gar and not g_rett and not g_salh and not g_salp: continue

        total_now += max(0, sn)
        total_eod += max(0, se)
        cat_data.append({"cat":cat,"sn":sn,"se":se,"garaje":len(g_gar),
                          "ret_disp":len(g_retd),"ret_pend":g_rets_pend,
                          "sal_h":len(g_salh),"sal_p":len(g_salp)})

        # Avail class
        if sn <= 0:   av_cls = "av-neg"  if sn < 0 else "av-zero"
        elif sn <= thr: av_cls = "av-low"
        elif sn <= 5:   av_cls = "av-ok"
        else:           av_cls = "av-great"

        # Next returns chip
        ret_pend_html = ""
        for rp in sorted(g_rets_pend, key=lambda x: x["avail_dt"])[:2]:
            ret_pend_html += f'<span class="ret-pill pending">+1 a las {rp["avail_str"]}</span> '

        # Models string
        mods = CAT_MODELS.get(cat,[])
        mods_str = " · ".join(mods[:3]) + ("…" if len(mods)>3 else "")

        cat_type = "auto" if cat in CATS_AUTO else "manu" if cat in CATS_MANU else ""

        st.markdown(f"""
        <div class="sell-row">
          <div class="sell-col">
            <span class="cat-badge cat-{cat}">{cat}</span><br>
            <span style="font-size:.65rem;color:#6B7280">{'AUTO' if cat in CATS_AUTO else 'MANUAL' if cat in CATS_MANU else 'ESP'}</span>
          </div>
          <div class="sell-col">
            <div style="font-weight:700;font-size:.82rem;color:#111827">{CAT_LABELS.get(cat,'')}</div>
            <div style="font-size:.68rem;color:#9CA3AF;margin-top:2px">{mods_str}</div>
            {ret_pend_html}
          </div>
          <div class="sell-col right" style="font-family:monospace;font-weight:700">{len(g_gar)}</div>
          <div class="sell-col right" style="font-family:monospace;font-weight:700;color:#1D4ED8">{len(g_retd)}</div>
          <div class="sell-col right" style="font-family:monospace;color:#6B7280">{len(g_salh)}</div>
          <div class="sell-col right" style="font-family:monospace;color:#D97706">{len(g_salp)}</div>
          <div class="sell-col center">
            <span class="avail-big {av_cls}">{sn}</span>
            <div style="font-size:.65rem;color:#9CA3AF;margin-top:2px">fin día: {se}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Big totals ────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    c1,c2,c3,c4,c5 = st.columns(5)
    with c1:
        st.markdown(f'<div class="metric-box neutral"><div class="ml">Garaje Son Oms</div><div class="mv">{len(eff_garaje)}</div><div class="ms">de {len(GARAJE)} total</div></div>',unsafe_allow_html=True)
    with c2:
        ret_d_total = sum(1 for r in ret_proc if r["disponible"])
        st.markdown(f'<div class="metric-box blue"><div class="ml">Retornos disponibles</div><div class="mv blue">{ret_d_total}</div><div class="ms">de {len(ret_proc)} retornos hoy</div></div>',unsafe_allow_html=True)
    with c3:
        sal_h_total = sum(1 for s in res_proc if s["realizada"])
        st.markdown(f'<div class="metric-box warn"><div class="ml">Salidas realizadas</div><div class="mv warn">{sal_h_total}</div><div class="ms">de {len(RESERVAS)} reservas hoy</div></div>',unsafe_allow_html=True)
    with c4:
        sal_p_total = sum(1 for s in res_proc if not s["realizada"])
        st.markdown(f'<div class="metric-box warn"><div class="ml">Reservas pendientes</div><div class="mv warn">{sal_p_total}</div><div class="ms">por salir hoy</div></div>',unsafe_allow_html=True)
    with c5:
        av_cls_tot = "ok" if total_now > 10 else ("warn" if total_now > 3 else "crit")
        st.markdown(f'<div class="metric-box {"" if total_now>thr else "crit"}"><div class="ml">🟢 DISPONIBLE AHORA</div><div class="mv {av_cls_tot}">{total_now}</div><div class="ms">fin de día estimado: {total_eod}</div></div>',unsafe_allow_html=True)

    # ── Next returns ──────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 🔁 Próximos retornos — cuándo tendrás más coches disponibles")
    pend_rets = sorted([r for r in ret_proc if not r["disponible"]], key=lambda x: x["avail_dt"])
    if pend_rets:
        df_r = pd.DataFrame([{
            "Disponible a": r["avail_str"],
            "Cat.":         r["cat"],
            "Modelo":       r["modelo"],
            "Matrícula":    r.get("matricula","—") or "—",
            "Zona retorno": r["zona"],
            "Hora retorno": r.get("hora","—"),
        } for r in pend_rets])
        st.dataframe(df_r, use_container_width=True, hide_index=True, height=300)
    else:
        st.success("✅ Todos los retornos del día ya están disponibles.")

    # ── Export ────────────────────────────────────
    st.divider()
    ex1, ex2 = st.columns(2)
    with ex1:
        out = io.StringIO(); w = csv.writer(out)
        w.writerow(["Cat","Descripción","Garaje","Ret.disp.","Salidas","Res.pend.","Disponible ahora","Fin día"])
        for d in cat_data:
            w.writerow([d["cat"],CAT_LABELS.get(d["cat"],""),d["garaje"],d["ret_disp"],d["sal_h"],d["sal_p"],d["sn"],d["se"]])
        st.download_button("⬇ CSV stock","\ufeff"+out.getvalue(),
            f"roig_stock_{now.strftime('%Y%m%d_%H%M')}.csv","text/csv",use_container_width=True)
    with ex2:
        out2 = io.StringIO()
        out2.write(f"ROIG FLEET MANAGER — STOCK DISPONIBLE\n{'='*45}\nSon Oms · {now.strftime('%d/%m/%Y')} · {sim_now.strftime('%H:%M')}\n\n")
        for d in cat_data:
            s="SIN STOCK" if d["sn"]<=0 else ("BAJO" if d["sn"]<=thr else "OK")
            out2.write(f"{d['cat']:4} {CAT_LABELS.get(d['cat'],''):30} | Ahora: {d['sn']:3} | Fin día: {d['se']:3} | {s}\n")
        out2.write(f"\nTOTAL DISPONIBLE AHORA: {total_now}\n")
        st.download_button("📄 TXT resumen",out2.getvalue(),
            f"roig_stock_{now.strftime('%Y%m%d_%H%M')}.txt","text/plain",use_container_width=True)

# ══════════════════════════════════════════
# TAB 1 — ASSIGNMENT
# ══════════════════════════════════════════
with tab_asgn:

    n_pre = sum(1 for a in assignments if a["source"]=="preasignado")
    n_ret = sum(1 for a in assignments if a["source"]=="retorno")
    n_gar = sum(1 for a in assignments if a["source"]=="garaje")
    n_alt = sum(1 for a in assignments if a["source"] in ("garaje_alt","retorno_alt"))
    n_man = sum(1 for a in assignments if a["source"]=="manual")
    n_err = sum(1 for a in assignments if not a["assigned"])
    n_dup = len(overlapped)

    if overlapped:
        st.markdown(f'<div class="overlap-alert">⚠️ <strong>Matrícula duplicada:</strong> {", ".join(sorted(overlapped))} — asignada a más de una reserva. Revisa manualmente.</div>',unsafe_allow_html=True)

    if removed or added_cars:
        parts=[]
        if removed: parts.append(f"🚛 {len(removed)} coches en traslado saliente")
        if added_cars: parts.append(f"🟣 {len(added_cars)} entrantes ({sum(1 for ac in added_cars if ac['disponible'])} disponibles)")
        st.markdown(f'<div class="impact-banner">{"  ·  ".join(parts)}</div>',unsafe_allow_html=True)

    # Summary strip
    st.markdown(f"""
    <div class="sum-strip">
      <div class="sum-cell"><div class="sum-num s-green">{n_pre+n_ret+n_gar+n_man}</div><div class="sum-lbl">🟢 Cubiertas</div></div>
      <div class="sum-cell"><div class="sum-num" style="color:#374151">{n_pre}</div><div class="sum-lbl">📋 PDF</div></div>
      <div class="sum-cell"><div class="sum-num s-blue">{n_ret}</div><div class="sum-lbl">🔵 Retorno</div></div>
      <div class="sum-cell"><div class="sum-num s-orange">{n_gar}</div><div class="sum-lbl">🟠 Garaje</div></div>
      <div class="sum-cell"><div class="sum-num" style="color:#D97706">{n_alt}</div><div class="sum-lbl">🟡 Alt.</div></div>
      <div class="sum-cell"><div class="sum-num s-red">{n_err}</div><div class="sum-lbl">🔴 Sin coche</div></div>
      <div class="sum-cell"><div class="sum-num" style="color:{'#D97706' if n_dup>0 else '#9CA3AF'}">{n_dup}</div><div class="sum-lbl">⚠️ Duplic.</div></div>
      <div class="sum-cell"><div class="sum-num" style="color:#6B7280">{len(assignments)}</div><div class="sum-lbl">Total</div></div>
    </div>
    """, unsafe_allow_html=True)

    # Filter
    fcols = st.columns(6)
    filters = [("todos","📋 Todos",len(assignments)),("ok","🟢 Cubiertas",n_pre+n_ret+n_gar+n_man),
               ("retorno","🔵 Retorno",n_ret),("garaje","🟠 Garaje",n_gar),
               ("sin_coche","🔴 Sin coche",n_err),("overlap","⚠️ Duplic.",n_dup)]
    for col,(fk,fl,fc) in zip(fcols,filters):
        with col:
            active = st.session_state.filter_state == fk
            if st.button(f"{fl} ({fc})",key=f"f_{fk}",use_container_width=True,type="primary" if active else "secondary"):
                st.session_state.filter_state=fk; st.rerun()

    def apply_filter(lst, fstate, over):
        if fstate=="todos":     return lst
        if fstate=="ok":        return [a for a in lst if a["assigned"]]
        if fstate=="retorno":   return [a for a in lst if a["source"]=="retorno"]
        if fstate=="garaje":    return [a for a in lst if a["source"]=="garaje"]
        if fstate=="sin_coche": return [a for a in lst if not a["assigned"]]
        if fstate=="overlap":   return [a for a in lst if a["assigned"] in over]
        return lst

    filtered = apply_filter(assignments, st.session_state.filter_state, overlapped)

    groups = OrderedDict()
    for cat in ALL_CATS:
        ca = [a for a in filtered if a["cat"]==cat]
        if ca: groups[cat] = ca

    for cat, cat_asgns in groups.items():
        cat_type = "auto" if cat in CATS_AUTO else "manu" if cat in CATS_MANU else ""
        n_ok_c  = sum(1 for a in cat_asgns if a["assigned"])
        n_err_c = sum(1 for a in cat_asgns if not a["assigned"])
        n_dup_c = sum(1 for a in cat_asgns if a["assigned"] in overlapped)
        err_h   = f'<span style="color:#DC2626;font-weight:700">{n_err_c} sin coche</span>' if n_err_c else "0 sin coche"
        dup_h   = f'&nbsp;·&nbsp;<span style="color:#D97706;font-weight:700">⚠️ {n_dup_c} dup.</span>' if n_dup_c else ""

        st.markdown(f"""
        <div class="model-header">
          <span>{"⚙️" if cat in CATS_AUTO else "🔧" if cat in CATS_MANU else "⭐"}</span>
          <span class="model-name">{cat}</span>
          <span class="cat-badge cat-{cat}">{CAT_LABELS.get(cat,cat)}</span>
          <span style="font-size:.71rem;color:#6B7280;margin-left:auto">{n_ok_c} cubiertas · {err_h}{dup_h} · {len(cat_asgns)} reservas</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""<div style="display:flex;background:#F8FAFC;padding:5px 12px 5px 26px;
            border-left:1px solid #E2E8F0;border-right:1px solid #E2E8F0;
            font-size:.62rem;font-weight:700;text-transform:uppercase;letter-spacing:.05em;color:#94A3B8;">
          <span style="min-width:50px">Hora</span>
          <span style="min-width:60px;margin-left:10px">Zona</span>
          <span style="min-width:195px;margin-left:8px">Coche asignado</span>
          <span style="min-width:155px;margin-left:8px">Detalle</span>
          <span style="min-width:50px;margin-left:8px">Num.</span>
          <span style="margin-left:auto">Hotel / Agencia</span>
        </div>""", unsafe_allow_html=True)

        for i_g,a in [(j,x) for j,x in enumerate(assignments) if x["cat"]==cat and x in filtered]:
            src    = a["source"] or ""
            is_dup = a["assigned"] in overlapped if a["assigned"] else False
            strip  = "strip-overlap" if is_dup else ("strip-ok" if a["assigned"] else "strip-err")
            row_ex = " overlap" if is_dup else ""

            if not a["assigned"]:      chip_c="chip-none"; chip_t="❌ Sin coche"
            elif src=="preasignado":   chip_c="chip-pre";  chip_t=f"📋 {a['assigned']}"
            elif src=="retorno":       chip_c="chip-ret";  chip_t=f"🔵 {a['assigned']}"
            elif src=="garaje":        chip_c="chip-gar";  chip_t=f"🟠 {a['assigned']}"
            elif src in ("garaje_alt","retorno_alt"): chip_c="chip-alt"; chip_t=f"🟡 {a['assigned']}"
            elif src=="manual":        chip_c="chip-man";  chip_t=f"🟢 {a['assigned']}"
            else:                      chip_c="chip-none"; chip_t="—"

            dup_ch = '<span class="chip chip-dup">⚠️ DUP</span>' if is_dup else ""
            mod_sp = f'<span style="font-size:.65rem;color:#6B7280;margin-left:4px">{a["mod_chip"]}</span>' if a.get("mod_chip") else ""
            note_h = f'<span style="font-size:.65rem;color:#6B7280">{a["note"]}</span>' if a.get("note") else '<span style="color:#E2E8F0;font-size:.65rem">—</span>'
            zona_r = a.get("zona","").upper()
            if "AEROP" in zona_r:   zc="z-aerop"; zl="AEROP"
            elif "SHUTT" in zona_r: zc="z-shutt"; zl="SHUTT"
            else:                    zc="z-other"; zl=zona_r[:6] or "—"
            obs_sp = f'<span style="font-size:.63rem;color:#D97706"> · {a["obs"]}</span>' if a.get("obs") else ""

            st.markdown(f"""
            <div class="res-row{row_ex}">
              <div class="strip {strip}"></div>
              <span class="res-time">{a['hora']}</span>
              <span style="margin-left:10px;min-width:60px"><span class="zona-pill {zc}">{zl}</span></span>
              <span style="margin-left:8px;min-width:195px"><span class="chip {chip_c}">{chip_t}</span>{mod_sp}{dup_ch}</span>
              <span style="margin-left:8px;min-width:155px">{note_h}</span>
              <span style="margin-left:8px;min-width:50px;font-family:monospace;font-size:.72rem;color:#6B7280">#{a['num']}</span>
              <span style="margin-left:auto;font-size:.71rem;color:#9CA3AF;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{a.get('hotel','')} · {a.get('agencia','')}{obs_sp}</span>
            </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    # Manual reassignment
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("✏️ Cambiar asignación manualmente"):
        res_opts = [f"#{i} · {a['hora']} · {a['cat']} · #{a['num']} · {a.get('agencia','')}" for i,a in enumerate(assignments)]
        ch_res   = st.selectbox("Reserva",res_opts,key="man_res")
        res_idx  = res_opts.index(ch_res)
        cur_a    = assignments[res_idx]
        car_opts = ["— Sin cambio —"]+[c["label"] for c in all_cars_sel]
        cur_mat  = cur_a["assigned"]
        cur_car  = next((c["label"] for c in all_cars_sel if c["matricula"]==cur_mat),None)
        def_idx  = car_opts.index(cur_car) if cur_car in car_opts else 0
        ch_car   = st.selectbox("Coche a asignar",car_opts,index=def_idx,key="man_car")
        cb1,cb2  = st.columns(2)
        with cb1:
            if st.button("✅ Confirmar",use_container_width=True,type="primary"):
                if ch_car!="— Sin cambio —":
                    mat=next((c["matricula"] for c in all_cars_sel if c["label"]==ch_car),None)
                    if mat: st.session_state.overrides[res_idx]=mat; st.rerun()
        with cb2:
            if res_idx in st.session_state.overrides:
                if st.button("↩ Restaurar auto",use_container_width=True):
                    del st.session_state.overrides[res_idx]; st.rerun()
        if not cur_a["assigned"] and cur_a.get("sugg"):
            st.warning("Sugerencias:"); [st.markdown(f"· {s}") for s in cur_a["sugg"]]

# ══════════════════════════════════════════
# TAB 2 — TRASLADOS
# ══════════════════════════════════════════
with tab_trucks:
    st.markdown("### 🚛 Gestión de traslados entre bases")
    st.caption("**Salientes** retiran coches de Son Oms. **Entrantes** los añaden (salida + 60 min).")

    with st.expander("➕ Registrar nuevo traslado", expanded=len(st.session_state.traslados)==0):
        ca,cb,cc = st.columns(3)
        with ca: t_cond = st.selectbox("Conductor",CONDUCTORES,key="t_cond")
        with cb: t_dir  = st.radio("Dirección",["Salida de Son Oms →","← Entrada a Son Oms"],key="t_dir",horizontal=True)
        with cc:
            t_hora = st.time_input("Hora salida",value=now.replace(hour=8,minute=0,second=0),key="t_hora")
            t_hora_str = t_hora.strftime("%H:%M")

        is_out = "Salida" in t_dir
        if is_out: t_base=st.selectbox("Base destino",BASES,key="t_base_out")
        else:
            t_base=st.selectbox("Base origen",BASES,key="t_base_in")
            arr=(datetime.combine(now.date(),t_hora)+timedelta(minutes=TRAVEL_MINS)).strftime("%H:%M")
            st.info(f"⏱ Llegada estimada a Son Oms: **{arr}**")

        st.markdown("**Coches en el camión** (hasta 4)")
        t_cars=[]
        for slot in range(4):
            s1,s2,s3=st.columns([1,2,2])
            with s1: tc=st.selectbox(f"Cat.#{slot+1}",["—"]+ALL_CATS,key=f"tc_{slot}")
            with s2: tm=st.text_input(f"Matrícula #{slot+1}",key=f"tm_{slot}",placeholder="0000XXX")
            with s3: tmd=st.text_input(f"Modelo #{slot+1}",key=f"tmd_{slot}",placeholder="Renault Clio")
            if tc!="—" and tm.strip():
                t_cars.append({"cat":tc,"matricula":tm.strip().upper(),"modelo":tmd.strip() or tc})

        if st.button("✅ Añadir traslado",type="primary",use_container_width=True):
            if not t_cars: st.error("Añade al menos 1 coche.")
            else:
                st.session_state.traslados.append({"id":len(st.session_state.traslados),"conductor":t_cond,
                    "direction":"out" if is_out else "in","base":t_base,"hora":t_hora_str,"cars":t_cars})
                st.success(f"✅ {t_cond} · {'Salida' if is_out else 'Entrada'} · {len(t_cars)} coches"); st.rerun()

    st.divider()
    if not st.session_state.traslados:
        st.info("No hay traslados registrados. Usa el formulario de arriba.")
    else:
        n_out_c=len(removed); n_in_c=len(added_cars); n_in_a=sum(1 for ac in added_cars if ac["disponible"])
        c1t,c2t,c3t=st.columns(3)
        with c1t: st.markdown(f'<div class="metric-box crit"><div class="ml">Coches retirados</div><div class="mv crit">{n_out_c}</div><div class="ms">fuera de Son Oms</div></div>',unsafe_allow_html=True)
        with c2t: st.markdown(f'<div class="metric-box purple"><div class="ml">Coches entrantes</div><div class="mv purple">{n_in_c}</div><div class="ms">{n_in_a} ya disponibles</div></div>',unsafe_allow_html=True)
        with c3t:
            net=n_in_a-n_out_c; nc="ok" if net>=0 else "crit"
            st.markdown(f'<div class="metric-box {"neutral" if net==0 else "crit" if net<0 else ""}"><div class="ml">Impacto neto</div><div class="mv {nc}">{("+" if net>0 else "")}{net}</div><div class="ms">sobre inventario</div></div>',unsafe_allow_html=True)
        st.markdown("<br>",unsafe_allow_html=True)
        for i,t in enumerate(st.session_state.traslados):
            io_t=t["direction"]=="out"
            if io_t: hd=f"Son Oms → {t['base']}"
            else:
                arr=arrival_str(t["hora"]); arrived=arrival_dt(t["hora"])<=sim_now
                hd=f"{t['base']} → Son Oms · ~{arr} {'✅ llegó' if arrived else '⏳ pendiente'}"
            st.markdown(f"""<div class="truck-card"><div class="truck-header">
              <span style="font-size:1.1rem">🚛</span>
              <span class="truck-name">{t['conductor']}</span>
              <span class="truck-badge {'truck-out' if io_t else 'truck-in'}">{'🔴 SALIDA →' if io_t else '🟢 ← ENTRADA'}</span>
              <span style="font-size:.77rem;color:#6B7280">{hd}</span>
              <span style="font-size:.7rem;color:#9CA3AF;margin-left:auto">Sal: {t['hora']} · {len(t['cars'])} coches</span>
            </div>""",unsafe_allow_html=True)
            for car in t["cars"]:
                ct="auto" if car["cat"] in CATS_AUTO else "manu"
                st_txt="❌ Retirado" if io_t else ("✅ En Son Oms" if arrival_dt(t["hora"])<=sim_now else f"⏳ Llega {arrival_str(t['hora'])}")
                st.markdown(f"""<div class="traslado-row {'out' if io_t else 'in'}">
                  <span class="cat-badge cat-{car['cat']}">{car['cat']}</span>
                  <span style="font-family:monospace;font-weight:700;font-size:.78rem;min-width:88px">{car['matricula']}</span>
                  <span style="font-size:.78rem;color:#374151">{car['modelo']}</span>
                  <span style="margin-left:auto;font-size:.7rem;color:#6B7280">{st_txt}</span>
                </div>""",unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)
            if st.button(f"🗑 Eliminar #{i+1}",key=f"del_t_{i}"):
                st.session_state.traslados.pop(i); st.rerun()

# ══════════════════════════════════════════
# TAB 3 — TIMELINE
# ══════════════════════════════════════════
with tab_tl:
    st.markdown("### 📅 Línea de tiempo — 11h a 24h")
    st.caption("🔵 Azul = ventana retorno (hora retorno → disponible) · 🔴 Punto rojo = hora de salida · Línea verde = hora actual")

    DAY_S, DAY_E = 11, 24

    def p(hora_str, off=0):
        h,m=map(int,hora_str.split(":"))
        total=h*60+m+off
        return max(0,min(100,(total-DAY_S*60)/((DAY_E-DAY_S)*60)*100))

    # Axis
    hours_axis = list(range(DAY_S, DAY_E+1, 1))
    axis_html='<div style="position:relative;height:18px;min-width:750px;padding-left:50px;margin-bottom:6px">'
    for h in hours_axis:
        pp=(h-DAY_S)/(DAY_E-DAY_S)*100
        axis_html+=f'<span style="position:absolute;left:{pp}%;transform:translateX(-50%);font-size:.58rem;color:#9CA3AF;font-weight:600">{h:02d}h</span>'
    axis_html+='</div>'

    now_p = p(sim_now.strftime("%H:%M"))
    now_line=f'<div class="tl-now" style="left:{now_p}%"><div class="tl-now-lbl">{sim_now.strftime("%H:%M")}</div></div>'

    ret_proc_tl=[]
    for r in RETORNOS:
        if r["matricula"] in removed: continue
        ret_proc_tl.append({**r,"avail_str":avail_str(r["hora"],r["zona"]),"disponible":avail_dt(r["hora"],r["zona"])<=sim_now})
    res_proc_tl=[{**s,"realizada":to_dt(s["hora"])<=sim_now} for s in RESERVAS]

    tl_html='<div class="tl-wrap">'
    tl_html+='<div style="font-size:.76rem;font-weight:700;color:#374151;margin-bottom:10px">Retornos (🔵) y Salidas (🔴) por categoría</div>'
    tl_html+=axis_html

    for cat in ALL_CATS:
        cat_rets=[r for r in ret_proc_tl if r["cat"]==cat]
        cat_sals=[s for s in res_proc_tl if s["cat"]==cat]
        if not cat_rets and not cat_sals: continue

        blocks=""
        for r in cat_rets:
            p1=p(r["hora"]); p2=p(r["avail_str"])
            w=max(1.2,p2-p1)
            mat=r.get("matricula","")[-7:] if r.get("matricula") else r["hora"]
            blocks+=f'<div class="tl-block tl-ret" style="left:{p1}%;width:{w}%" title="{r["modelo"]} · ret {r[\"hora\"]} → disp {r[\"avail_str\"]}">{mat}</div>'
        for s in cat_sals:
            pp=p(s["hora"])
            col="#DC2626" if not s["realizada"] else "#9CA3AF"
            blocks+=f'<div class="tl-block" style="left:{pp}%;width:2.5%;background:#FEE2E2;color:{col};border-color:#FECACA" title="Salida {s[\"hora\"]} · #{s[\"num\"]}">{s["hora"]}</div>'

        tl_html+=f'''<div class="tl-row">
          <span class="tl-cat"><span class="cat-badge cat-{cat}" style="font-size:.6rem;padding:1px 5px">{cat}</span></span>
          <div class="tl-track" style="position:relative;flex:1;margin-left:8px">{now_line}{blocks}</div>
        </div>'''

    tl_html+='</div>'
    st.markdown(tl_html,unsafe_allow_html=True)

    st.markdown("""<div style="display:flex;gap:16px;font-size:.72rem;color:#374151;flex-wrap:wrap;margin-top:6px">
      <span><span style="background:#DBEAFE;border-radius:3px;padding:1px 7px;border:1px solid #BFDBFE">🔵</span> Ventana retorno (llegada → disponible)</span>
      <span><span style="background:#FEE2E2;border-radius:3px;padding:1px 7px;border:1px solid #FECACA">🔴</span> Hora de salida</span>
      <span style="color:#0F6E56;font-weight:700">│ Línea verde = ahora</span>
    </div>""",unsafe_allow_html=True)

st.markdown('<div style="text-align:center;padding:14px 0 4px;font-size:.67rem;color:#9CA3AF">Roig Fleet Manager · Son Oms · 16 Jun 2026</div>',unsafe_allow_html=True)
