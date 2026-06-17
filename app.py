"""
Roig Fleet Manager — v5
+ Mejora 3: Alerta de solapamiento de matrícula
+ Mejora 4: Filtro rápido por estado
+ Mejora 5: Línea de tiempo visual por categoría
+ Mejora 6: Historial de traslados persistente (localStorage via query params trick)
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import io, csv, json

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
    margin-bottom: 16px;
    display: flex; align-items: center; justify-content: space-between;
    box-shadow: 0 4px 16px rgba(15,110,86,0.25);
}
.rfm-header h1 { font-size: 1.1rem; margin:0; font-weight:800; }
.rfm-header .sub { font-size:.72rem; opacity:.7; margin-top:2px; }
.rfm-header .clock { font-size:1.2rem; font-weight:800; font-family:monospace; }
.rfm-header .date  { font-size:.68rem; opacity:.6; text-align:right; margin-top:2px; }

.demo-pill {
    display:inline-block; background:#FEF3C7; color:#92400E;
    border:1px solid #FCD34D; border-radius:20px;
    padding:3px 11px; font-size:.7rem; font-weight:700; margin-bottom:14px;
}

/* Summary bar */
.sum-bar {
    background:white; border:1px solid #E5E7EB; border-radius:10px;
    padding:10px 18px; margin-bottom:12px;
    display:flex; gap:24px; align-items:center; flex-wrap:wrap;
    box-shadow:0 1px 3px rgba(0,0,0,.06);
}
.sum-item { text-align:center; }
.sum-val  { font-size:1.5rem; font-weight:900; line-height:1; }
.sum-lbl  { font-size:.62rem; text-transform:uppercase; letter-spacing:.06em; color:#6B7280; font-weight:700; margin-top:2px; }
.sum-ok   { color:#16A34A; }
.sum-ret  { color:#0284C7; }
.sum-gar  { color:#EA580C; }
.sum-warn { color:#D97706; }
.sum-err  { color:#DC2626; }
.sum-neu  { color:#6B7280; }

/* Filter pills */
.filter-bar {
    display:flex; gap:8px; margin-bottom:14px; flex-wrap:wrap; align-items:center;
}

/* Model group header */
.model-header {
    background:#F8FAFC; border:1px solid #E2E8F0;
    border-radius:8px 8px 0 0; padding:8px 14px;
    margin-top:12px;
    display:flex; align-items:center; gap:10px;
}
.model-name { font-weight:800; font-size:.92rem; color:#0F6E56; }
.cat-badge  { font-size:.75rem; font-weight:800; padding:3px 10px;
              border-radius:6px; display:inline-block; letter-spacing:.02em; }
.cat-auto   { background:#E0F2FE; color:#0284C7; }
.cat-manu   { background:#F0FDF4; color:#166534; }

/* Reservation row */
.res-row {
    display:flex; align-items:center; gap:0;
    border-left:1px solid #E2E8F0; border-right:1px solid #E2E8F0;
    border-bottom:1px solid #E2E8F0;
    padding:7px 14px; font-size:.8rem; background:white;
    transition:background .1s;
}
.res-row:last-child { border-radius:0 0 8px 8px; }
.res-row:hover { background:#FAFAFA; }
.res-row.overlap { background:#FFFBEB !important; }

.strip { width:5px; height:36px; border-radius:3px; flex-shrink:0; margin-right:12px; }
.strip-ok     { background:#16A34A; }
.strip-err    { background:#DC2626; }
.strip-overlap{ background:#D97706; }

.res-time { font-family:monospace; font-weight:700; font-size:.82rem; color:#374151; min-width:52px; }

.zona-pill { font-size:.64rem; font-weight:700; padding:2px 7px; border-radius:4px;
             min-width:52px; text-align:center; display:inline-block; }
.zona-aerop { background:#FEE2E2; color:#991B1B; }
.zona-shutt { background:#E0E7FF; color:#3730A3; }
.zona-other { background:#F3F4F6; color:#374151; }

.chip { font-size:.72rem; font-weight:700; padding:3px 10px; border-radius:20px;
        white-space:nowrap; display:inline-flex; align-items:center; gap:4px; }
.chip-ret  { background:#DBEAFE; color:#1D4ED8; border:1px solid #BFDBFE; }
.chip-gar  { background:#FFEDD5; color:#C2410C; border:1px solid #FED7AA; }
.chip-alt  { background:#FEF3C7; color:#92400E; border:1px solid #FDE68A; }
.chip-none { background:#FEE2E2; color:#991B1B; border:1px solid #FECACA; }
.chip-man  { background:#F0FDF4; color:#166534; border:1px solid #BBF7D0; }
.chip-overlap { background:#FEF3C7; color:#92400E; border:1px solid #FCD34D; font-size:.65rem; padding:2px 6px; margin-left:4px; }

.res-client { font-size:.73rem; color:#6B7280; min-width:130px; }
.res-hotel  { font-size:.71rem; color:#9CA3AF; min-width:120px;
              overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }

/* ── Overlap alert ── */
.overlap-alert {
    background:#FFFBEB; border:1.5px solid #FCD34D; border-radius:8px;
    padding:10px 14px; margin-bottom:12px; font-size:.8rem; color:#92400E;
}
.overlap-alert strong { color:#B45309; }

/* ── Timeline ── */
.tl-wrap {
    background:white; border:1px solid #E5E7EB; border-radius:10px;
    padding:16px; margin-bottom:12px; overflow-x:auto;
    box-shadow:0 1px 3px rgba(0,0,0,.06);
}
.tl-row { display:flex; align-items:center; gap:0; margin-bottom:6px; min-width:700px; }
.tl-cat { font-size:.72rem; font-weight:800; min-width:44px;
          text-align:right; padding-right:10px; color:#374151; }
.tl-track {
    flex:1; height:28px; background:#F1F5F9; border-radius:6px;
    position:relative; overflow:visible;
}
.tl-block {
    position:absolute; height:22px; top:3px;
    border-radius:4px; font-size:.6rem; font-weight:700;
    display:flex; align-items:center; justify-content:center;
    white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
    padding:0 4px; cursor:default;
    border:1px solid rgba(0,0,0,.1);
}
.tl-ret { background:#DBEAFE; color:#1E40AF; }
.tl-sal { background:#FEE2E2; color:#991B1B; }
.tl-gar { background:#FFEDD5; color:#C2410C; }
.tl-hour-line {
    position:absolute; top:0; bottom:0; width:2px;
    background:#0F6E56; z-index:10;
}
.tl-hour-label {
    position:absolute; top:-18px; font-size:.6rem;
    font-weight:700; color:#0F6E56; transform:translateX(-50%);
    white-space:nowrap;
}
.tl-axis { display:flex; min-width:700px; padding-left:54px; margin-bottom:2px; }
.tl-axis-label { font-size:.6rem; color:#9CA3AF; flex:1; text-align:center; }

/* ── Dashboard metrics ── */
.metric-box {
    background:white; border:1px solid #E5E7EB; border-radius:10px;
    padding:14px; text-align:center; border-top:4px solid #0F6E56;
    box-shadow:0 1px 3px rgba(0,0,0,.06);
}
.metric-box.warn    { border-top-color:#D97706; }
.metric-box.crit    { border-top-color:#DC2626; }
.metric-box.neutral { border-top-color:#9CA3AF; }
.metric-box.blue    { border-top-color:#0284C7; }
.metric-box.purple  { border-top-color:#7C3AED; }
.mv { font-size:2rem; font-weight:900; line-height:1; color:#111827; }
.mv.ok     { color:#0F6E56; }
.mv.warn   { color:#D97706; }
.mv.crit   { color:#DC2626; }
.mv.blue   { color:#0284C7; }
.mv.purple { color:#7C3AED; }
.ml { font-size:.66rem; font-weight:700; text-transform:uppercase;
      letter-spacing:.06em; color:#6B7280; margin-bottom:6px; }
.ms { font-size:.7rem; color:#9CA3AF; margin-top:3px; }

/* ── Avail table ── */
.avail-table { width:100%; border-collapse:collapse; font-size:.82rem; }
.avail-table th {
    background:#F1F5F9; padding:9px 12px; text-align:left;
    font-size:.67rem; font-weight:700; text-transform:uppercase;
    letter-spacing:.05em; color:#64748B; border-bottom:2px solid #E2E8F0;
}
.avail-table td { padding:10px 12px; border-bottom:1px solid #F1F5F9; vertical-align:middle; }
.avail-table tr:hover td { background:#F8FAFC; }
.avail-num  { font-size:1.3rem; font-weight:900; }
.avail-ok   { color:#0F6E56; }
.avail-warn { color:#D97706; }
.avail-crit { color:#DC2626; }

/* ── Traslado cards ── */
.truck-card {
    background:white; border:1.5px solid #E5E7EB; border-radius:12px;
    padding:14px 16px; margin-bottom:10px;
    box-shadow:0 1px 4px rgba(0,0,0,.05);
}
.truck-header {
    display:flex; align-items:center; gap:10px;
    margin-bottom:10px; padding-bottom:8px;
    border-bottom:1px solid #F1F5F9;
}
.truck-name  { font-size:.95rem; font-weight:800; color:#111827; }
.truck-badge { font-size:.72rem; font-weight:700; padding:3px 10px; border-radius:20px; }
.truck-out   { background:#FEE2E2; color:#991B1B; border:1px solid #FECACA; }
.truck-in    { background:#D1FAE5; color:#065F46; border:1px solid #A7F3D0; }
.traslado-row {
    display:flex; align-items:center; gap:10px;
    padding:5px 8px; border-radius:6px; font-size:.78rem;
    margin-bottom:3px; background:#F9FAFB;
}
.traslado-row.out { border-left:4px solid #DC2626; }
.traslado-row.in  { border-left:4px solid #16A34A; }

.impact-banner {
    background:#FFF7ED; border:1px solid #FED7AA;
    border-radius:8px; padding:9px 14px;
    font-size:.78rem; color:#92400E; margin-bottom:12px;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap:3px; background:#F1F5F9; padding:4px; border-radius:10px; margin-bottom:16px;
}
.stTabs [data-baseweb="tab"] { border-radius:7px !important; font-weight:700 !important; }
.stTabs [aria-selected="true"] { background:white !important; box-shadow:0 1px 3px rgba(0,0,0,.1) !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────
CATS_AUTO  = ["BA","CA","KA","HA","FA"]
CATS_MANU  = ["A","B","C"]
ALL_CATS   = CATS_AUTO + CATS_MANU
CAT_LABELS = {
    "BA":"Automático pequeño","CA":"Automático compacto",
    "KA":"Automático mediano","HA":"Automático SUV",
    "FA":"Automático familiar","A":"Manual pequeño",
    "B":"Manual compacto","C":"Manual mediano",
}
ZONA_OFFSET = {"AEROP":60,"SHUTT":45}
BASES       = ["Cala d'Or","Calas","Cala Millor","Alcudia"]
CONDUCTORES = ["LOMBA","JOSE","DIEGO"]
TRAVEL_MINS = 60

# ─────────────────────────────────────────
# DEMO DATA
# ─────────────────────────────────────────
DEMO_GARAJE = [
    {"cat":"BA","modelo":"Seat Ibiza Auto",     "matricula":"4523 MLL"},
    {"cat":"BA","modelo":"Seat Ibiza Auto",     "matricula":"7821 PKR"},
    {"cat":"BA","modelo":"Opel Corsa Auto",     "matricula":"3190 HBT"},
    {"cat":"BA","modelo":"VW Polo Auto",        "matricula":"9902 DFS"},
    {"cat":"CA","modelo":"Seat León Auto",      "matricula":"6614 NMW"},
    {"cat":"CA","modelo":"Seat León Auto",      "matricula":"1147 QVX"},
    {"cat":"CA","modelo":"Toyota Corolla Auto", "matricula":"2255 RPK"},
    {"cat":"KA","modelo":"VW Tiguan Auto",      "matricula":"7709 MXQ"},
    {"cat":"KA","modelo":"Hyundai Tucson Auto", "matricula":"3348 LVZ"},
    {"cat":"HA","modelo":"Seat Tarraco Auto",   "matricula":"1123 WKF"},
    {"cat":"HA","modelo":"VW Touareg Auto",     "matricula":"5580 ZZA"},
    {"cat":"FA","modelo":"Ford Galaxy Auto",    "matricula":"9934 CPM"},
    {"cat":"A", "modelo":"Seat Ibiza",          "matricula":"8801 TRE"},
    {"cat":"A", "modelo":"Opel Corsa",          "matricula":"4412 QQM"},
    {"cat":"B", "modelo":"Seat León",           "matricula":"6630 BNK"},
    {"cat":"B", "modelo":"Ford Focus",          "matricula":"8830 JTL"},
    {"cat":"C", "modelo":"Dacia Duster",        "matricula":"5571 CBN"},
]

DEMO_RETORNOS = [
    {"hora":"07:30","cat":"BA","modelo":"Seat Ibiza Auto",     "matricula":"1198 ZZT","zona":"AEROP"},
    {"hora":"08:00","cat":"A", "modelo":"Seat Ibiza",          "matricula":"4456 KLM","zona":"SHUTT"},
    {"hora":"08:45","cat":"CA","modelo":"Seat León Auto",      "matricula":"7723 OPQ","zona":"AEROP"},
    {"hora":"09:15","cat":"C", "modelo":"Dacia Duster",        "matricula":"3381 RST","zona":"OFICINA"},
    {"hora":"10:00","cat":"CA","modelo":"Toyota Corolla Auto", "matricula":"6690 UVW","zona":"SHUTT"},
    {"hora":"10:30","cat":"KA","modelo":"Hyundai Tucson Auto", "matricula":"8812 XYZ","zona":"AEROP"},
    {"hora":"11:00","cat":"B", "modelo":"Ford Focus",          "matricula":"2234 ABC","zona":"OFICINA"},
    {"hora":"12:00","cat":"BA","modelo":"Opel Corsa Auto",     "matricula":"5567 DEF","zona":"AEROP"},
    {"hora":"13:30","cat":"KA","modelo":"VW Tiguan Auto",      "matricula":"9901 GHI","zona":"SHUTT"},
    {"hora":"14:00","cat":"BA","modelo":"Seat Ibiza Auto",     "matricula":"1145 JKL","zona":"AEROP"},
    {"hora":"15:30","cat":"HA","modelo":"Seat Tarraco Auto",   "matricula":"4478 MNO","zona":"OFICINA"},
    {"hora":"16:00","cat":"FA","modelo":"Ford Galaxy Auto",    "matricula":"7712 PQR","zona":"AEROP"},
    {"hora":"17:00","cat":"B", "modelo":"Seat León",           "matricula":"3345 STU","zona":"SHUTT"},
    {"hora":"18:30","cat":"CA","modelo":"Seat León Auto",      "matricula":"6678 VWX","zona":"AEROP"},
    {"hora":"19:00","cat":"A", "modelo":"Opel Corsa",          "matricula":"9923 YZA","zona":"OFICINA"},
]

DEMO_RESERVAS = [
    {"hora":"07:00","cat":"BA","cliente":"García López, M.", "agencia":"OFFUGO","hotel":"1504"},
    {"hora":"07:30","cat":"BA","cliente":"Müller, H.",       "agencia":"SHUTT", "hotel":"1501 Solier Garden"},
    {"hora":"08:00","cat":"C", "cliente":"Smith, J.",        "agencia":"GARAJE","hotel":"1504"},
    {"hora":"08:30","cat":"CA","cliente":"Martínez, A.",     "agencia":"AEROP", "hotel":"1504"},
    {"hora":"09:00","cat":"KA","cliente":"Rossi, G.",        "agencia":"AEROP", "hotel":"1504"},
    {"hora":"09:30","cat":"B", "cliente":"Dupont, C.",       "agencia":"OFFUGO","hotel":"1504"},
    {"hora":"10:00","cat":"CA","cliente":"Fernández, R.",    "agencia":"SHUTT", "hotel":"1501 Casa Rural"},
    {"hora":"10:30","cat":"BA","cliente":"Williams, T.",     "agencia":"AEROP", "hotel":"1504"},
    {"hora":"11:00","cat":"KA","cliente":"Sánchez, P.",      "agencia":"OFFUGO","hotel":"1504"},
    {"hora":"12:00","cat":"BA","cliente":"Johnson, K.",      "agencia":"AEROP", "hotel":"1501 Barceló"},
    {"hora":"13:00","cat":"HA","cliente":"Nakamura, Y.",     "agencia":"SHUTT", "hotel":"1504"},
    {"hora":"13:00","cat":"BA","cliente":"Pérez, L.",        "agencia":"AEROP", "hotel":"1504"},
    {"hora":"14:00","cat":"CA","cliente":"Brown, A.",        "agencia":"OFFUGO","hotel":"1501 Iberostar"},
    {"hora":"15:00","cat":"HA","cliente":"González, C.",     "agencia":"AEROP", "hotel":"1504"},
    {"hora":"16:00","cat":"FA","cliente":"Hoffmann, E.",     "agencia":"SHUTT", "hotel":"1501 Primasol"},
    {"hora":"17:00","cat":"A", "cliente":"López, S.",        "agencia":"AEROP", "hotel":"1504"},
    {"hora":"18:00","cat":"BA","cliente":"Davies, R.",       "agencia":"OFFUGO","hotel":"1504"},
    {"hora":"19:00","cat":"C", "cliente":"Moreau, F.",       "agencia":"AEROP", "hotel":"1504"},
    {"hora":"20:00","cat":"B", "cliente":"Schmidt, K.",      "agencia":"SHUTT", "hotel":"1501 Leonardo"},
    {"hora":"20:30","cat":"KA","cliente":"Tanaka, H.",       "agencia":"AEROP", "hotel":"1504"},
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

def hora_to_frac(hora_str):
    """Convert HH:MM to fraction of day [0,1]"""
    h, m = map(int, hora_str.split(":"))
    return (h * 60 + m) / (24 * 60)

# ─────────────────────────────────────────
# OVERLAP DETECTOR (Mejora 3)
# ─────────────────────────────────────────
def detect_overlaps(assignments):
    """Return set of matriculas assigned more than once"""
    mat_count = {}
    for a in assignments:
        if a["assigned"]:
            mat_count[a["assigned"]] = mat_count.get(a["assigned"], 0) + 1
    return {m for m, c in mat_count.items() if c > 1}

# ─────────────────────────────────────────
# TRASLADO IMPACT
# ─────────────────────────────────────────
def compute_traslado_impacts(traslados, sim_now):
    removed_plates = set()
    added_cars     = []
    for t in traslados:
        if t["direction"] == "out":
            for car in t["cars"]:
                if car["matricula"]: removed_plates.add(car["matricula"])
        else:
            arr_dt  = arrival_dt(t["hora"])
            arr_s   = arr_dt.strftime("%H:%M")
            avail   = arr_dt <= sim_now
            for car in t["cars"]:
                if car["cat"] and car["matricula"]:
                    added_cars.append({
                        "cat": car["cat"], "modelo": car.get("modelo", car["cat"]),
                        "matricula": car["matricula"],
                        "avail_dt": arr_dt, "avail_str": arr_s,
                        "disponible": avail,
                        "conductor": t["conductor"], "base": t["base"],
                    })
    return removed_plates, added_cars

# ─────────────────────────────────────────
# ASSIGNMENT ENGINE
# ─────────────────────────────────────────
def auto_assign(reservas, garaje, retornos, sim_now, removed_plates, added_cars):
    garaje_pool = [dict(c, used=False) for c in garaje if c["matricula"] not in removed_plates]
    ret_pool    = []
    for r in retornos:
        if r["matricula"] in removed_plates: continue
        av = avail_dt(r["hora"], r["zona"])
        ret_pool.append(dict(r, avail_dt=av, avail_str=avail_str(r["hora"], r["zona"]), used=False))
    for ac in added_cars:
        if ac["disponible"]:
            garaje_pool.append({"cat":ac["cat"],"modelo":ac["modelo"],"matricula":ac["matricula"],"used":False})
        else:
            ret_pool.append({"cat":ac["cat"],"modelo":ac["modelo"],"matricula":ac["matricula"],
                             "avail_dt":ac["avail_dt"],"avail_str":ac["avail_str"],
                             "zona":"TRASLADO","hora":ac["avail_str"],"used":False})

    assignments = []
    for res in reservas:
        res_dt = to_dt(res["hora"])
        cat    = res["cat"]
        assigned = source = None
        note = ""; modelo_chip = ""; alt_sugg = []

        # 1. Return exact cat
        cands = sorted([r for r in ret_pool if not r["used"] and r["cat"]==cat and r["avail_dt"]<=res_dt],
                       key=lambda x: x["avail_dt"])
        if cands:
            r2=cands[0]; r2["used"]=True
            assigned=r2["matricula"]; source="retorno"; modelo_chip=r2["modelo"]
            note=f"Retorno {r2['hora']} · zona {r2.get('zona','—')} · disp. {r2['avail_str']}"

        # 2. Garaje exact cat
        if not assigned:
            for c in garaje_pool:
                if not c["used"] and c["cat"]==cat:
                    c["used"]=True; assigned=c["matricula"]; source="garaje"; modelo_chip=c["modelo"]; break

        # 3. Garaje adjacent cat
        if not assigned:
            cat_idx = ALL_CATS.index(cat) if cat in ALL_CATS else -1
            for c in garaje_pool:
                if not c["used"] and c["cat"] in ALL_CATS and ALL_CATS.index(c["cat"])==cat_idx+1:
                    c["used"]=True; assigned=c["matricula"]; source="garaje_alt"
                    modelo_chip=c["modelo"]; note=f"Alt: {c['cat']} ({c['modelo']})"; break

        # 4. Return adjacent cat
        if not assigned:
            cat_idx = ALL_CATS.index(cat) if cat in ALL_CATS else -1
            cands = sorted([r for r in ret_pool
                            if not r["used"] and r["cat"] in ALL_CATS
                            and ALL_CATS.index(r["cat"])==cat_idx+1
                            and r["avail_dt"]<=res_dt], key=lambda x: x["avail_dt"])
            if cands:
                r2=cands[0]; r2["used"]=True
                assigned=r2["matricula"]; source="retorno_alt"; modelo_chip=r2["modelo"]
                note=f"Alt. {r2['cat']} ({r2['modelo']}) · disp. {r2['avail_str']}"

        if not assigned:
            for c in garaje_pool:
                if not c["used"]:
                    alt_sugg.append(f"{c['cat']} · {c['modelo']} · {c['matricula']} (garaje)")
                    if len(alt_sugg)>=3: break
            if len(alt_sugg)<3:
                for r2 in ret_pool:
                    if not r2["used"]:
                        alt_sugg.append(f"{r2['cat']} · {r2['modelo']} · {r2['matricula']} (ret {r2.get('hora','—')}→{r2['avail_str']})")
                        if len(alt_sugg)>=3: break

        assignments.append({
            "hora":res["hora"],"cat":cat,"cliente":res["cliente"],
            "agencia":res.get("agencia",""),"hotel":res.get("hotel",""),
            "assigned":assigned,"source":source,"note":note,
            "sugg":alt_sugg,"modelo_chip":modelo_chip,
        })
    return assignments, garaje_pool, ret_pool

# ─────────────────────────────────────────
# TIMELINE BUILDER (Mejora 5)
# ─────────────────────────────────────────
DAY_START = 6   # 06:00
DAY_END   = 23  # 23:00
DAY_MINS  = (DAY_END - DAY_START) * 60

def pct(hora_str, offset_mins=0):
    """Convert time string to % position on timeline"""
    h, m = map(int, hora_str.split(":"))
    total = h*60 + m + offset_mins
    start = DAY_START * 60
    return max(0, min(100, (total - start) / DAY_MINS * 100))

def render_timeline(ret_proc, res_proc, sim_now, added_cars):
    """Render SVG-like timeline using HTML/CSS"""
    # Hour axis
    hours = list(range(DAY_START, DAY_END+1, 2))
    axis_html = '<div class="tl-axis">'
    for h in hours:
        p = (h - DAY_START) / (DAY_END - DAY_START) * 100
        axis_html += f'<span class="tl-axis-label" style="position:absolute;left:{p}%;transform:translateX(-50%)">{h:02d}h</span>'
    axis_html = f'<div style="position:relative;height:16px;min-width:700px;padding-left:54px;margin-bottom:4px">{axis_html}</div>'

    now_pct = pct(sim_now.strftime("%H:%M"))
    now_line = f'<div class="tl-hour-line" style="left:{now_pct}%"><div class="tl-hour-label">{sim_now.strftime("%H:%M")}</div></div>'

    html = '<div class="tl-wrap">'
    html += "<div style='font-size:.75rem;font-weight:700;color:#374151;margin-bottom:10px'>📅 Línea de tiempo del día — Retornos (🔵) vs Salidas (🔴)</div>"
    html += axis_html

    for cat in ALL_CATS:
        cat_rets = [r for r in ret_proc if r["cat"]==cat]
        cat_sals = [s for s in res_proc if s["cat"]==cat]
        cat_adds = [ac for ac in added_cars if ac["cat"]==cat]
        if not cat_rets and not cat_sals and not cat_adds: continue

        cat_type = "auto" if cat in CATS_AUTO else "manu"
        blocks = ""

        # Retornos (disponibles = green, pending = blue)
        for r in cat_rets:
            p_start = pct(r["hora"])
            p_avail = pct(r["avail_str"])
            width   = max(1.5, p_avail - p_start)
            mat     = r.get("matricula","")
            blocks += f'<div class="tl-block tl-ret" style="left:{p_start}%;width:{width}%" title="Retorno {r[\"hora\"]} → disp. {r[\"avail_str\"]} · {mat}">{mat[-7:] if mat else r["hora"]}</div>'

        # Incoming transfers
        for ac in cat_adds:
            p = pct(ac["avail_str"])
            blocks += f'<div class="tl-block" style="left:{p}%;width:3%;background:#EDE9FE;color:#6D28D9;border-color:#C4B5FD" title="Traslado entrada {ac[\"avail_str\"]} · {ac[\"matricula\"]}">{ac["matricula"][-7:]}</div>'

        # Salidas
        for s in cat_sals:
            p = pct(s["hora"])
            blocks += f'<div class="tl-block tl-sal" style="left:{p}%;width:3%" title="Salida {s[\"hora\"]} · {s[\"cliente\"]}">{s["hora"]}</div>'

        html += f'''
        <div class="tl-row">
          <span class="tl-cat"><span class="cat-badge cat-{cat_type}" style="font-size:.62rem;padding:2px 6px">{cat}</span></span>
          <div class="tl-track" style="position:relative;flex:1;margin-left:10px">
            {now_line}
            {blocks}
          </div>
        </div>'''

    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

# ─────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────
now = datetime.now()
defaults = {
    "sim_h":now.hour,"sim_m":now.minute,"use_sim":False,
    "threshold":2,"overrides":{},"filter_state":"todos",
    "traslados":[],   # Mejora 6: persists in session
}
for k,v in defaults.items():
    if k not in st.session_state: st.session_state[k] = v

sim_now = now.replace(hour=st.session_state.sim_h,minute=st.session_state.sim_m,second=0) \
    if st.session_state.use_sim else now

# ─────────────────────────────────────────
# COMPUTE
# ─────────────────────────────────────────
removed_plates, added_cars = compute_traslado_impacts(st.session_state.traslados, sim_now)
base_asgn, gp, rp = auto_assign(DEMO_RESERVAS, DEMO_GARAJE, DEMO_RETORNOS, sim_now, removed_plates, added_cars)

all_cars_sel = []
for c in DEMO_GARAJE:
    if c["matricula"] not in removed_plates:
        all_cars_sel.append({"label":f"[{c['cat']}] {c['matricula']} — {c['modelo']} · GARAJE","matricula":c["matricula"],"cat":c["cat"]})
for r in DEMO_RETORNOS:
    if r["matricula"] not in removed_plates:
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
            assignments.append({**a,"assigned":mat,"source":"manual",
                                 "note":f"Manual · {car['label'].split('·')[1].strip() if '·' in car['label'] else ''}"})
            continue
    assignments.append(a)

# Mejora 3: detect overlaps
overlapped_plates = detect_overlaps(assignments)

# ─────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────
st.markdown(f"""
<div class="rfm-header">
  <div>
    <h1>🚗 Roig Fleet Manager</h1>
    <div class="sub">Roig Rent a Car · ROIG · HASSO · AVIS · MARASON</div>
  </div>
  <div>
    <div class="clock">{now.strftime('%H:%M:%S')}</div>
    <div class="date">{now.strftime('%d %b %Y').upper()}</div>
  </div>
</div>
<div class="demo-pill">🎯 MODO DEMO — datos de ejemplo · En producción se cargan desde PDFs con IA</div>
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
    st.markdown("🔵 Azul = retorno")
    st.markdown("🟠 Naranja = garaje")
    st.markdown("🟡 Amarillo = alternativa")
    st.markdown("🔴 Rojo = sin coche")
    st.markdown("⚠️ Borde amarillo = matrícula duplicada")

# ─────────────────────────────────────────
# TABS
# ─────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📋  Asignación de reservas",
    "🚛  Traslados",
    "📅  Línea de tiempo",
    "📊  Stock disponible",
])

# ══════════════════════════════════════════
# TAB 1 — RESERVATIONS
# ══════════════════════════════════════════
with tab1:

    n_ret = sum(1 for a in assignments if a["source"]=="retorno")
    n_gar = sum(1 for a in assignments if a["source"]=="garaje")
    n_alt = sum(1 for a in assignments if a["source"] in ("garaje_alt","retorno_alt"))
    n_man = sum(1 for a in assignments if a["source"]=="manual")
    n_err = sum(1 for a in assignments if not a["assigned"])
    n_dup = len(overlapped_plates)

    # Overlap alert (Mejora 3)
    if overlapped_plates:
        overlap_list = ", ".join(sorted(overlapped_plates))
        st.markdown(f"""<div class="overlap-alert">
            ⚠️ <strong>Atención — matrícula duplicada:</strong>
            Los siguientes coches aparecen asignados a más de una reserva:
            <strong>{overlap_list}</strong> — revisa y reasigna manualmente.
        </div>""", unsafe_allow_html=True)

    if removed_plates or added_cars:
        parts=[]
        if removed_plates: parts.append(f"🚛 {len(removed_plates)} coches en traslado saliente")
        if added_cars:     parts.append(f"🟣 {len(added_cars)} entrantes ({sum(1 for ac in added_cars if ac['disponible'])} disponibles)")
        st.markdown(f'<div class="impact-banner">{"&nbsp;&nbsp;·&nbsp;&nbsp;".join(parts)}</div>',unsafe_allow_html=True)

    # Summary bar
    st.markdown(f"""
    <div class="sum-bar">
      <div class="sum-item"><div class="sum-val sum-ok">{n_gar+n_ret+n_man}</div><div class="sum-lbl">🟢 Cubiertas</div></div>
      <div class="sum-item"><div class="sum-val sum-ret">{n_ret}</div><div class="sum-lbl">🔵 Retorno</div></div>
      <div class="sum-item"><div class="sum-val sum-gar">{n_gar}</div><div class="sum-lbl">🟠 Garaje</div></div>
      <div class="sum-item"><div class="sum-val sum-warn">{n_alt}</div><div class="sum-lbl">🟡 Alt.</div></div>
      <div class="sum-item"><div class="sum-val sum-err">{n_err}</div><div class="sum-lbl">🔴 Sin coche</div></div>
      <div class="sum-item"><div class="sum-val" style="color:{'#D97706' if n_dup>0 else '#6B7280'}">{n_dup}</div><div class="sum-lbl">⚠️ Duplicadas</div></div>
      <div class="sum-item"><div class="sum-val sum-neu">{len(assignments)}</div><div class="sum-lbl">Total</div></div>
    </div>
    """, unsafe_allow_html=True)

    # Mejora 4: Filter pills
    st.markdown("**Filtrar por estado:**")
    fcols = st.columns(6)
    filters = [
        ("todos",    "📋 Todos",        len(assignments)),
        ("ok",       "🟢 Cubiertas",    n_gar+n_ret+n_man),
        ("retorno",  "🔵 Retorno",      n_ret),
        ("garaje",   "🟠 Garaje",       n_gar),
        ("sin_coche","🔴 Sin coche",    n_err),
        ("overlap",  "⚠️ Duplicadas",   n_dup),
    ]
    for col,(fkey,flabel,fcount) in zip(fcols, filters):
        with col:
            is_active = st.session_state.filter_state == fkey
            btn_type  = "primary" if is_active else "secondary"
            if st.button(f"{flabel} ({fcount})", key=f"f_{fkey}", use_container_width=True, type=btn_type):
                st.session_state.filter_state = fkey; st.rerun()

    # Apply filter
    def apply_filter(asgn_list, fstate, overlap_plates):
        if fstate == "todos":     return asgn_list
        if fstate == "ok":        return [a for a in asgn_list if a["assigned"] and a["source"] not in ("garaje_alt","retorno_alt")]
        if fstate == "retorno":   return [a for a in asgn_list if a["source"]=="retorno"]
        if fstate == "garaje":    return [a for a in asgn_list if a["source"]=="garaje"]
        if fstate == "sin_coche": return [a for a in asgn_list if not a["assigned"]]
        if fstate == "overlap":   return [a for a in asgn_list if a["assigned"] in overlap_plates]
        return asgn_list

    filtered = apply_filter(assignments, st.session_state.filter_state, overlapped_plates)

    if not filtered:
        st.info("No hay reservas que coincidan con el filtro seleccionado.")
    else:
        from collections import OrderedDict
        groups = OrderedDict()
        for cat in ALL_CATS:
            cat_asgn = [a for a in filtered if a["cat"]==cat]
            if cat_asgn: groups[cat] = cat_asgn

        for cat, cat_asgns in groups.items():
            cat_type  = "auto" if cat in CATS_AUTO else "manu"
            type_icon = "⚙️" if cat in CATS_AUTO else "🔧"
            n_ok_c    = sum(1 for a in cat_asgns if a["assigned"])
            n_err_c   = sum(1 for a in cat_asgns if not a["assigned"])
            err_html  = f'<span style="color:#DC2626;font-weight:700">{n_err_c} sin coche</span>' if n_err_c else "0 sin coche"
            n_dup_c   = sum(1 for a in cat_asgns if a["assigned"] in overlapped_plates)
            dup_html  = f'&nbsp;·&nbsp;<span style="color:#D97706;font-weight:700">⚠️ {n_dup_c} duplicada(s)</span>' if n_dup_c else ""

            st.markdown(f"""
            <div class="model-header">
              <span>{type_icon}</span>
              <span class="model-name">{cat}</span>
              <span class="cat-badge cat-{cat_type}">{CAT_LABELS.get(cat,cat)}</span>
              <span style="font-size:.72rem;color:#6B7280;margin-left:auto">
                {n_ok_c} cubiertas · {err_html}{dup_html} · {len(cat_asgns)} reservas
              </span>
            </div>""", unsafe_allow_html=True)

            st.markdown("""<div style="display:flex;background:#F8FAFC;padding:5px 14px 5px 31px;
                border-left:1px solid #E2E8F0;border-right:1px solid #E2E8F0;
                font-size:.63rem;font-weight:700;text-transform:uppercase;
                letter-spacing:.05em;color:#94A3B8;">
              <span style="min-width:52px">Hora</span>
              <span style="min-width:64px;margin-left:12px">Zona</span>
              <span style="min-width:200px;margin-left:8px">Coche asignado</span>
              <span style="min-width:160px;margin-left:8px">Detalle</span>
              <span style="min-width:130px;margin-left:8px">Cliente</span>
              <span style="margin-left:auto">Hotel</span>
            </div>""", unsafe_allow_html=True)

            for i_g, a in [(j,x) for j,x in enumerate(assignments) if x["cat"]==cat and x in filtered]:
                src = a["source"] or ""
                is_dup = a["assigned"] in overlapped_plates if a["assigned"] else False
                strip_cls = "strip-overlap" if is_dup else ("strip-ok" if a["assigned"] else "strip-err")
                row_extra = " overlap" if is_dup else ""

                if not a["assigned"]:  chip_cls="chip-none"; chip_txt="❌ Sin coche"
                elif src=="retorno":   chip_cls="chip-ret";  chip_txt=f"🔵 {a['assigned']}"
                elif src=="garaje":    chip_cls="chip-gar";  chip_txt=f"🟠 {a['assigned']}"
                elif src in ("garaje_alt","retorno_alt"): chip_cls="chip-alt"; chip_txt=f"🟡 {a['assigned']}"
                elif src=="manual":    chip_cls="chip-man";  chip_txt=f"🟢 {a['assigned']}"
                else:                  chip_cls="chip-none"; chip_txt="—"

                dup_chip = '<span class="chip chip-overlap">⚠️ DUPLICADA</span>' if is_dup else ""
                mod_span = f'<span style="font-size:.67rem;color:#6B7280;margin-left:5px">{a["modelo_chip"]}</span>' if a.get("modelo_chip") else ""
                note_html = f'<span style="font-size:.67rem;color:#6B7280">{a["note"]}</span>' if a["note"] else '<span style="color:#CBD5E1;font-size:.67rem">—</span>'

                zona_raw=a.get("agencia","").upper()
                if "AEROP" in zona_raw:   zona_cls="zona-aerop"; zona_lbl="AEROP"
                elif "SHUTT" in zona_raw: zona_cls="zona-shutt"; zona_lbl="SHUTT"
                else:                      zona_cls="zona-other"; zona_lbl=zona_raw[:6] or "—"

                st.markdown(f"""
                <div class="res-row{row_extra}">
                  <div class="strip {strip_cls}"></div>
                  <span class="res-time">{a['hora']}</span>
                  <span style="margin-left:12px;min-width:64px"><span class="zona-pill {zona_cls}">{zona_lbl}</span></span>
                  <span style="margin-left:8px;min-width:200px">
                    <span class="chip {chip_cls}">{chip_txt}</span>{mod_span}{dup_chip}
                  </span>
                  <span style="margin-left:8px;min-width:160px">{note_html}</span>
                  <span class="res-client" style="margin-left:8px">{a['cliente']}</span>
                  <span class="res-hotel">{a.get('hotel','')}</span>
                </div>""", unsafe_allow_html=True)

            st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    # Manual reassignment
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("✏️ Cambiar asignación manualmente"):
        res_opts  = [f"#{i} · {a['hora']} · {a['cat']} · {a['cliente']}" for i,a in enumerate(assignments)]
        ch_res    = st.selectbox("Reserva",res_opts,key="man_res")
        res_idx   = res_opts.index(ch_res)
        cur_a     = assignments[res_idx]
        car_opts  = ["— Sin cambio —"]+[c["label"] for c in all_cars_sel]
        cur_mat   = cur_a["assigned"]
        cur_car   = next((c["label"] for c in all_cars_sel if c["matricula"]==cur_mat),None)
        def_idx   = car_opts.index(cur_car) if cur_car in car_opts else 0
        ch_car    = st.selectbox("Coche a asignar",car_opts,index=def_idx,key="man_car")
        cb1,cb2   = st.columns(2)
        with cb1:
            if st.button("✅ Confirmar",use_container_width=True,type="primary"):
                if ch_car!="— Sin cambio —":
                    mat=next((c["matricula"] for c in all_cars_sel if c["label"]==ch_car),None)
                    if mat: st.session_state.overrides[res_idx]=mat; st.rerun()
        with cb2:
            if res_idx in st.session_state.overrides:
                if st.button("↩ Restaurar auto",use_container_width=True):
                    del st.session_state.overrides[res_idx]; st.rerun()
        if not cur_a["assigned"] and cur_a["sugg"]:
            st.warning("Sin coche. Sugerencias:"); [st.markdown(f"· {s}") for s in cur_a["sugg"]]

# ══════════════════════════════════════════
# TAB 2 — TRASLADOS (Mejora 6: persists in session)
# ══════════════════════════════════════════
with tab2:
    st.markdown("### 🚛 Gestión de traslados entre bases")
    st.caption("**Salientes** retiran coches del inventario de Son Oms. **Entrantes** los añaden cuando llegan (salida + 60 min). Los traslados se mantienen durante toda la sesión.")

    with st.expander("➕ Registrar nuevo traslado", expanded=len(st.session_state.traslados)==0):
        ca,cb,cc = st.columns(3)
        with ca: t_cond = st.selectbox("Conductor",CONDUCTORES,key="t_cond")
        with cb: t_dir  = st.radio("Dirección",["Salida de Son Oms →","← Entrada a Son Oms"],key="t_dir",horizontal=True)
        with cc:
            t_hora = st.time_input("Hora de salida",value=now.replace(hour=8,minute=0,second=0),key="t_hora")
            t_hora_str = t_hora.strftime("%H:%M")

        is_out = "Salida" in t_dir
        if is_out:
            t_base = st.selectbox("Base destino",BASES,key="t_base_out")
        else:
            t_base = st.selectbox("Base origen",BASES,key="t_base_in")
            arr=(datetime.combine(now.date(),t_hora)+timedelta(minutes=TRAVEL_MINS)).strftime("%H:%M")
            st.info(f"⏱ Llegada estimada a Son Oms: **{arr}**")

        st.markdown("**Coches en el camión** (hasta 4)")
        t_cars=[]
        for slot in range(4):
            s1,s2,s3=st.columns([1,2,2])
            with s1: tc=st.selectbox(f"Cat.#{slot+1}",["—"]+ALL_CATS,key=f"tc_{slot}")
            with s2: tm=st.text_input(f"Matrícula #{slot+1}",key=f"tm_{slot}",placeholder="0000 XXX")
            with s3: tmd=st.text_input(f"Modelo #{slot+1}",key=f"tmd_{slot}",placeholder="Seat Ibiza")
            if tc!="—" and tm.strip():
                t_cars.append({"cat":tc,"matricula":tm.strip().upper(),"modelo":tmd.strip() or tc})

        if st.button("✅ Añadir traslado",type="primary",use_container_width=True):
            if not t_cars: st.error("Añade al menos 1 coche.")
            else:
                st.session_state.traslados.append({
                    "id":len(st.session_state.traslados),
                    "conductor":t_cond,"direction":"out" if is_out else "in",
                    "base":t_base,"hora":t_hora_str,"cars":t_cars,
                })
                st.success(f"✅ {t_cond} · {'Salida' if is_out else 'Entrada'} · {len(t_cars)} coches")
                st.rerun()

    st.divider()

    if not st.session_state.traslados:
        st.info("No hay traslados registrados. Usa el formulario de arriba.")
    else:
        n_out_c=len(removed_plates); n_in_c=len(added_cars); n_in_a=sum(1 for ac in added_cars if ac["disponible"])
        c1t,c2t,c3t=st.columns(3)
        with c1t:
            st.markdown(f'<div class="metric-box crit"><div class="ml">Coches retirados</div><div class="mv crit">{n_out_c}</div><div class="ms">salidas Son Oms</div></div>',unsafe_allow_html=True)
        with c2t:
            st.markdown(f'<div class="metric-box purple"><div class="ml">Coches entrantes</div><div class="mv purple">{n_in_c}</div><div class="ms">{n_in_a} ya disponibles</div></div>',unsafe_allow_html=True)
        with c3t:
            net=n_in_a-n_out_c; nc="ok" if net>=0 else "crit"
            st.markdown(f'<div class="metric-box {"neutral" if net==0 else "crit" if net<0 else ""}"><div class="ml">Impacto neto ahora</div><div class="mv {nc}">{("+" if net>0 else "")}{net}</div><div class="ms">sobre inventario</div></div>',unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        for i,t in enumerate(st.session_state.traslados):
            is_out_t=t["direction"]=="out"
            dir_b="truck-out" if is_out_t else "truck-in"
            dir_l="🔴 SALIDA →" if is_out_t else "🟢 ← ENTRADA"
            if is_out_t: hdet=f"Son Oms → {t['base']}"
            else:
                arr=arrival_str(t["hora"]); arrived=arrival_dt(t["hora"])<=sim_now
                hdet=f"{t['base']} → Son Oms · llega ~{arr} {'✅ llegó' if arrived else '⏳ pendiente'}"
            st.markdown(f"""<div class="truck-card">
              <div class="truck-header">
                <span style="font-size:1.2rem">🚛</span>
                <span class="truck-name">{t['conductor']}</span>
                <span class="truck-badge {dir_b}">{dir_l}</span>
                <span style="font-size:.78rem;color:#6B7280">{hdet}</span>
                <span style="font-size:.72rem;color:#9CA3AF;margin-left:auto">Salida: {t['hora']} · {len(t['cars'])} coches</span>
              </div>""", unsafe_allow_html=True)
            for car in t["cars"]:
                rc="out" if is_out_t else "in"
                ct="auto" if car["cat"] in CATS_AUTO else "manu"
                status="❌ Retirado" if is_out_t else (f"✅ En Son Oms" if arrival_dt(t["hora"])<=sim_now else f"⏳ Llega {arrival_str(t['hora'])}")
                st.markdown(f"""<div class="traslado-row {rc}">
                  <span class="cat-badge cat-{ct}">{car['cat']}</span>
                  <span style="font-family:monospace;font-weight:700;font-size:.8rem;min-width:90px">{car['matricula']}</span>
                  <span style="font-size:.8rem;color:#374151">{car['modelo']}</span>
                  <span style="margin-left:auto;font-size:.72rem;color:#6B7280">{status}</span>
                </div>""", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            if st.button(f"🗑 Eliminar traslado #{i+1}",key=f"del_t_{i}"):
                st.session_state.traslados.pop(i); st.rerun()

# ══════════════════════════════════════════
# TAB 3 — TIMELINE (Mejora 5)
# ══════════════════════════════════════════
with tab3:
    st.markdown("### 📅 Línea de tiempo del día")
    st.caption("Cada fila es una categoría. 🔵 Azul = ventana de retorno (hora retorno → disponible). 🔴 Rojo = hora de salida. La línea verde es la hora actual.")

    ret_proc_tl=[]
    for r in DEMO_RETORNOS:
        if r["matricula"] in removed_plates: continue
        ret_proc_tl.append({**r,"avail_str":avail_str(r["hora"],r["zona"]),"disponible":avail_dt(r["hora"],r["zona"])<=sim_now})
    for ac in added_cars:
        ret_proc_tl.append({**ac,"hora":ac["avail_str"],"zona":"TRASLADO","disponible":ac["disponible"]})

    res_proc_tl=[{**s,"realizada":to_dt(s["hora"])<=sim_now} for s in DEMO_RESERVAS]

    render_timeline(ret_proc_tl, res_proc_tl, sim_now, added_cars)

    # Legend
    st.markdown("""
    <div style="display:flex;gap:16px;font-size:.73rem;color:#374151;flex-wrap:wrap;margin-top:8px">
      <span><span style="background:#DBEAFE;border-radius:3px;padding:1px 7px;border:1px solid #BFDBFE">🔵 Retorno</span> ventana desde hora retorno hasta disponible</span>
      <span><span style="background:#FEE2E2;border-radius:3px;padding:1px 7px;border:1px solid #FECACA">🔴 Salida</span> hora de entrega al cliente</span>
      <span><span style="background:#EDE9FE;border-radius:3px;padding:1px 7px;border:1px solid #C4B5FD">🟣 Traslado</span> entrada desde otra base</span>
      <span style="color:#0F6E56;font-weight:700">│ Línea verde = hora actual</span>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════
# TAB 4 — STOCK DASHBOARD
# ══════════════════════════════════════════
with tab4:
    ret_proc4=[]
    for r in DEMO_RETORNOS:
        if r["matricula"] in removed_plates: continue
        av=avail_dt(r["hora"],r["zona"])
        ret_proc4.append({**r,"avail_dt":av,"avail_str":avail_str(r["hora"],r["zona"]),"disponible":av<=sim_now})
    for ac in added_cars:
        ret_proc4.append({**ac,"zona":"TRASLADO","hora":ac["avail_str"]})

    res_proc4=[{**s,"realizada":to_dt(s["hora"])<=sim_now} for s in DEMO_RESERVAS]
    eff_garaje=[c for c in DEMO_GARAJE if c["matricula"] not in removed_plates]
    for ac in added_cars:
        if ac["disponible"]: eff_garaje.append({"cat":ac["cat"],"modelo":ac["modelo"],"matricula":ac["matricula"]})

    total_g  = len(eff_garaje)
    ret_d    = sum(1 for r in ret_proc4 if r["disponible"])
    sal_h    = sum(1 for s in res_proc4 if s["realizada"])
    sal_p    = sum(1 for s in res_proc4 if not s["realizada"])
    stk_now  = total_g + ret_d - sal_h
    stk_eod  = total_g + len(ret_proc4) - len(res_proc4)
    thr      = st.session_state.threshold

    if removed_plates or added_cars:
        parts=[]
        if removed_plates: parts.append(f"🚛 {len(removed_plates)} coches retirados por traslado")
        if added_cars:     parts.append(f"🟣 {len(added_cars)} entrantes ({sum(1 for ac in added_cars if ac['disponible'])} disponibles)")
        st.markdown(f'<div class="impact-banner">{"&nbsp;&nbsp;·&nbsp;&nbsp;".join(parts)}</div>',unsafe_allow_html=True)

    st.caption(f"🟢 Stock a las {sim_now.strftime('%H:%M')} {'(simulado)' if st.session_state.use_sim else '(tiempo real)'}")

    c1,c2,c3,c4,c5=st.columns(5)
    mets=[
        ("neutral","Garaje efectivo",   total_g, f"original: {len(DEMO_GARAJE)}",""),
        ("blue",   "Retornos disp.",    ret_d,   f"de {len(ret_proc4)} hoy","blue"),
        ("warn",   "Salidas hechas",    sal_h,   "entregados","warn"),
        ("warn",   "Reservas pend.",    sal_p,   "por salir","warn"),
        ("" if stk_now>thr else "crit","Disponible ahora",stk_now,f"fin día: {stk_eod}","ok" if stk_now>thr else "crit"),
    ]
    for col,(cc,lbl,val,sub,vc) in zip([c1,c2,c3,c4,c5],mets):
        with col:
            st.markdown(f'<div class="metric-box {cc}"><div class="ml">{lbl}</div><div class="mv {vc}">{val}</div><div class="ms">{sub}</div></div>',unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 📦 Disponibilidad por categoría")

    thead='<table class="avail-table"><thead><tr><th>Cat.</th><th>Descripción</th><th>Tipo</th><th>Garaje ef.</th><th>Ret. disp.</th><th>Ret. total</th><th>Salidas</th><th>Res. pend.</th><th>🟢 Ahora</th><th>📅 Fin día</th></tr></thead><tbody>'
    tbody=""
    for cat in ALL_CATS:
        g_gar =[c for c in eff_garaje  if c["cat"]==cat]
        g_retd=[r for r in ret_proc4   if r["cat"]==cat and r["disponible"]]
        g_rett=[r for r in ret_proc4   if r["cat"]==cat]
        g_salh=[s for s in res_proc4   if s["cat"]==cat and s["realizada"]]
        g_salp=[s for s in res_proc4   if s["cat"]==cat and not s["realizada"]]
        if not g_gar and not g_rett and not g_salh and not g_salp: continue
        sn=len(g_gar)+len(g_retd)-len(g_salh); se=len(g_gar)+len(g_rett)-len(g_salh)-len(g_salp)
        sn_c="avail-ok" if sn>thr else ("avail-warn" if sn>0 else "avail-crit")
        se_c="avail-ok" if se>thr else ("avail-warn" if se>0 else "avail-crit")
        tipo="auto" if cat in CATS_AUTO else "manu"
        tbody+=f'<tr><td><span class="cat-badge cat-{tipo}">{cat}</span></td><td>{CAT_LABELS.get(cat,cat)}</td><td>{"Automático" if cat in CATS_AUTO else "Manual"}</td><td>{len(g_gar)}</td><td>{len(g_retd)}</td><td>{len(g_rett)}</td><td>{len(g_salh)}</td><td>{len(g_salp)}</td><td><span class="avail-num {sn_c}">{sn}</span></td><td><span class="avail-num {se_c}">{se}</span></td></tr>'
    st.markdown(thead+tbody+"</tbody></table>",unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 🔁 Próximos retornos pendientes")
    pend=sorted([r for r in ret_proc4 if not r["disponible"]],key=lambda x: x["avail_dt"])
    if pend:
        st.dataframe(pd.DataFrame([{"Disp. a":r["avail_str"],"Cat.":r["cat"],"Modelo":r["modelo"],"Matrícula":r["matricula"],"Zona":r["zona"]} for r in pend]),use_container_width=True,hide_index=True)
    else:
        st.success("✅ Todos los retornos ya disponibles.")

    st.divider()
    e1,e2=st.columns(2)
    with e1:
        out=io.StringIO(); w=csv.writer(out)
        w.writerow(["Cat","Descripción","Garaje ef.","Ret.disp","Ret.total","Salidas","Pend.","Stock ahora","Stock fin día"])
        for cat in ALL_CATS:
            g_gar=[c for c in eff_garaje if c["cat"]==cat]; g_retd=[r for r in ret_proc4 if r["cat"]==cat and r["disponible"]]
            g_rett=[r for r in ret_proc4 if r["cat"]==cat]; g_salh=[s for s in res_proc4 if s["cat"]==cat and s["realizada"]]
            g_salp=[s for s in res_proc4 if s["cat"]==cat and not s["realizada"]]
            if not g_gar and not g_rett: continue
            sn=len(g_gar)+len(g_retd)-len(g_salh); se=len(g_gar)+len(g_rett)-len(g_salh)-len(g_salp)
            w.writerow([cat,CAT_LABELS.get(cat,cat),len(g_gar),len(g_retd),len(g_rett),len(g_salh),len(g_salp),sn,se])
        st.download_button("⬇ CSV stock","\ufeff"+out.getvalue(),f"roig_stock_{now.strftime('%Y%m%d_%H%M')}.csv","text/csv",use_container_width=True)
    with e2:
        out2=io.StringIO()
        out2.write(f"ROIG FLEET MANAGER — STOCK\n{'='*40}\n{now.strftime('%d/%m/%Y')} {sim_now.strftime('%H:%M')}\n\n")
        for cat in ALL_CATS:
            g_gar=[c for c in eff_garaje if c["cat"]==cat]; g_retd=[r for r in ret_proc4 if r["cat"]==cat and r["disponible"]]
            g_rett=[r for r in ret_proc4 if r["cat"]==cat]; g_salh=[s for s in res_proc4 if s["cat"]==cat and s["realizada"]]
            g_salp=[s for s in res_proc4 if s["cat"]==cat and not s["realizada"]]
            if not g_gar and not g_rett: continue
            sn=len(g_gar)+len(g_retd)-len(g_salh); se=len(g_gar)+len(g_rett)-len(g_salh)-len(g_salp)
            estado="SIN STOCK" if sn<=0 else ("BAJO" if sn<=thr else "OK")
            out2.write(f"{cat} {CAT_LABELS.get(cat,''):25} | Ahora:{sn:3} | Fin:{se:3} | {estado}\n")
        st.download_button("📄 TXT resumen",out2.getvalue(),f"roig_stock_{now.strftime('%Y%m%d_%H%M')}.txt","text/plain",use_container_width=True)

st.markdown('<div style="text-align:center;padding:14px 0 4px;font-size:.67rem;color:#9CA3AF">Roig Fleet Manager · Modo Demo · Roig Rent a Car</div>',unsafe_allow_html=True)
