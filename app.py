"""
Roig Fleet Manager — DEMO INTERACTIVO v3
Categorías reales: BA CA KA HA FA (automáticas) | A B C (manuales)
Vista lista por modelo · colores por fuente de asignación
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import io, csv

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
    padding:10px 18px; margin-bottom:16px;
    display:flex; gap:28px; align-items:center; flex-wrap:wrap;
    box-shadow:0 1px 3px rgba(0,0,0,.06);
}
.sum-item { text-align:center; }
.sum-val  { font-size:1.6rem; font-weight:900; line-height:1; }
.sum-lbl  { font-size:.62rem; text-transform:uppercase; letter-spacing:.06em; color:#6B7280; font-weight:700; margin-top:2px; }
.sum-ok   { color:#16A34A; }
.sum-ret  { color:#0284C7; }
.sum-gar  { color:#EA580C; }
.sum-err  { color:#DC2626; }
.sum-neu  { color:#6B7280; }

/* Model group header */
.model-header {
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 8px 8px 0 0;
    padding: 8px 14px;
    margin-top: 14px;
    display: flex; align-items: center; gap: 10px;
}
.model-name { font-weight:800; font-size:.92rem; color:#0F6E56; }
.model-cat  { font-size:.72rem; background:#E0F2FE; color:#0284C7;
              border-radius:4px; padding:2px 8px; font-weight:700; }
.model-count { font-size:.72rem; color:#6B7280; margin-left:auto; }

/* Reservation row */
.res-row {
    display:flex; align-items:center; gap:0;
    border-left:1px solid #E2E8F0;
    border-right:1px solid #E2E8F0;
    border-bottom:1px solid #E2E8F0;
    padding:7px 14px;
    font-size:.8rem;
    background:white;
    transition:background .1s;
}
.res-row:last-child { border-radius:0 0 8px 8px; }
.res-row:hover { background:#FAFAFA; }

/* Status strip (left color bar) */
.strip {
    width:5px; height:36px; border-radius:3px;
    flex-shrink:0; margin-right:12px;
}
.strip-ok  { background:#16A34A; }
.strip-err { background:#DC2626; }

/* Time */
.res-time { font-family:monospace; font-weight:700; font-size:.82rem;
            color:#374151; min-width:52px; }

/* Zona pill */
.zona-pill {
    font-size:.64rem; font-weight:700; padding:2px 7px;
    border-radius:4px; min-width:52px; text-align:center;
    display:inline-block;
}
.zona-aerop { background:#FEE2E2; color:#991B1B; }
.zona-shutt { background:#E0E7FF; color:#3730A3; }
.zona-other { background:#F3F4F6; color:#374151; }

/* Car assignment chip */
.chip {
    font-size:.72rem; font-weight:700; padding:3px 10px;
    border-radius:20px; white-space:nowrap;
    display:inline-flex; align-items:center; gap:5px;
}
.chip-ret  { background:#DBEAFE; color:#1D4ED8; border:1px solid #BFDBFE; } /* celeste = retorno */
.chip-gar  { background:#FFEDD5; color:#C2410C; border:1px solid #FED7AA; } /* naranja = garaje */
.chip-alt  { background:#FEF3C7; color:#92400E; border:1px solid #FDE68A; } /* amarillo = alternativa */
.chip-none { background:#FEE2E2; color:#991B1B; border:1px solid #FECACA; } /* rojo = sin coche */
.chip-man  { background:#F0FDF4; color:#166534; border:1px solid #BBF7D0; } /* verde = manual */

/* Client + hotel */
.res-client { font-size:.73rem; color:#6B7280; min-width:140px; }
.res-hotel  { font-size:.71rem; color:#9CA3AF; flex:1; text-align:right;
              overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }

/* Dashboard metrics */
.metric-box {
    background:white; border:1px solid #E5E7EB; border-radius:10px;
    padding:16px; text-align:center; border-top:4px solid #0F6E56;
    box-shadow:0 1px 3px rgba(0,0,0,.06);
}
.metric-box.warn    { border-top-color:#D97706; }
.metric-box.crit    { border-top-color:#DC2626; }
.metric-box.neutral { border-top-color:#9CA3AF; }
.metric-box.blue    { border-top-color:#0284C7; }
.mv { font-size:2rem; font-weight:900; line-height:1; color:#111827; }
.mv.ok   { color:#0F6E56; }
.mv.warn { color:#D97706; }
.mv.crit { color:#DC2626; }
.mv.blue { color:#0284C7; }
.ml { font-size:.67rem; font-weight:700; text-transform:uppercase;
      letter-spacing:.06em; color:#6B7280; margin-bottom:7px; }
.ms { font-size:.7rem; color:#9CA3AF; margin-top:4px; }

/* Category availability table */
.avail-table { width:100%; border-collapse:collapse; font-size:.82rem; }
.avail-table th {
    background:#F1F5F9; padding:9px 12px; text-align:left;
    font-size:.67rem; font-weight:700; text-transform:uppercase;
    letter-spacing:.05em; color:#64748B;
    border-bottom:2px solid #E2E8F0;
}
.avail-table td { padding:10px 12px; border-bottom:1px solid #F1F5F9; vertical-align:middle; }
.avail-table tr:hover td { background:#F8FAFC; }
.cat-badge {
    font-size:.75rem; font-weight:800; padding:3px 10px;
    border-radius:6px; display:inline-block; letter-spacing:.02em;
}
.cat-auto { background:#E0F2FE; color:#0284C7; }
.cat-manu { background:#F0FDF4; color:#166534; }
.avail-num { font-size:1.3rem; font-weight:900; }
.avail-ok   { color:#0F6E56; }
.avail-warn { color:#D97706; }
.avail-crit { color:#DC2626; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap:3px; background:#F1F5F9; padding:4px; border-radius:10px; margin-bottom:16px;
}
.stTabs [data-baseweb="tab"] { border-radius:7px !important; font-weight:700 !important; }
.stTabs [aria-selected="true"] { background:white !important; box-shadow:0 1px 3px rgba(0,0,0,.1) !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# CATEGORIES
# ─────────────────────────────────────────
CATS_AUTO = ["BA", "CA", "KA", "HA", "FA"]
CATS_MANU = ["A", "B", "C"]
ALL_CATS  = CATS_AUTO + CATS_MANU

CAT_LABELS = {
    "BA": "Automático pequeño",
    "CA": "Automático compacto",
    "KA": "Automático mediano",
    "HA": "Automático SUV",
    "FA": "Automático familiar",
    "A":  "Manual pequeño",
    "B":  "Manual compacto",
    "C":  "Manual mediano",
}

ZONA_OFFSET = {"AEROP": 60, "SHUTT": 45}

# ─────────────────────────────────────────
# DEMO DATA — using real category codes
# ─────────────────────────────────────────
DEMO_GARAJE = [
    # BA — auto pequeño
    {"cat": "BA", "modelo": "Seat Ibiza Auto",      "matricula": "4523 MLL"},
    {"cat": "BA", "modelo": "Seat Ibiza Auto",      "matricula": "7821 PKR"},
    {"cat": "BA", "modelo": "Opel Corsa Auto",      "matricula": "3190 HBT"},
    {"cat": "BA", "modelo": "VW Polo Auto",         "matricula": "9902 DFS"},
    # CA — auto compacto
    {"cat": "CA", "modelo": "Seat León Auto",       "matricula": "6614 NMW"},
    {"cat": "CA", "modelo": "Seat León Auto",       "matricula": "1147 QVX"},
    {"cat": "CA", "modelo": "Toyota Corolla Auto",  "matricula": "2255 RPK"},
    # KA — auto mediano
    {"cat": "KA", "modelo": "VW Tiguan Auto",       "matricula": "7709 MXQ"},
    {"cat": "KA", "modelo": "Hyundai Tucson Auto",  "matricula": "3348 LVZ"},
    # HA — auto SUV
    {"cat": "HA", "modelo": "Seat Tarraco Auto",    "matricula": "1123 WKF"},
    {"cat": "HA", "modelo": "VW Touareg Auto",      "matricula": "5580 ZZA"},
    # FA — auto familiar
    {"cat": "FA", "modelo": "Ford Galaxy Auto",     "matricula": "9934 CPM"},
    # A — manual pequeño
    {"cat": "A",  "modelo": "Seat Ibiza",           "matricula": "8801 TRE"},
    {"cat": "A",  "modelo": "Opel Corsa",           "matricula": "4412 QQM"},
    # B — manual compacto
    {"cat": "B",  "modelo": "Seat León",            "matricula": "6630 BNK"},
    {"cat": "B",  "modelo": "Ford Focus",           "matricula": "8830 JTL"},
    # C — manual mediano
    {"cat": "C",  "modelo": "Dacia Duster",         "matricula": "5571 CBN"},
]

DEMO_RETORNOS = [
    {"hora": "07:30", "cat": "BA", "modelo": "Seat Ibiza Auto",     "matricula": "1198 ZZT", "zona": "AEROP"},
    {"hora": "08:00", "cat": "A",  "modelo": "Seat Ibiza",          "matricula": "4456 KLM", "zona": "SHUTT"},
    {"hora": "08:45", "cat": "CA", "modelo": "Seat León Auto",      "matricula": "7723 OPQ", "zona": "AEROP"},
    {"hora": "09:15", "cat": "C",  "modelo": "Dacia Duster",        "matricula": "3381 RST", "zona": "OFICINA"},
    {"hora": "10:00", "cat": "CA", "modelo": "Toyota Corolla Auto", "matricula": "6690 UVW", "zona": "SHUTT"},
    {"hora": "10:30", "cat": "KA", "modelo": "Hyundai Tucson Auto", "matricula": "8812 XYZ", "zona": "AEROP"},
    {"hora": "11:00", "cat": "B",  "modelo": "Ford Focus",          "matricula": "2234 ABC", "zona": "OFICINA"},
    {"hora": "12:00", "cat": "BA", "modelo": "Opel Corsa Auto",     "matricula": "5567 DEF", "zona": "AEROP"},
    {"hora": "13:30", "cat": "KA", "modelo": "VW Tiguan Auto",      "matricula": "9901 GHI", "zona": "SHUTT"},
    {"hora": "14:00", "cat": "BA", "modelo": "Seat Ibiza Auto",     "matricula": "1145 JKL", "zona": "AEROP"},
    {"hora": "15:30", "cat": "HA", "modelo": "Seat Tarraco Auto",   "matricula": "4478 MNO", "zona": "OFICINA"},
    {"hora": "16:00", "cat": "FA", "modelo": "Ford Galaxy Auto",    "matricula": "7712 PQR", "zona": "AEROP"},
    {"hora": "17:00", "cat": "B",  "modelo": "Seat León",           "matricula": "3345 STU", "zona": "SHUTT"},
    {"hora": "18:30", "cat": "CA", "modelo": "Seat León Auto",      "matricula": "6678 VWX", "zona": "AEROP"},
    {"hora": "19:00", "cat": "A",  "modelo": "Opel Corsa",          "matricula": "9923 YZA", "zona": "OFICINA"},
]

DEMO_RESERVAS = [
    {"hora": "07:00", "cat": "BA", "modelo": "BA",  "cliente": "García López, M.",  "agencia": "OFFUGO",        "hotel": "1504"},
    {"hora": "07:30", "cat": "BA", "modelo": "BA",  "cliente": "Müller, H.",        "agencia": "SHUTT",         "hotel": "1501 Solier Garden"},
    {"hora": "08:00", "cat": "C",  "modelo": "C",   "cliente": "Smith, J.",         "agencia": "GARAJE",        "hotel": "1504"},
    {"hora": "08:30", "cat": "CA", "modelo": "CA",  "cliente": "Martínez, A.",      "agencia": "AEROP",         "hotel": "1504"},
    {"hora": "09:00", "cat": "KA", "modelo": "KA",  "cliente": "Rossi, G.",         "agencia": "AEROP",         "hotel": "1504"},
    {"hora": "09:30", "cat": "B",  "modelo": "B",   "cliente": "Dupont, C.",        "agencia": "OFFUGO",        "hotel": "1504"},
    {"hora": "10:00", "cat": "CA", "modelo": "CA",  "cliente": "Fernández, R.",     "agencia": "SHUTT",         "hotel": "1501 Casa Rural"},
    {"hora": "10:30", "cat": "BA", "modelo": "BA",  "cliente": "Williams, T.",      "agencia": "AEROP",         "hotel": "1504"},
    {"hora": "11:00", "cat": "KA", "modelo": "KA",  "cliente": "Sánchez, P.",       "agencia": "OFFUGO",        "hotel": "1504"},
    {"hora": "12:00", "cat": "BA", "modelo": "BA",  "cliente": "Johnson, K.",       "agencia": "AEROP",         "hotel": "1501 Barceló"},
    {"hora": "13:00", "cat": "HA", "modelo": "HA",  "cliente": "Nakamura, Y.",      "agencia": "SHUTT",         "hotel": "1504"},
    {"hora": "13:00", "cat": "BA", "modelo": "BA",  "cliente": "Pérez, L.",         "agencia": "AEROP",         "hotel": "1504"},
    {"hora": "14:00", "cat": "CA", "modelo": "CA",  "cliente": "Brown, A.",         "agencia": "OFFUGO",        "hotel": "1501 Iberostar"},
    {"hora": "15:00", "cat": "HA", "modelo": "HA",  "cliente": "González, C.",      "agencia": "AEROP",         "hotel": "1504"},
    {"hora": "16:00", "cat": "FA", "modelo": "FA",  "cliente": "Hoffmann, E.",      "agencia": "SHUTT",         "hotel": "1501 Primasol"},
    {"hora": "17:00", "cat": "A",  "modelo": "A",   "cliente": "López, S.",         "agencia": "AEROP",         "hotel": "1504"},
    {"hora": "18:00", "cat": "BA", "modelo": "BA",  "cliente": "Davies, R.",        "agencia": "OFFUGO",        "hotel": "1504"},
    {"hora": "19:00", "cat": "C",  "modelo": "C",   "cliente": "Moreau, F.",        "agencia": "AEROP",         "hotel": "1504"},
    {"hora": "20:00", "cat": "B",  "modelo": "B",   "cliente": "Schmidt, K.",       "agencia": "SHUTT",         "hotel": "1501 Leonardo"},
    {"hora": "20:30", "cat": "KA", "modelo": "KA",  "cliente": "Tanaka, H.",        "agencia": "AEROP",         "hotel": "1504"},
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

# ─────────────────────────────────────────
# ASSIGNMENT ENGINE
# ─────────────────────────────────────────
def auto_assign(reservas, garaje, retornos, sim_now):
    garaje_pool = [dict(c, used=False) for c in garaje]
    ret_pool = []
    for r in retornos:
        av = avail_dt(r["hora"], r["zona"])
        ret_pool.append(dict(r, avail_dt=av, avail_str=avail_str(r["hora"], r["zona"]), used=False))

    assignments = []
    for res in reservas:
        res_dt  = to_dt(res["hora"])
        cat     = res["cat"]
        assigned = None
        source   = None
        note     = ""
        alt_sugg = []

        # 1. Return — exact category, arrives in time (PRIORITY)
        cands = [r for r in ret_pool if not r["used"] and r["cat"] == cat and r["avail_dt"] <= res_dt]
        cands.sort(key=lambda x: x["avail_dt"])
        if cands:
            r2 = cands[0]; r2["used"] = True
            assigned = r2["matricula"]
            source   = "retorno"
            note     = f"Retorno {r2['hora']} · zona {r2['zona']} · disponible {r2['avail_str']}"

        # 2. Garaje — exact category
        if not assigned:
            for c in garaje_pool:
                if not c["used"] and c["cat"] == cat:
                    c["used"] = True
                    assigned  = c["matricula"]
                    source    = "garaje"
                    break

        # 3. Garaje — adjacent category (upgrade first)
        if not assigned:
            cat_order = ALL_CATS
            cat_idx   = cat_order.index(cat) if cat in cat_order else -1
            for c in garaje_pool:
                if not c["used"]:
                    ci = cat_order.index(c["cat"]) if c["cat"] in cat_order else -1
                    if ci == cat_idx + 1:
                        c["used"] = True
                        assigned  = c["matricula"]
                        source    = "garaje_alt"
                        note      = f"Alternativa: {c['cat']} ({c['modelo']})"
                        break

        # 4. Return — adjacent category arriving in time
        if not assigned:
            cat_idx = ALL_CATS.index(cat) if cat in ALL_CATS else -1
            cands = [r for r in ret_pool if not r["used"] 
                     and r["avail_dt"] <= res_dt
                     and r["cat"] in ALL_CATS
                     and ALL_CATS.index(r["cat"]) == cat_idx + 1]
            cands.sort(key=lambda x: x["avail_dt"])
            if cands:
                r2 = cands[0]; r2["used"] = True
                assigned = r2["matricula"]
                source   = "retorno_alt"
                note     = f"Alt. {r2['cat']} ({r2['modelo']}) · retorno {r2['hora']} disp. {r2['avail_str']}"

        # No car — build suggestions
        if not assigned:
            for c in garaje_pool:
                if not c["used"]:
                    alt_sugg.append(f"{c['cat']} · {c['modelo']} · {c['matricula']} (garaje)")
                    if len(alt_sugg) >= 3: break
            if len(alt_sugg) < 3:
                for r2 in ret_pool:
                    if not r2["used"]:
                        alt_sugg.append(f"{r2['cat']} · {r2['modelo']} · {r2['matricula']} (retorno {r2['hora']} → {r2['avail_str']})")
                        if len(alt_sugg) >= 3: break

        assignments.append({
            "hora":     res["hora"],
            "cat":      cat,
            "cliente":  res["cliente"],
            "agencia":  res.get("agencia",""),
            "hotel":    res.get("hotel",""),
            "assigned": assigned,
            "source":   source,
            "note":     note,
            "sugg":     alt_sugg,
            "modelo_ret": next((r["modelo"] for r in ret_pool if r["matricula"] == assigned), None) if source in ("retorno","retorno_alt") else None,
            "modelo_gar": next((c["modelo"] for c in garaje_pool if c["matricula"] == assigned), None) if source in ("garaje","garaje_alt") else None,
        })

    return assignments, garaje_pool, ret_pool

# ─────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────
now = datetime.now()
for k, v in {"sim_h": now.hour, "sim_m": now.minute, "use_sim": False,
             "threshold": 2, "overrides": {}}.items():
    if k not in st.session_state: st.session_state[k] = v

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
    st.session_state.threshold = st.number_input("Umbral alerta stock", 0, 10, st.session_state.threshold)
    st.divider()
    st.markdown("### ⏱ Simular hora")
    st.session_state.sim_h   = st.slider("Hora", 0, 23, st.session_state.sim_h)
    st.session_state.sim_m   = st.slider("Minuto", 0, 59, st.session_state.sim_m)
    st.session_state.use_sim = st.checkbox("Activar simulación", st.session_state.use_sim)
    if st.session_state.use_sim:
        st.info(f"⏱ Simulando **{st.session_state.sim_h:02d}:{st.session_state.sim_m:02d}**")
    st.divider()
    if st.button("🔄 Resetear asignaciones manuales", use_container_width=True):
        st.session_state.overrides = {}; st.rerun()
    st.divider()
    st.markdown("**Leyenda de colores:**")
    st.markdown("🔵 Azul celeste = retorno")
    st.markdown("🟠 Naranja = garaje")
    st.markdown("🟡 Amarillo = alternativa de categoría")
    st.markdown("🟢 Verde = asignación manual OK")
    st.markdown("🔴 Rojo = sin coche disponible")

sim_now = now.replace(hour=st.session_state.sim_h, minute=st.session_state.sim_m, second=0) \
    if st.session_state.use_sim else now

# ─────────────────────────────────────────
# COMPUTE
# ─────────────────────────────────────────
base_asgn, garaje_pool, ret_pool = auto_assign(DEMO_RESERVAS, DEMO_GARAJE, DEMO_RETORNOS, sim_now)

# Build all-car list for manual selector
all_cars_sel = []
for c in DEMO_GARAJE:
    all_cars_sel.append({"label": f"[{c['cat']}] {c['matricula']} — {c['modelo']} · GARAJE",
                          "matricula": c["matricula"], "cat": c["cat"], "source": "garaje"})
for r in DEMO_RETORNOS:
    av = avail_str(r["hora"], r["zona"])
    all_cars_sel.append({"label": f"[{r['cat']}] {r['matricula']} — {r['modelo']} · RETORNO {r['hora']} → {av}",
                          "matricula": r["matricula"], "cat": r["cat"], "source": f"retorno {r['hora']}", "avail": av})

# Apply overrides
assignments = []
for i, a in enumerate(base_asgn):
    if i in st.session_state.overrides:
        mat = st.session_state.overrides[i]
        car = next((c for c in all_cars_sel if c["matricula"] == mat), None)
        if car:
            assignments.append({**a, "assigned": mat, "source": "manual",
                                 "note": f"Manual · {car['cat']} · {car['label'].split('—')[1].strip()}"})
            continue
    assignments.append(a)

# ─────────────────────────────────────────
# TABS
# ─────────────────────────────────────────
tab1, tab2 = st.tabs(["📋  Asignación de reservas por modelo", "📊  Stock disponible para vender"])

# ══════════════════════════════════════════════
# TAB 1 — RESERVATIONS LIST BY CATEGORY
# ══════════════════════════════════════════════
with tab1:

    n_ret  = sum(1 for a in assignments if a["source"] in ("retorno",))
    n_gar  = sum(1 for a in assignments if a["source"] in ("garaje",))
    n_alt  = sum(1 for a in assignments if a["source"] in ("garaje_alt","retorno_alt"))
    n_man  = sum(1 for a in assignments if a["source"] == "manual")
    n_err  = sum(1 for a in assignments if not a["assigned"])
    n_ok   = n_ret + n_gar + n_man

    st.markdown(f"""
    <div class="sum-bar">
      <div class="sum-item"><div class="sum-val sum-ok">{n_ok}</div><div class="sum-lbl">🟢 Cubiertas</div></div>
      <div class="sum-item"><div class="sum-val sum-ret">{n_ret}</div><div class="sum-lbl">🔵 Retorno</div></div>
      <div class="sum-item"><div class="sum-val sum-gar">{n_gar}</div><div class="sum-lbl">🟠 Garaje</div></div>
      <div class="sum-item"><div class="sum-val sum-warn" style="color:#D97706">{n_alt}</div><div class="sum-lbl">🟡 Alternativa</div></div>
      <div class="sum-item"><div class="sum-val sum-err">{n_err}</div><div class="sum-lbl">🔴 Sin coche</div></div>
      <div class="sum-item"><div class="sum-val sum-neu">{len(assignments)}</div><div class="sum-lbl">Total</div></div>
    </div>
    """, unsafe_allow_html=True)

    # Group by category maintaining order
    from collections import OrderedDict
    groups = OrderedDict()
    for cat in ALL_CATS:
        cat_asgn = [a for a in assignments if a["cat"] == cat]
        if cat_asgn:
            groups[cat] = cat_asgn

    for cat, cat_asgns in groups.items():
        cat_type  = "auto" if cat in CATS_AUTO else "manu"
        type_icon = "⚙️" if cat in CATS_AUTO else "🔧"
        n_cat_ok  = sum(1 for a in cat_asgns if a["assigned"])
        n_cat_err = sum(1 for a in cat_asgns if not a["assigned"])

        # Model group header
        st.markdown(f"""
        <div class="model-header">
          <span style="font-size:1rem">{type_icon}</span>
          <span class="model-name">{cat}</span>
          <span class="cat-badge cat-{cat_type}">{CAT_LABELS.get(cat, cat)}</span>
          <span style="font-size:.72rem;color:#6B7280;margin-left:auto">
            {n_cat_ok} cubiertas · {'<span style="color:#DC2626;font-weight:700">' + str(n_cat_err) + ' sin coche</span>' if n_cat_err else '0 sin coche'}
            · {len(cat_asgns)} reservas
          </span>
        </div>
        """, unsafe_allow_html=True)

        # Header row
        st.markdown("""
        <div style="display:flex;background:#F8FAFC;padding:5px 14px 5px 31px;
                    border-left:1px solid #E2E8F0;border-right:1px solid #E2E8F0;
                    font-size:.65rem;font-weight:700;text-transform:uppercase;
                    letter-spacing:.05em;color:#94A3B8;gap:0">
          <span style="min-width:52px">Hora</span>
          <span style="min-width:64px;margin-left:12px">Zona</span>
          <span style="min-width:200px;margin-left:8px">Coche asignado</span>
          <span style="min-width:160px;margin-left:8px">Detalle asignación</span>
          <span style="min-width:150px;margin-left:8px">Cliente</span>
          <span style="margin-left:auto">Hotel / Agencia</span>
        </div>
        """, unsafe_allow_html=True)

        for i_global, a in [(j, x) for j, x in enumerate(assignments) if x["cat"] == cat]:
            src = a["source"] or ""

            # Strip color
            if not a["assigned"]:   strip_cls = "strip-err"
            else:                    strip_cls = "strip-ok"

            # Chip
            if not a["assigned"]:
                chip_cls = "chip-none"
                chip_txt = "❌ Sin coche"
                chip_mat = ""
            elif src == "retorno":
                chip_cls = "chip-ret"
                chip_txt = f"🔵 {a['assigned']}"
                chip_mat = a.get("modelo_ret","")
            elif src == "garaje":
                chip_cls = "chip-gar"
                chip_txt = f"🟠 {a['assigned']}"
                chip_mat = a.get("modelo_gar","")
            elif src in ("garaje_alt","retorno_alt"):
                chip_cls = "chip-alt"
                chip_txt = f"🟡 {a['assigned']}"
                chip_mat = ""
            elif src == "manual":
                chip_cls = "chip-man"
                chip_txt = f"🟢 {a['assigned']}"
                chip_mat = ""
            else:
                chip_cls = "chip-none"
                chip_txt = "—"
                chip_mat = ""

            # Zona pill
            zona_raw = a.get("agencia","").upper()
            if "AEROP" in zona_raw:   zona_cls = "zona-aerop"; zona_lbl = "AEROP"
            elif "SHUTT" in zona_raw: zona_cls = "zona-shutt"; zona_lbl = "SHUTT"
            else:                      zona_cls = "zona-other"; zona_lbl = zona_raw[:6] or "—"

            note_html = f'<span style="font-size:.68rem;color:#6B7280">{a["note"]}</span>' if a["note"] else '<span style="color:#CBD5E1;font-size:.68rem">—</span>'

            st.markdown(f"""
            <div class="res-row">
              <div class="strip {strip_cls}"></div>
              <span class="res-time">{a['hora']}</span>
              <span style="margin-left:12px;min-width:64px">
                <span class="zona-pill {zona_cls}">{zona_lbl}</span>
              </span>
              <span style="margin-left:8px;min-width:200px">
                <span class="chip {chip_cls}">{chip_txt}</span>
                {f'<span style="font-size:.68rem;color:#6B7280;margin-left:4px">{chip_mat}</span>' if chip_mat else ''}
              </span>
              <span style="margin-left:8px;min-width:160px">{note_html}</span>
              <span class="res-client" style="margin-left:8px">{a['cliente']}</span>
              <span class="res-hotel">{a.get('hotel','')}</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    # ── Manual reassignment expander ──────────
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("✏️ Cambiar asignación manualmente"):
        st.caption("Selecciona una reserva y asígnale un coche diferente.")

        res_options = [f"#{i} · {a['hora']} · Cat.{a['cat']} · {a['cliente']}" for i,a in enumerate(assignments)]
        chosen_res  = st.selectbox("Reserva", res_options, key="man_res")
        res_idx     = res_options.index(chosen_res)
        cur_asgn    = assignments[res_idx]

        car_opts = ["— Sin cambio —"] + [c["label"] for c in all_cars_sel]
        cur_mat  = cur_asgn["assigned"]
        cur_car  = next((c["label"] for c in all_cars_sel if c["matricula"] == cur_mat), None)
        def_idx  = car_opts.index(cur_car) if cur_car in car_opts else 0

        chosen_car = st.selectbox("Coche a asignar", car_opts, index=def_idx, key="man_car")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Confirmar asignación", use_container_width=True, type="primary"):
                if chosen_car != "— Sin cambio —":
                    mat = next((c["matricula"] for c in all_cars_sel if c["label"] == chosen_car), None)
                    if mat:
                        st.session_state.overrides[res_idx] = mat
                        st.rerun()
        with col2:
            if res_idx in st.session_state.overrides:
                if st.button("↩ Restaurar automático", use_container_width=True):
                    del st.session_state.overrides[res_idx]; st.rerun()

        # Show suggestions if no car
        if not cur_asgn["assigned"] and cur_asgn["sugg"]:
            st.warning("Sin coche disponible. Sugerencias:")
            for s in cur_asgn["sugg"]:
                st.markdown(f"· {s}")

# ══════════════════════════════════════════════
# TAB 2 — STOCK DASHBOARD
# ══════════════════════════════════════════════
with tab2:

    ret_proc = []
    for r in DEMO_RETORNOS:
        av = avail_dt(r["hora"], r["zona"])
        ret_proc.append({**r, "avail_dt": av, "avail_str": avail_str(r["hora"], r["zona"]),
                          "disponible": av <= sim_now})

    res_proc = []
    for s in DEMO_RESERVAS:
        res_proc.append({**s, "realizada": to_dt(s["hora"]) <= sim_now})

    total_garaje = len(DEMO_GARAJE)
    ret_disp     = sum(1 for r in ret_proc if r["disponible"])
    ret_total    = len(ret_proc)
    sal_hechas   = sum(1 for s in res_proc if s["realizada"])
    sal_pend     = sum(1 for s in res_proc if not s["realizada"])
    stock_now    = total_garaje + ret_disp - sal_hechas
    stock_eod    = total_garaje + ret_total - len(res_proc)
    thr          = st.session_state.threshold

    st.caption(f"🟢 Stock a las {sim_now.strftime('%H:%M')} {'(simulado)' if st.session_state.use_sim else '(tiempo real)'}")

    c1,c2,c3,c4,c5 = st.columns(5)
    mets = [
        ("neutral","Coches en garaje",       total_garaje, "inventario base",              ""),
        ("blue",   "Retornos disponibles",   ret_disp,     f"de {ret_total} retornos hoy", "blue"),
        ("warn",   "Salidas realizadas",     sal_hechas,   "ya entregados",                "warn"),
        ("warn",   "Reservas pendientes",    sal_pend,     "por salir hoy",                "warn"),
        ("" if stock_now>thr else "crit", "Disponible ahora", stock_now, f"fin día: {stock_eod}",
         "ok" if stock_now>thr else "crit"),
    ]
    for col,(cc,lbl,val,sub,vc) in zip([c1,c2,c3,c4,c5],mets):
        with col:
            st.markdown(f"""<div class="metric-box {cc}">
                <div class="ml">{lbl}</div>
                <div class="mv {vc}">{val}</div>
                <div class="ms">{sub}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 📦 Disponibilidad por categoría — lo que puedes ofrecer ahora")

    thead = """<table class="avail-table"><thead><tr>
      <th>Cat.</th><th>Descripción</th><th>Tipo</th>
      <th>Garaje</th><th>Ret. disp.</th><th>Ret. total</th>
      <th>Salidas</th><th>Res. pend.</th>
      <th>🟢 Ahora</th><th>📅 Fin día</th>
    </tr></thead><tbody>"""

    tbody = ""
    for cat in ALL_CATS:
        g_gar  = [c for c in DEMO_GARAJE if c["cat"] == cat]
        g_retd = [r for r in ret_proc    if r["cat"] == cat and r["disponible"]]
        g_rett = [r for r in ret_proc    if r["cat"] == cat]
        g_salh = [s for s in res_proc    if s["cat"] == cat and s["realizada"]]
        g_salp = [s for s in res_proc    if s["cat"] == cat and not s["realizada"]]
        sn = len(g_gar) + len(g_retd) - len(g_salh)
        se = len(g_gar) + len(g_rett) - len(g_salh) - len(g_salp)
        if not g_gar and not g_rett and not g_salh and not g_salp: continue
        sn_cls = "avail-ok" if sn > thr else ("avail-warn" if sn > 0 else "avail-crit")
        se_cls = "avail-ok" if se > thr else ("avail-warn" if se > 0 else "avail-crit")
        tipo   = "auto" if cat in CATS_AUTO else "manu"
        tipo_l = "Automático" if cat in CATS_AUTO else "Manual"
        tbody += f"""<tr>
          <td><span class="cat-badge cat-{tipo}">{cat}</span></td>
          <td>{CAT_LABELS.get(cat,cat)}</td>
          <td>{tipo_l}</td>
          <td>{len(g_gar)}</td>
          <td>{len(g_retd)}</td>
          <td>{len(g_rett)}</td>
          <td>{len(g_salh)}</td>
          <td>{len(g_salp)}</td>
          <td><span class="avail-num {sn_cls}">{sn}</span></td>
          <td><span class="avail-num {se_cls}">{se}</span></td>
        </tr>"""

    st.markdown(thead + tbody + "</tbody></table>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 🔁 Próximos retornos pendientes de llegar")
    pend = sorted([r for r in ret_proc if not r["disponible"]], key=lambda x: x["avail_dt"])
    if pend:
        df_ret = pd.DataFrame([{
            "Disp. a": r["avail_str"], "Hora ret.": r["hora"],
            "Cat.": r["cat"], "Modelo": r["modelo"],
            "Matrícula": r["matricula"], "Zona": r["zona"],
        } for r in pend])
        st.dataframe(df_ret, use_container_width=True, hide_index=True)
    else:
        st.success("✅ Todos los retornos del día ya están disponibles.")

    st.divider()
    e1, e2 = st.columns(2)
    with e1:
        out = io.StringIO()
        w = csv.writer(out)
        w.writerow(["Cat","Descripción","Garaje","Ret.disp","Ret.total","Salidas","Pend.","Stock ahora","Stock fin día"])
        for cat in ALL_CATS:
            g_gar  = [c for c in DEMO_GARAJE if c["cat"]==cat]
            g_retd = [r for r in ret_proc if r["cat"]==cat and r["disponible"]]
            g_rett = [r for r in ret_proc if r["cat"]==cat]
            g_salh = [s for s in res_proc if s["cat"]==cat and s["realizada"]]
            g_salp = [s for s in res_proc if s["cat"]==cat and not s["realizada"]]
            if not g_gar and not g_rett: continue
            sn=len(g_gar)+len(g_retd)-len(g_salh); se=len(g_gar)+len(g_rett)-len(g_salh)-len(g_salp)
            w.writerow([cat,CAT_LABELS.get(cat,cat),len(g_gar),len(g_retd),len(g_rett),len(g_salh),len(g_salp),sn,se])
        st.download_button("⬇ CSV stock por categoría", "\ufeff"+out.getvalue(),
            f"roig_stock_{now.strftime('%Y%m%d_%H%M')}.csv","text/csv", use_container_width=True)
    with e2:
        out2 = io.StringIO()
        out2.write(f"ROIG FLEET MANAGER — STOCK\n{'='*40}\n{now.strftime('%d/%m/%Y')} {sim_now.strftime('%H:%M')}\n\n")
        for cat in ALL_CATS:
            g_gar  = [c for c in DEMO_GARAJE if c["cat"]==cat]
            g_retd = [r for r in ret_proc if r["cat"]==cat and r["disponible"]]
            g_rett = [r for r in ret_proc if r["cat"]==cat]
            g_salh = [s for s in res_proc if s["cat"]==cat and s["realizada"]]
            g_salp = [s for s in res_proc if s["cat"]==cat and not s["realizada"]]
            if not g_gar and not g_rett: continue
            sn=len(g_gar)+len(g_retd)-len(g_salh); se=len(g_gar)+len(g_rett)-len(g_salh)-len(g_salp)
            estado="SIN STOCK" if sn<=0 else ("BAJO" if sn<=thr else "OK")
            out2.write(f"{cat} {CAT_LABELS.get(cat,''):25} | Ahora:{sn:3} | Fin:{se:3} | {estado}\n")
        st.download_button("📄 TXT resumen", out2.getvalue(),
            f"roig_stock_{now.strftime('%Y%m%d_%H%M')}.txt","text/plain", use_container_width=True)

st.markdown('<div style="text-align:center;padding:16px 0 4px;font-size:.68rem;color:#9CA3AF">Roig Fleet Manager · Modo Demo</div>', unsafe_allow_html=True)
