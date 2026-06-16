"""
Roig Fleet Manager — v4
+ Pestaña Traslados: camiones LOMBA, JOSE, DIEGO
  Salida Son Oms → resta del inventario ese día
  Entrada a Son Oms → disponible desde hora_salida + 60 min
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
.sum-warn { color:#D97706; }
.sum-err  { color:#DC2626; }
.sum-neu  { color:#6B7280; }
.sum-truck { color:#7C3AED; }

.model-header {
    background: #F8FAFC; border: 1px solid #E2E8F0;
    border-radius: 8px 8px 0 0; padding: 8px 14px;
    margin-top: 14px;
    display: flex; align-items: center; gap: 10px;
}
.model-name { font-weight:800; font-size:.92rem; color:#0F6E56; }
.model-cat  { font-size:.72rem; background:#E0F2FE; color:#0284C7;
              border-radius:4px; padding:2px 8px; font-weight:700; }

.res-row {
    display:flex; align-items:center; gap:0;
    border-left:1px solid #E2E8F0; border-right:1px solid #E2E8F0;
    border-bottom:1px solid #E2E8F0;
    padding:7px 14px; font-size:.8rem; background:white;
    transition:background .1s;
}
.res-row:last-child { border-radius:0 0 8px 8px; }
.res-row:hover { background:#FAFAFA; }

.strip { width:5px; height:36px; border-radius:3px; flex-shrink:0; margin-right:12px; }
.strip-ok  { background:#16A34A; }
.strip-err { background:#DC2626; }

.res-time { font-family:monospace; font-weight:700; font-size:.82rem; color:#374151; min-width:52px; }

.zona-pill { font-size:.64rem; font-weight:700; padding:2px 7px; border-radius:4px;
             min-width:52px; text-align:center; display:inline-block; }
.zona-aerop { background:#FEE2E2; color:#991B1B; }
.zona-shutt { background:#E0E7FF; color:#3730A3; }
.zona-other { background:#F3F4F6; color:#374151; }

.chip { font-size:.72rem; font-weight:700; padding:3px 10px; border-radius:20px;
        white-space:nowrap; display:inline-flex; align-items:center; gap:5px; }
.chip-ret  { background:#DBEAFE; color:#1D4ED8; border:1px solid #BFDBFE; }
.chip-gar  { background:#FFEDD5; color:#C2410C; border:1px solid #FED7AA; }
.chip-alt  { background:#FEF3C7; color:#92400E; border:1px solid #FDE68A; }
.chip-none { background:#FEE2E2; color:#991B1B; border:1px solid #FECACA; }
.chip-man  { background:#F0FDF4; color:#166534; border:1px solid #BBF7D0; }

.res-client { font-size:.73rem; color:#6B7280; min-width:140px; }
.res-hotel  { font-size:.71rem; color:#9CA3AF; flex:1; text-align:right;
              overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }

/* ── Traslados ── */
.truck-card {
    background: white;
    border: 1.5px solid #E5E7EB;
    border-radius: 12px;
    padding: 16px 18px;
    margin-bottom: 12px;
    box-shadow: 0 1px 4px rgba(0,0,0,.06);
}
.truck-header {
    display: flex; align-items: center; gap: 10px;
    margin-bottom: 12px;
    padding-bottom: 10px;
    border-bottom: 1px solid #F1F5F9;
}
.truck-name { font-size:1rem; font-weight:800; color:#111827; }
.truck-badge {
    font-size:.72rem; font-weight:700; padding:3px 10px;
    border-radius:20px;
}
.truck-out  { background:#FEE2E2; color:#991B1B; border:1px solid #FECACA; }
.truck-in   { background:#D1FAE5; color:#065F46; border:1px solid #A7F3D0; }
.truck-idle { background:#F3F4F6; color:#6B7280; border:1px solid #E5E7EB; }

.traslado-row {
    display:flex; align-items:center; gap:10px;
    padding:6px 10px; border-radius:8px;
    font-size:.8rem; margin-bottom:4px;
    background:#F9FAFB;
}
.traslado-row.out { border-left:4px solid #DC2626; }
.traslado-row.in  { border-left:4px solid #16A34A; }
.traslado-row.pending { opacity:.6; }

.impact-banner {
    background:#FFF7ED; border:1px solid #FED7AA;
    border-radius:8px; padding:10px 14px;
    font-size:.78rem; color:#92400E;
    margin-top:10px;
}

/* ── Dashboard metrics ── */
.metric-box {
    background:white; border:1px solid #E5E7EB; border-radius:10px;
    padding:16px; text-align:center; border-top:4px solid #0F6E56;
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
.ml { font-size:.67rem; font-weight:700; text-transform:uppercase;
      letter-spacing:.06em; color:#6B7280; margin-bottom:7px; }
.ms { font-size:.7rem; color:#9CA3AF; margin-top:4px; }

.avail-table { width:100%; border-collapse:collapse; font-size:.82rem; }
.avail-table th {
    background:#F1F5F9; padding:9px 12px; text-align:left;
    font-size:.67rem; font-weight:700; text-transform:uppercase;
    letter-spacing:.05em; color:#64748B; border-bottom:2px solid #E2E8F0;
}
.avail-table td { padding:10px 12px; border-bottom:1px solid #F1F5F9; vertical-align:middle; }
.avail-table tr:hover td { background:#F8FAFC; }
.cat-badge { font-size:.75rem; font-weight:800; padding:3px 10px;
             border-radius:6px; display:inline-block; letter-spacing:.02em; }
.cat-auto { background:#E0F2FE; color:#0284C7; }
.cat-manu { background:#F0FDF4; color:#166534; }
.avail-num { font-size:1.3rem; font-weight:900; }
.avail-ok   { color:#0F6E56; }
.avail-warn { color:#D97706; }
.avail-crit { color:#DC2626; }

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
ZONA_OFFSET  = {"AEROP":60,"SHUTT":45}
BASES        = ["Cala d'Or","Calas","Cala Millor","Alcudia"]
CONDUCTORES  = ["LOMBA","JOSE","DIEGO"]
TRAVEL_MINS  = 60   # travel time between bases

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
    """Estimated arrival at Son Oms = departure + 60 min travel"""
    return to_dt(hora_salida) + timedelta(minutes=TRAVEL_MINS)

def arrival_str(hora_salida):
    return arrival_dt(hora_salida).strftime("%H:%M")

# ─────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────
now = datetime.now()
defaults = {
    "sim_h": now.hour, "sim_m": now.minute,
    "use_sim": False, "threshold": 2, "overrides": {},
    # traslados: list of dicts
    "traslados": [],
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

sim_now = now.replace(
    hour=st.session_state.sim_h,
    minute=st.session_state.sim_m, second=0
) if st.session_state.use_sim else now

# ─────────────────────────────────────────
# TRASLADO IMPACT CALCULATOR
# ─────────────────────────────────────────
def compute_traslado_impacts(traslados, sim_now):
    """
    Returns:
      removed_plates: set of matriculas removed from inventory (salidas activas)
      added_cars: list of {cat, modelo, matricula, avail_dt, avail_str} (entradas ya disponibles o futuras)
    """
    removed_plates = set()
    added_cars     = []

    for t in traslados:
        if t["direction"] == "out":
            # Remove all cars in this truck from inventory
            for car in t["cars"]:
                if car["matricula"]:
                    removed_plates.add(car["matricula"])
        else:  # "in"
            hora_sal  = t["hora"]
            arr_dt    = arrival_dt(hora_sal)
            arr_str   = arr_dt.strftime("%H:%M")
            available = arr_dt <= sim_now
            for car in t["cars"]:
                if car["cat"] and car["matricula"]:
                    added_cars.append({
                        "cat":       car["cat"],
                        "modelo":    car.get("modelo", car["cat"]),
                        "matricula": car["matricula"],
                        "avail_dt":  arr_dt,
                        "avail_str": arr_str,
                        "disponible": available,
                        "conductor": t["conductor"],
                        "base":      t["base"],
                    })
    return removed_plates, added_cars

# ─────────────────────────────────────────
# ASSIGNMENT ENGINE
# ─────────────────────────────────────────
def auto_assign(reservas, garaje, retornos, sim_now, removed_plates, added_cars):
    # Build pools excluding removed plates
    garaje_pool = [dict(c, used=False) for c in garaje if c["matricula"] not in removed_plates]

    ret_pool = []
    for r in retornos:
        if r["matricula"] in removed_plates:
            continue
        av = avail_dt(r["hora"], r["zona"])
        ret_pool.append(dict(r, avail_dt=av, avail_str=avail_str(r["hora"], r["zona"]), used=False))

    # Add incoming transfer cars to garaje_pool (available from arrival time)
    for ac in added_cars:
        if ac["disponible"]:
            garaje_pool.append({
                "cat": ac["cat"], "modelo": ac["modelo"],
                "matricula": ac["matricula"], "used": False,
                "_transfer_in": True,
            })
        else:
            # Treat like a return with avail_dt
            ret_pool.append({
                "cat": ac["cat"], "modelo": ac["modelo"],
                "matricula": ac["matricula"],
                "avail_dt": ac["avail_dt"], "avail_str": ac["avail_str"],
                "zona": "TRASLADO", "hora": ac["avail_str"],
                "used": False, "_transfer_in": True,
            })

    assignments = []
    for res in reservas:
        res_dt   = to_dt(res["hora"])
        cat      = res["cat"]
        assigned = None
        source   = None
        note     = ""
        alt_sugg = []
        modelo_chip = ""

        # 1. Return — exact cat, arrives in time (PRIORITY)
        cands = [r for r in ret_pool
                 if not r["used"] and r["cat"] == cat and r["avail_dt"] <= res_dt]
        cands.sort(key=lambda x: x["avail_dt"])
        if cands:
            r2 = cands[0]; r2["used"] = True
            assigned    = r2["matricula"]
            source      = "retorno"
            modelo_chip = r2["modelo"]
            note        = f"Retorno {r2['hora']} · zona {r2.get('zona','—')} · disp. {r2['avail_str']}"

        # 2. Garaje — exact cat
        if not assigned:
            for c in garaje_pool:
                if not c["used"] and c["cat"] == cat:
                    c["used"] = True
                    assigned    = c["matricula"]
                    source      = "garaje"
                    modelo_chip = c["modelo"]
                    break

        # 3. Garaje — adjacent cat (upgrade)
        if not assigned:
            cat_idx = ALL_CATS.index(cat) if cat in ALL_CATS else -1
            for c in garaje_pool:
                if not c["used"] and c["cat"] in ALL_CATS:
                    ci = ALL_CATS.index(c["cat"])
                    if ci == cat_idx + 1:
                        c["used"] = True
                        assigned    = c["matricula"]
                        source      = "garaje_alt"
                        modelo_chip = c["modelo"]
                        note        = f"Alternativa: {c['cat']} ({c['modelo']})"
                        break

        # 4. Return — adjacent cat arriving in time
        if not assigned:
            cat_idx = ALL_CATS.index(cat) if cat in ALL_CATS else -1
            cands = [r for r in ret_pool
                     if not r["used"]
                     and r["cat"] in ALL_CATS
                     and ALL_CATS.index(r["cat"]) == cat_idx + 1
                     and r["avail_dt"] <= res_dt]
            cands.sort(key=lambda x: x["avail_dt"])
            if cands:
                r2 = cands[0]; r2["used"] = True
                assigned    = r2["matricula"]
                source      = "retorno_alt"
                modelo_chip = r2["modelo"]
                note        = f"Alt. {r2['cat']} ({r2['modelo']}) · retorno {r2['hora']} disp. {r2['avail_str']}"

        # No car → suggestions
        if not assigned:
            for c in garaje_pool:
                if not c["used"]:
                    alt_sugg.append(f"{c['cat']} · {c['modelo']} · {c['matricula']} (garaje)")
                    if len(alt_sugg) >= 3: break
            if len(alt_sugg) < 3:
                for r2 in ret_pool:
                    if not r2["used"]:
                        alt_sugg.append(f"{r2['cat']} · {r2['modelo']} · {r2['matricula']} (retorno {r2.get('hora','—')} → {r2['avail_str']})")
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
            "modelo_chip": modelo_chip,
        })

    return assignments, garaje_pool, ret_pool

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
    st.session_state.sim_h   = st.slider("Hora",   0, 23, st.session_state.sim_h)
    st.session_state.sim_m   = st.slider("Minuto", 0, 59, st.session_state.sim_m)
    st.session_state.use_sim = st.checkbox("Activar simulación", st.session_state.use_sim)
    if st.session_state.use_sim:
        st.info(f"⏱ Simulando **{st.session_state.sim_h:02d}:{st.session_state.sim_m:02d}**")
    st.divider()
    if st.button("🔄 Resetear asignaciones manuales", use_container_width=True):
        st.session_state.overrides = {}; st.rerun()
    st.divider()
    st.markdown("**Leyenda:**")
    st.markdown("🔵 Azul = retorno · 🟠 Naranja = garaje")
    st.markdown("🟡 Amarillo = alternativa · 🔴 Rojo = sin coche")
    st.markdown("🟣 Morado = traslado entrante")

# ─────────────────────────────────────────
# COMPUTE IMPACTS & ASSIGNMENTS
# ─────────────────────────────────────────
removed_plates, added_cars = compute_traslado_impacts(st.session_state.traslados, sim_now)

base_asgn, garaje_pool_used, ret_pool_used = auto_assign(
    DEMO_RESERVAS, DEMO_GARAJE, DEMO_RETORNOS, sim_now, removed_plates, added_cars
)

# Build car selector list
all_cars_sel = []
for c in DEMO_GARAJE:
    if c["matricula"] not in removed_plates:
        all_cars_sel.append({
            "label": f"[{c['cat']}] {c['matricula']} — {c['modelo']} · GARAJE",
            "matricula": c["matricula"], "cat": c["cat"],
        })
for r in DEMO_RETORNOS:
    if r["matricula"] not in removed_plates:
        av = avail_str(r["hora"], r["zona"])
        all_cars_sel.append({
            "label": f"[{r['cat']}] {r['matricula']} — {r['modelo']} · RETORNO {r['hora']} → {av}",
            "matricula": r["matricula"], "cat": r["cat"],
        })
for ac in added_cars:
    all_cars_sel.append({
        "label": f"[{ac['cat']}] {ac['matricula']} — {ac['modelo']} · TRASLADO ENTRADA {ac['avail_str']}",
        "matricula": ac["matricula"], "cat": ac["cat"],
    })

# Apply manual overrides
assignments = []
for i, a in enumerate(base_asgn):
    if i in st.session_state.overrides:
        mat = st.session_state.overrides[i]
        car = next((c for c in all_cars_sel if c["matricula"] == mat), None)
        if car:
            assignments.append({**a, "assigned": mat, "source": "manual",
                                 "note": f"Manual · {car['label'].split('·')[1].strip() if '·' in car['label'] else ''}"})
            continue
    assignments.append(a)

# ─────────────────────────────────────────
# TABS
# ─────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "📋  Asignación de reservas",
    "🚛  Traslados",
    "📊  Stock disponible",
])

# ══════════════════════════════════════════
# TAB 1 — RESERVATIONS
# ══════════════════════════════════════════
with tab1:

    n_ret = sum(1 for a in assignments if a["source"] == "retorno")
    n_gar = sum(1 for a in assignments if a["source"] == "garaje")
    n_alt = sum(1 for a in assignments if a["source"] in ("garaje_alt","retorno_alt"))
    n_man = sum(1 for a in assignments if a["source"] == "manual")
    n_err = sum(1 for a in assignments if not a["assigned"])
    n_trl = sum(1 for ac in added_cars if ac["disponible"])

    # Show transfer impact if any
    if removed_plates or added_cars:
        impact_parts = []
        if removed_plates:
            impact_parts.append(f"🚛 <b>{len(removed_plates)}</b> coches retirados por traslado saliente")
        if added_cars:
            disp_now = sum(1 for ac in added_cars if ac["disponible"])
            impact_parts.append(f"🟣 <b>{len(added_cars)}</b> coches entrantes por traslado ({disp_now} ya disponibles)")
        st.markdown(f'<div class="impact-banner">{"&nbsp;&nbsp;·&nbsp;&nbsp;".join(impact_parts)}</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="sum-bar">
      <div class="sum-item"><div class="sum-val sum-ok">{n_gar+n_ret+n_man}</div><div class="sum-lbl">🟢 Cubiertas</div></div>
      <div class="sum-item"><div class="sum-val sum-ret">{n_ret}</div><div class="sum-lbl">🔵 Retorno</div></div>
      <div class="sum-item"><div class="sum-val sum-gar">{n_gar}</div><div class="sum-lbl">🟠 Garaje</div></div>
      <div class="sum-item"><div class="sum-val sum-warn">{n_alt}</div><div class="sum-lbl">🟡 Alternativa</div></div>
      <div class="sum-item"><div class="sum-val sum-err">{n_err}</div><div class="sum-lbl">🔴 Sin coche</div></div>
      <div class="sum-item"><div class="sum-val sum-neu">{len(assignments)}</div><div class="sum-lbl">Total</div></div>
    </div>
    """, unsafe_allow_html=True)

    from collections import OrderedDict
    groups = OrderedDict()
    for cat in ALL_CATS:
        cat_asgn = [a for a in assignments if a["cat"] == cat]
        if cat_asgn:
            groups[cat] = cat_asgn

    for cat, cat_asgns in groups.items():
        cat_type  = "auto" if cat in CATS_AUTO else "manu"
        type_icon = "⚙️" if cat in CATS_AUTO else "🔧"
        n_ok_cat  = sum(1 for a in cat_asgns if a["assigned"])
        n_err_cat = sum(1 for a in cat_asgns if not a["assigned"])
        err_html  = f'<span style="color:#DC2626;font-weight:700">{n_err_cat} sin coche</span>' if n_err_cat else "0 sin coche"

        st.markdown(f"""
        <div class="model-header">
          <span>{type_icon}</span>
          <span class="model-name">{cat}</span>
          <span class="cat-badge cat-{cat_type}">{CAT_LABELS.get(cat,cat)}</span>
          <span style="font-size:.72rem;color:#6B7280;margin-left:auto">
            {n_ok_cat} cubiertas · {err_html} · {len(cat_asgns)} reservas
          </span>
        </div>
        """, unsafe_allow_html=True)

        # Column headers
        st.markdown("""
        <div style="display:flex;background:#F8FAFC;padding:5px 14px 5px 31px;
                    border-left:1px solid #E2E8F0;border-right:1px solid #E2E8F0;
                    font-size:.63rem;font-weight:700;text-transform:uppercase;
                    letter-spacing:.05em;color:#94A3B8;">
          <span style="min-width:52px">Hora</span>
          <span style="min-width:64px;margin-left:12px">Zona</span>
          <span style="min-width:210px;margin-left:8px">Coche asignado</span>
          <span style="min-width:170px;margin-left:8px">Detalle</span>
          <span style="min-width:150px;margin-left:8px">Cliente</span>
          <span style="margin-left:auto">Hotel</span>
        </div>""", unsafe_allow_html=True)

        for i_global, a in [(j, x) for j, x in enumerate(assignments) if x["cat"] == cat]:
            src = a["source"] or ""
            strip_cls = "strip-ok" if a["assigned"] else "strip-err"

            if not a["assigned"]:
                chip_cls = "chip-none"; chip_txt = "❌ Sin coche"
            elif src == "retorno":
                chip_cls = "chip-ret";  chip_txt = f"🔵 {a['assigned']}"
            elif src == "garaje":
                chip_cls = "chip-gar";  chip_txt = f"🟠 {a['assigned']}"
            elif src in ("garaje_alt","retorno_alt"):
                chip_cls = "chip-alt";  chip_txt = f"🟡 {a['assigned']}"
            elif src == "manual":
                chip_cls = "chip-man";  chip_txt = f"🟢 {a['assigned']}"
            else:
                chip_cls = "chip-none"; chip_txt = "—"

            modelo_span = f'<span style="font-size:.67rem;color:#6B7280;margin-left:5px">{a["modelo_chip"]}</span>' if a.get("modelo_chip") else ""
            note_html   = f'<span style="font-size:.67rem;color:#6B7280">{a["note"]}</span>' if a["note"] else '<span style="color:#CBD5E1;font-size:.67rem">—</span>'

            zona_raw = a.get("agencia","").upper()
            if "AEROP" in zona_raw:    zona_cls="zona-aerop"; zona_lbl="AEROP"
            elif "SHUTT" in zona_raw:  zona_cls="zona-shutt"; zona_lbl="SHUTT"
            else:                       zona_cls="zona-other"; zona_lbl=zona_raw[:6] or "—"

            st.markdown(f"""
            <div class="res-row">
              <div class="strip {strip_cls}"></div>
              <span class="res-time">{a['hora']}</span>
              <span style="margin-left:12px;min-width:64px">
                <span class="zona-pill {zona_cls}">{zona_lbl}</span>
              </span>
              <span style="margin-left:8px;min-width:210px">
                <span class="chip {chip_cls}">{chip_txt}</span>{modelo_span}
              </span>
              <span style="margin-left:8px;min-width:170px">{note_html}</span>
              <span class="res-client" style="margin-left:8px">{a['cliente']}</span>
              <span class="res-hotel">{a.get('hotel','')}</span>
            </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    # Manual reassignment
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("✏️ Cambiar asignación manualmente"):
        res_options = [f"#{i} · {a['hora']} · Cat.{a['cat']} · {a['cliente']}" for i,a in enumerate(assignments)]
        chosen_res  = st.selectbox("Reserva", res_options, key="man_res")
        res_idx     = res_options.index(chosen_res)
        cur_asgn    = assignments[res_idx]
        car_opts    = ["— Sin cambio —"] + [c["label"] for c in all_cars_sel]
        cur_mat     = cur_asgn["assigned"]
        cur_car     = next((c["label"] for c in all_cars_sel if c["matricula"] == cur_mat), None)
        def_idx     = car_opts.index(cur_car) if cur_car in car_opts else 0
        chosen_car  = st.selectbox("Coche a asignar", car_opts, index=def_idx, key="man_car")
        c1b, c2b = st.columns(2)
        with c1b:
            if st.button("✅ Confirmar", use_container_width=True, type="primary"):
                if chosen_car != "— Sin cambio —":
                    mat = next((c["matricula"] for c in all_cars_sel if c["label"] == chosen_car), None)
                    if mat: st.session_state.overrides[res_idx] = mat; st.rerun()
        with c2b:
            if res_idx in st.session_state.overrides:
                if st.button("↩ Restaurar auto", use_container_width=True):
                    del st.session_state.overrides[res_idx]; st.rerun()
        if not cur_asgn["assigned"] and cur_asgn["sugg"]:
            st.warning("Sin coche. Sugerencias:")
            for s in cur_asgn["sugg"]: st.markdown(f"· {s}")

# ══════════════════════════════════════════
# TAB 2 — TRASLADOS
# ══════════════════════════════════════════
with tab2:

    st.markdown("### 🚛 Gestión de traslados entre bases")
    st.caption("Los traslados **salientes** retiran coches del inventario de Son Oms. Los **entrantes** los añaden cuando llegan (hora salida + 1h de viaje).")

    # ── Add new traslado ──────────────────────
    with st.expander("➕ Registrar nuevo traslado", expanded=len(st.session_state.traslados) == 0):

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            t_conductor = st.selectbox("Conductor / Camión", CONDUCTORES, key="t_cond")
        with col_b:
            t_direction = st.radio("Dirección", ["Salida de Son Oms →", "← Entrada a Son Oms"],
                                   key="t_dir", horizontal=True)
        with col_c:
            t_hora = st.time_input("Hora de salida", value=now.replace(hour=8,minute=0,second=0), key="t_hora")
            t_hora_str = t_hora.strftime("%H:%M")

        is_out = "Salida" in t_direction
        if is_out:
            t_base = st.selectbox("Base de destino", BASES, key="t_base_out")
        else:
            t_base = st.selectbox("Base de origen", BASES, key="t_base_in")
            arr = (datetime.combine(now.date(), t_hora) + timedelta(minutes=TRAVEL_MINS)).strftime("%H:%M")
            st.info(f"⏱ Llegada estimada a Son Oms: **{arr}** (salida {t_hora_str} + 60 min)")

        st.markdown("**Coches en el camión** (hasta 4)")
        t_cars = []
        for slot in range(4):
            cs1, cs2, cs3 = st.columns([1,2,2])
            with cs1:
                t_cat = st.selectbox(f"Cat. #{slot+1}", ["—"]+ALL_CATS, key=f"t_cat_{slot}")
            with cs2:
                t_mat = st.text_input(f"Matrícula #{slot+1}", key=f"t_mat_{slot}", placeholder="0000 XXX")
            with cs3:
                t_mod = st.text_input(f"Modelo #{slot+1}", key=f"t_mod_{slot}", placeholder="Seat Ibiza")
            if t_cat != "—" and t_mat.strip():
                t_cars.append({"cat": t_cat, "matricula": t_mat.strip().upper(), "modelo": t_mod.strip() or t_cat})

        if st.button("✅ Añadir traslado", type="primary", use_container_width=True):
            if not t_cars:
                st.error("Añade al menos 1 coche con categoría y matrícula.")
            else:
                st.session_state.traslados.append({
                    "id":        len(st.session_state.traslados),
                    "conductor": t_conductor,
                    "direction": "out" if is_out else "in",
                    "base":      t_base,
                    "hora":      t_hora_str,
                    "cars":      t_cars,
                })
                st.success(f"✅ Traslado registrado — {t_conductor} · {'Salida' if is_out else 'Entrada'} · {len(t_cars)} coches")
                st.rerun()

    st.divider()

    # ── Active traslados ──────────────────────
    if not st.session_state.traslados:
        st.info("No hay traslados registrados hoy. Usa el formulario de arriba para añadir uno.")
    else:
        st.markdown(f"#### Traslados del día — {len(st.session_state.traslados)} registrado(s)")

        # Summary impact
        n_out_cars = len(removed_plates)
        n_in_cars  = len(added_cars)
        n_in_avail = sum(1 for ac in added_cars if ac["disponible"])

        col_t1, col_t2, col_t3 = st.columns(3)
        with col_t1:
            st.markdown(f"""<div class="metric-box crit">
                <div class="ml">Coches retirados hoy</div>
                <div class="mv crit">{n_out_cars}</div>
                <div class="ms">salidas Son Oms</div>
            </div>""", unsafe_allow_html=True)
        with col_t2:
            st.markdown(f"""<div class="metric-box purple">
                <div class="ml">Coches entrantes hoy</div>
                <div class="mv purple">{n_in_cars}</div>
                <div class="ms">{n_in_avail} ya disponibles</div>
            </div>""", unsafe_allow_html=True)
        with col_t3:
            net = n_in_avail - n_out_cars
            net_cls = "ok" if net >= 0 else "crit"
            st.markdown(f"""<div class="metric-box {'neutral' if net==0 else ('crit' if net<0 else '')}">
                <div class="ml">Impacto neto ahora</div>
                <div class="mv {net_cls}">{'+' if net>0 else ''}{net}</div>
                <div class="ms">sobre inventario disponible</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        for i, t in enumerate(st.session_state.traslados):
            is_out_t  = t["direction"] == "out"
            dir_icon  = "🔴 SALIDA →" if is_out_t else "🟢 ← ENTRADA"
            dir_badge = "truck-out" if is_out_t else "truck-in"

            if is_out_t:
                header_detail = f"Son Oms → {t['base']}"
            else:
                arr = arrival_str(t["hora"])
                arrived = arrival_dt(t["hora"]) <= sim_now
                header_detail = f"{t['base']} → Son Oms · llega ~{arr} {'✅ ya llegó' if arrived else '⏳ pendiente'}"

            st.markdown(f"""
            <div class="truck-card">
              <div class="truck-header">
                <span style="font-size:1.3rem">🚛</span>
                <span class="truck-name">{t['conductor']}</span>
                <span class="truck-badge {dir_badge}">{dir_icon}</span>
                <span style="font-size:.8rem;color:#6B7280;margin-left:4px">{header_detail}</span>
                <span style="font-size:.75rem;color:#9CA3AF;margin-left:auto">Salida: {t['hora']} · {len(t['cars'])} coches</span>
              </div>
            """, unsafe_allow_html=True)

            for car in t["cars"]:
                row_cls = "out" if is_out_t else "in"
                st.markdown(f"""
                <div class="traslado-row {row_cls}">
                  <span class="cat-badge cat-{'auto' if car['cat'] in CATS_AUTO else 'manu'}">{car['cat']}</span>
                  <span style="font-family:monospace;font-weight:700;font-size:.8rem;min-width:90px">{car['matricula']}</span>
                  <span style="font-size:.8rem;color:#374151">{car['modelo']}</span>
                  <span style="margin-left:auto;font-size:.72rem;color:#6B7280">
                    {'❌ Retirado del inventario' if is_out_t else f'⏳ Disponible desde {arrival_str(t["hora"])}' if arrival_dt(t["hora"]) > sim_now else '✅ Disponible en Son Oms'}
                  </span>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

            if st.button(f"🗑 Eliminar traslado #{i+1}", key=f"del_t_{i}"):
                st.session_state.traslados.pop(i); st.rerun()

# ══════════════════════════════════════════
# TAB 3 — STOCK DASHBOARD
# ══════════════════════════════════════════
with tab3:

    # Process retornos and reservas
    ret_proc = []
    for r in DEMO_RETORNOS:
        if r["matricula"] in removed_plates:
            continue
        av = avail_dt(r["hora"], r["zona"])
        ret_proc.append({**r, "avail_dt": av, "avail_str": avail_str(r["hora"], r["zona"]),
                          "disponible": av <= sim_now})

    # Add incoming transfer cars to ret_proc
    for ac in added_cars:
        ret_proc.append({
            "cat": ac["cat"], "modelo": ac["modelo"], "matricula": ac["matricula"],
            "avail_dt": ac["avail_dt"], "avail_str": ac["avail_str"],
            "disponible": ac["disponible"], "zona": "TRASLADO", "hora": ac["avail_str"],
        })

    res_proc = [{**s, "realizada": to_dt(s["hora"]) <= sim_now} for s in DEMO_RESERVAS]

    # Effective garaje (excluding removed)
    eff_garaje = [c for c in DEMO_GARAJE if c["matricula"] not in removed_plates]
    # Add already-arrived transfer cars to garaje
    for ac in added_cars:
        if ac["disponible"]:
            eff_garaje.append({"cat": ac["cat"], "modelo": ac["modelo"], "matricula": ac["matricula"]})

    total_garaje = len(eff_garaje)
    ret_disp     = sum(1 for r in ret_proc if r["disponible"])
    sal_hechas   = sum(1 for s in res_proc if s["realizada"])
    sal_pend     = sum(1 for s in res_proc if not s["realizada"])
    stock_now    = total_garaje + ret_disp - sal_hechas
    stock_eod    = total_garaje + len(ret_proc) - len(res_proc)
    thr          = st.session_state.threshold

    if removed_plates or added_cars:
        parts = []
        if removed_plates:
            parts.append(f"🚛 {len(removed_plates)} coches en traslado saliente (excluidos del inventario)")
        if added_cars:
            parts.append(f"🟣 {len(added_cars)} coches en traslado entrante ({sum(1 for ac in added_cars if ac['disponible'])} disponibles ya)")
        st.markdown(f'<div class="impact-banner">{"&nbsp;&nbsp;·&nbsp;&nbsp;".join(parts)}</div>', unsafe_allow_html=True)

    st.caption(f"🟢 Stock a las {sim_now.strftime('%H:%M')} {'(simulado)' if st.session_state.use_sim else '(tiempo real)'}")

    c1,c2,c3,c4,c5 = st.columns(5)
    mets = [
        ("neutral","En garaje (efectivo)", total_garaje, f"base original: {len(DEMO_GARAJE)}", ""),
        ("blue",   "Retornos disponibles", ret_disp,     f"de {len(ret_proc)} retornos hoy", "blue"),
        ("warn",   "Salidas realizadas",   sal_hechas,   "ya entregados", "warn"),
        ("warn",   "Reservas pendientes",  sal_pend,     "por salir hoy", "warn"),
        ("" if stock_now>thr else "crit","Disponible ahora", stock_now, f"fin día est.: {stock_eod}",
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
    st.markdown("#### 📦 Disponibilidad por categoría")

    thead = """<table class="avail-table"><thead><tr>
      <th>Cat.</th><th>Descripción</th><th>Tipo</th>
      <th>Garaje ef.</th><th>Ret. disp.</th><th>Ret. total</th>
      <th>Salidas</th><th>Res. pend.</th>
      <th>🟢 Ahora</th><th>📅 Fin día</th>
    </tr></thead><tbody>"""
    tbody = ""
    for cat in ALL_CATS:
        g_gar  = [c for c in eff_garaje if c["cat"] == cat]
        g_retd = [r for r in ret_proc   if r["cat"] == cat and r["disponible"]]
        g_rett = [r for r in ret_proc   if r["cat"] == cat]
        g_salh = [s for s in res_proc   if s["cat"] == cat and s["realizada"]]
        g_salp = [s for s in res_proc   if s["cat"] == cat and not s["realizada"]]
        if not g_gar and not g_rett and not g_salh and not g_salp: continue
        sn = len(g_gar)+len(g_retd)-len(g_salh)
        se = len(g_gar)+len(g_rett)-len(g_salh)-len(g_salp)
        sn_cls = "avail-ok" if sn>thr else ("avail-warn" if sn>0 else "avail-crit")
        se_cls = "avail-ok" if se>thr else ("avail-warn" if se>0 else "avail-crit")
        tipo   = "auto" if cat in CATS_AUTO else "manu"
        tbody += f"""<tr>
          <td><span class="cat-badge cat-{tipo}">{cat}</span></td>
          <td>{CAT_LABELS.get(cat,cat)}</td>
          <td>{'Automático' if cat in CATS_AUTO else 'Manual'}</td>
          <td>{len(g_gar)}</td><td>{len(g_retd)}</td><td>{len(g_rett)}</td>
          <td>{len(g_salh)}</td><td>{len(g_salp)}</td>
          <td><span class="avail-num {sn_cls}">{sn}</span></td>
          <td><span class="avail-num {se_cls}">{se}</span></td>
        </tr>"""
    st.markdown(thead+tbody+"</tbody></table>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 🔁 Próximos retornos pendientes")
    pend = sorted([r for r in ret_proc if not r["disponible"]], key=lambda x: x["avail_dt"])
    if pend:
        st.dataframe(pd.DataFrame([{
            "Disp. a":   r["avail_str"],
            "Cat.":      r["cat"],
            "Modelo":    r["modelo"],
            "Matrícula": r["matricula"],
            "Zona":      r["zona"],
        } for r in pend]), use_container_width=True, hide_index=True)
    else:
        st.success("✅ Todos los retornos del día ya están disponibles.")

    st.divider()
    e1,e2 = st.columns(2)
    with e1:
        out = io.StringIO()
        w = csv.writer(out)
        w.writerow(["Cat","Descripción","Garaje ef.","Ret.disp","Ret.total","Salidas","Pend.","Stock ahora","Stock fin día"])
        for cat in ALL_CATS:
            g_gar  = [c for c in eff_garaje if c["cat"]==cat]
            g_retd = [r for r in ret_proc if r["cat"]==cat and r["disponible"]]
            g_rett = [r for r in ret_proc if r["cat"]==cat]
            g_salh = [s for s in res_proc if s["cat"]==cat and s["realizada"]]
            g_salp = [s for s in res_proc if s["cat"]==cat and not s["realizada"]]
            if not g_gar and not g_rett: continue
            sn=len(g_gar)+len(g_retd)-len(g_salh)
            se=len(g_gar)+len(g_rett)-len(g_salh)-len(g_salp)
            w.writerow([cat,CAT_LABELS.get(cat,cat),len(g_gar),len(g_retd),len(g_rett),len(g_salh),len(g_salp),sn,se])
        st.download_button("⬇ CSV stock","\ufeff"+out.getvalue(),
            f"roig_stock_{now.strftime('%Y%m%d_%H%M')}.csv","text/csv",use_container_width=True)
    with e2:
        out2=io.StringIO()
        out2.write(f"ROIG FLEET MANAGER — STOCK\n{'='*40}\n{now.strftime('%d/%m/%Y')} {sim_now.strftime('%H:%M')}\n")
        if removed_plates: out2.write(f"Traslados salientes: {len(removed_plates)} coches retirados\n")
        if added_cars:     out2.write(f"Traslados entrantes: {len(added_cars)} coches añadidos\n")
        out2.write("\n")
        for cat in ALL_CATS:
            g_gar=[c for c in eff_garaje if c["cat"]==cat]
            g_retd=[r for r in ret_proc if r["cat"]==cat and r["disponible"]]
            g_rett=[r for r in ret_proc if r["cat"]==cat]
            g_salh=[s for s in res_proc if s["cat"]==cat and s["realizada"]]
            g_salp=[s for s in res_proc if s["cat"]==cat and not s["realizada"]]
            if not g_gar and not g_rett: continue
            sn=len(g_gar)+len(g_retd)-len(g_salh)
            se=len(g_gar)+len(g_rett)-len(g_salh)-len(g_salp)
            estado="SIN STOCK" if sn<=0 else ("BAJO" if sn<=thr else "OK")
            out2.write(f"{cat} {CAT_LABELS.get(cat,''):25} | Ahora:{sn:3} | Fin:{se:3} | {estado}\n")
        st.download_button("📄 TXT resumen",out2.getvalue(),
            f"roig_stock_{now.strftime('%Y%m%d_%H%M')}.txt","text/plain",use_container_width=True)

st.markdown('<div style="text-align:center;padding:14px 0 4px;font-size:.67rem;color:#9CA3AF">Roig Fleet Manager · Modo Demo · Roig Rent a Car</div>', unsafe_allow_html=True)
