"""
Roig Fleet Manager — DEMO INTERACTIVO
Pantalla 1: Asignación interactiva reserva por reserva
Pantalla 2: Dashboard de disponibilidad por categoría
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import io, csv

# ─────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────
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

/* ── Header ── */
.rfm-header {
    background: linear-gradient(135deg, #0A4A39 0%, #0F6E56 100%);
    color: white;
    padding: 16px 24px;
    border-radius: 12px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 4px 16px rgba(15,110,86,0.25);
}
.rfm-header h1  { font-size: 1.2rem; margin: 0; font-weight: 800; }
.rfm-header .sub { font-size: .75rem; opacity: .7; margin-top: 2px; }
.rfm-header .clock { font-size: 1.3rem; font-weight: 800; font-family: monospace; }
.rfm-header .date  { font-size: .7rem; opacity: .65; text-align:right; margin-top:2px; }

/* ── Demo banner ── */
.demo-pill {
    display: inline-block;
    background: #FEF3C7; color: #92400E;
    border: 1px solid #FCD34D;
    border-radius: 20px;
    padding: 4px 12px;
    font-size: .72rem; font-weight: 700;
    margin-bottom: 16px;
}

/* ── Reservation cards ── */
.res-card {
    border-radius: 12px;
    padding: 14px 16px;
    margin-bottom: 10px;
    border: 2px solid;
    transition: all .2s;
    position: relative;
}
.res-card.green {
    background: #F0FDF4;
    border-color: #16A34A;
}
.res-card.red {
    background: #FFF5F5;
    border-color: #DC2626;
}
.res-card.yellow {
    background: #FFFBEB;
    border-color: #D97706;
}
.res-time {
    font-family: monospace; font-weight: 800;
    font-size: 1.1rem; color: #0F6E56;
}
.res-model { font-weight: 700; font-size: .95rem; color: #111827; }
.res-client { font-size: .78rem; color: #6B7280; margin-top: 2px; }
.res-assign {
    font-size: .75rem; font-weight: 700;
    padding: 3px 10px; border-radius: 20px;
    display: inline-block; margin-top: 6px;
}
.assign-ok    { background: #DCFCE7; color: #166534; }
.assign-ret   { background: #DBEAFE; color: #1D4ED8; }
.assign-none  { background: #FEE2E2; color: #991B1B; }
.assign-warn  { background: #FEF3C7; color: #92400E; }

/* ── Status badge ── */
.status-dot {
    width: 12px; height: 12px; border-radius: 50%;
    display: inline-block; margin-right: 6px;
    vertical-align: middle;
}
.dot-green  { background: #16A34A; box-shadow: 0 0 0 3px #DCFCE7; }
.dot-red    { background: #DC2626; box-shadow: 0 0 0 3px #FEE2E2; }
.dot-yellow { background: #D97706; box-shadow: 0 0 0 3px #FEF3C7; }

/* ── Summary header ── */
.summary-bar {
    background: white;
    border: 1px solid #E5E7EB;
    border-radius: 10px;
    padding: 12px 18px;
    margin-bottom: 18px;
    display: flex; gap: 24px; align-items: center;
    box-shadow: 0 1px 3px rgba(0,0,0,.06);
    flex-wrap: wrap;
}
.sum-item { text-align: center; }
.sum-val  { font-size: 1.5rem; font-weight: 800; }
.sum-lbl  { font-size: .65rem; text-transform: uppercase; letter-spacing: .06em; color: #6B7280; font-weight: 700; }
.sum-ok   { color: #16A34A; }
.sum-warn { color: #D97706; }
.sum-err  { color: #DC2626; }

/* ── Dashboard metrics ── */
.metric-box {
    background: white; border: 1px solid #E5E7EB;
    border-radius: 12px; padding: 18px 16px;
    text-align: center; border-top: 4px solid #0F6E56;
    box-shadow: 0 1px 4px rgba(0,0,0,.07);
}
.metric-box.warn { border-top-color: #D97706; }
.metric-box.crit { border-top-color: #DC2626; }
.metric-box.neutral { border-top-color: #9CA3AF; }
.metric-val { font-size: 2.2rem; font-weight: 900; color: #111827; line-height:1; }
.metric-val.ok   { color: #0F6E56; }
.metric-val.warn { color: #D97706; }
.metric-val.crit { color: #DC2626; }
.metric-lbl { font-size: .68rem; font-weight: 700; text-transform: uppercase;
              letter-spacing: .07em; color: #6B7280; margin-bottom: 8px; }
.metric-sub { font-size: .7rem; color: #9CA3AF; margin-top: 4px; }

/* ── Category table ── */
.cat-table { width: 100%; border-collapse: collapse; font-size: .83rem; }
.cat-table th {
    background: #F9FAFB; padding: 9px 12px;
    text-align: left; font-size: .68rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: .05em; color: #6B7280;
    border-bottom: 2px solid #E5E7EB;
}
.cat-table td { padding: 10px 12px; border-bottom: 1px solid #F3F4F6; vertical-align: middle; }
.cat-table tr:hover td { background: #F9FAFB; }
.avail-big { font-size: 1.2rem; font-weight: 800; }
.avail-ok   { color: #0F6E56; }
.avail-warn { color: #D97706; }
.avail-crit { color: #DC2626; }

/* ── Tabs custom ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: #F3F4F6;
    padding: 4px;
    border-radius: 10px;
    margin-bottom: 18px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 7px !important;
    font-weight: 600 !important;
    font-size: .85rem !important;
}
.stTabs [aria-selected="true"] {
    background: white !important;
    box-shadow: 0 1px 3px rgba(0,0,0,.1) !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# DEMO DATA
# ─────────────────────────────────────────
ZONA_OFFSET = {"AEROP": 60, "SHUTT": 45}

DEMO_GARAJE = [
    {"modelo": "Seat Ibiza",        "grupo": "Económico",  "matricula": "4523 MLL"},
    {"modelo": "Seat Ibiza",        "grupo": "Económico",  "matricula": "7821 PKR"},
    {"modelo": "Opel Corsa",        "grupo": "Económico",  "matricula": "3190 HBT"},
    {"modelo": "VW Polo",           "grupo": "Económico",  "matricula": "9902 DFS"},
    {"modelo": "Seat León",         "grupo": "Compacto",   "matricula": "6614 NMW"},
    {"modelo": "Seat León",         "grupo": "Compacto",   "matricula": "1147 QVX"},
    {"modelo": "Ford Focus",        "grupo": "Compacto",   "matricula": "8830 JTL"},
    {"modelo": "Toyota Corolla",    "grupo": "Compacto",   "matricula": "2255 RPK"},
    {"modelo": "Dacia Duster",      "grupo": "SUV",        "matricula": "5571 CBN"},
    {"modelo": "Hyundai Tucson",    "grupo": "SUV",        "matricula": "3348 LVZ"},
    {"modelo": "VW Tiguan",         "grupo": "SUV",        "matricula": "7709 MXQ"},
    {"modelo": "Seat Tarraco",      "grupo": "SUV",        "matricula": "1123 WKF"},
    {"modelo": "Mercedes Clase A",  "grupo": "Premium",    "matricula": "6680 GTY"},
    {"modelo": "BMW Serie 1",       "grupo": "Premium",    "matricula": "4412 BRD"},
    {"modelo": "Ford Galaxy",       "grupo": "Familiar",   "matricula": "9934 CPM"},
    {"modelo": "Seat Alhambra",     "grupo": "Minivan",    "matricula": "2267 NHJ"},
]

DEMO_RETORNOS = [
    {"hora": "07:30", "modelo": "Seat Ibiza",        "matricula": "1198 ZZT", "zona": "AEROP"},
    {"hora": "08:00", "modelo": "VW Polo",            "matricula": "4456 KLM", "zona": "SHUTT"},
    {"hora": "08:45", "modelo": "Seat León",          "matricula": "7723 OPQ", "zona": "AEROP"},
    {"hora": "09:15", "modelo": "Dacia Duster",       "matricula": "3381 RST", "zona": "OFICINA"},
    {"hora": "10:00", "modelo": "Toyota Corolla",     "matricula": "6690 UVW", "zona": "SHUTT"},
    {"hora": "10:30", "modelo": "Hyundai Tucson",     "matricula": "8812 XYZ", "zona": "AEROP"},
    {"hora": "11:00", "modelo": "Ford Focus",         "matricula": "2234 ABC", "zona": "OFICINA"},
    {"hora": "12:00", "modelo": "Opel Corsa",         "matricula": "5567 DEF", "zona": "AEROP"},
    {"hora": "13:30", "modelo": "VW Tiguan",          "matricula": "9901 GHI", "zona": "SHUTT"},
    {"hora": "14:00", "modelo": "Seat Ibiza",         "matricula": "1145 JKL", "zona": "AEROP"},
    {"hora": "15:30", "modelo": "BMW Serie 1",        "matricula": "4478 MNO", "zona": "OFICINA"},
    {"hora": "16:00", "modelo": "Seat Tarraco",       "matricula": "7712 PQR", "zona": "AEROP"},
    {"hora": "17:00", "modelo": "Ford Galaxy",        "matricula": "3345 STU", "zona": "SHUTT"},
    {"hora": "18:30", "modelo": "Mercedes Clase A",   "matricula": "6678 VWX", "zona": "AEROP"},
    {"hora": "19:00", "modelo": "Seat León",          "matricula": "9923 YZA", "zona": "OFICINA"},
]

DEMO_RESERVAS = [
    {"hora": "07:00", "modelo": "Seat Ibiza",        "cliente": "García López, M.",   "grupo": "Económico"},
    {"hora": "07:30", "modelo": "VW Polo",            "cliente": "Müller, H.",         "grupo": "Económico"},
    {"hora": "08:00", "modelo": "Dacia Duster",       "cliente": "Smith, J.",          "grupo": "SUV"},
    {"hora": "08:30", "modelo": "Seat León",          "cliente": "Martínez Ruiz, A.", "grupo": "Compacto"},
    {"hora": "09:00", "modelo": "Hyundai Tucson",     "cliente": "Rossi, G.",          "grupo": "SUV"},
    {"hora": "09:30", "modelo": "Ford Focus",         "cliente": "Dupont, C.",         "grupo": "Compacto"},
    {"hora": "10:00", "modelo": "Toyota Corolla",     "cliente": "Fernández, R.",      "grupo": "Compacto"},
    {"hora": "10:30", "modelo": "Opel Corsa",         "cliente": "Williams, T.",       "grupo": "Económico"},
    {"hora": "11:00", "modelo": "VW Tiguan",          "cliente": "Sánchez Mora, P.",  "grupo": "SUV"},
    {"hora": "12:00", "modelo": "Seat Ibiza",         "cliente": "Johnson, K.",        "grupo": "Económico"},
    {"hora": "13:00", "modelo": "BMW Serie 1",        "cliente": "Nakamura, Y.",       "grupo": "Premium"},
    {"hora": "14:00", "modelo": "Seat León",          "cliente": "Pérez Vidal, L.",   "grupo": "Compacto"},
    {"hora": "15:00", "modelo": "Mercedes Clase A",   "cliente": "Brown, A.",          "grupo": "Premium"},
    {"hora": "16:00", "modelo": "Seat Tarraco",       "cliente": "González, C.",       "grupo": "SUV"},
    {"hora": "17:00", "modelo": "Ford Galaxy",        "cliente": "Hoffmann, E.",       "grupo": "Familiar"},
    {"hora": "18:00", "modelo": "Seat Alhambra",      "cliente": "López Torres, S.",  "grupo": "Minivan"},
    {"hora": "19:00", "modelo": "Dacia Duster",       "cliente": "Davies, R.",         "grupo": "SUV"},
    {"hora": "20:00", "modelo": "VW Polo",            "cliente": "Moreau, F.",         "grupo": "Económico"},
]

# ─────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────
def to_dt(hora: str) -> datetime:
    t = datetime.strptime(hora, "%H:%M")
    return datetime.now().replace(hour=t.hour, minute=t.minute, second=0, microsecond=0)

def avail_dt(hora: str, zona: str) -> datetime:
    offset = ZONA_OFFSET.get(zona.upper().strip(), 0)
    return to_dt(hora) + timedelta(minutes=offset)

def avail_str(hora: str, zona: str) -> str:
    return avail_dt(hora, zona).strftime("%H:%M")

# ─────────────────────────────────────────
# AUTO-ASSIGN ENGINE
# ─────────────────────────────────────────
def auto_assign(reservas, garaje, retornos, sim_now):
    """
    For each reservation, find the best available car:
    1. Garaje units of same model (immediate)
    2. Garaje units of same group (upgrade/downgrade note)
    3. Returns of same model arriving in time
    4. Returns of same group arriving in time
    Priority: exact model > group. Within returns: earliest arriving first.
    Returns list of assignment dicts.
    """
    # Build mutable pools
    garaje_pool = [dict(c, used=False) for c in garaje]

    ret_pool = []
    for r in retornos:
        av = avail_dt(r["hora"], r["zona"])
        ret_pool.append(dict(r,
            avail_dt=av,
            avail_str=avail_str(r["hora"], r["zona"]),
            used=False,
            grupo=next((c["grupo"] for c in garaje if c["modelo"] == r["modelo"]), "—")
        ))

    assignments = []

    for res in reservas:
        res_dt   = to_dt(res["hora"])
        modelo   = res["modelo"]
        grupo    = res["grupo"]
        assigned = None
        source   = None
        note     = ""
        alt_suggestions = []

        # 1. Garaje — exact model
        for c in garaje_pool:
            if not c["used"] and c["modelo"] == modelo:
                c["used"] = True
                assigned  = c["matricula"]
                source    = "garaje"
                break

        # 2. Return — exact model arriving before reservation
        if not assigned:
            candidates = [r for r in ret_pool if not r["used"] and r["modelo"] == modelo and r["avail_dt"] <= res_dt]
            candidates.sort(key=lambda x: x["avail_dt"])
            if candidates:
                r2 = candidates[0]
                r2["used"]  = True
                assigned    = r2["matricula"]
                source      = "retorno"
                note        = f"Retorno {r2['hora']} zona {r2['zona']} · disponible a las {r2['avail_str']}"

        # 3. Garaje — same group (different model)
        if not assigned:
            for c in garaje_pool:
                if not c["used"] and c["grupo"] == grupo:
                    c["used"] = True
                    assigned  = c["matricula"]
                    source    = "garaje_alt"
                    note      = f"Alternativa de grupo {grupo}: {c['modelo']}"
                    break

        # 4. Return — same group arriving in time
        if not assigned:
            candidates = [r for r in ret_pool if not r["used"] and r["grupo"] == grupo and r["avail_dt"] <= res_dt]
            candidates.sort(key=lambda x: x["avail_dt"])
            if candidates:
                r2 = candidates[0]
                r2["used"]  = True
                assigned    = r2["matricula"]
                source      = "retorno_alt"
                note        = f"Alternativa de grupo {grupo}: {r2['modelo']} · retorno {r2['hora']} disponible {r2['avail_str']}"

        # No car found — build suggestions
        if not assigned:
            # Suggest any available garaje car
            for c in garaje_pool:
                if not c["used"]:
                    alt_suggestions.append(f"{c['modelo']} ({c['matricula']}) — garaje")
                    if len(alt_suggestions) >= 3: break
            # Suggest any return arriving today
            if len(alt_suggestions) < 3:
                for r2 in ret_pool:
                    if not r2["used"]:
                        alt_suggestions.append(f"{r2['modelo']} ({r2['matricula']}) — retorno {r2['hora']} disp. {r2['avail_str']}")
                        if len(alt_suggestions) >= 3: break

        assignments.append({
            "hora":        res["hora"],
            "modelo":      modelo,
            "grupo":       grupo,
            "cliente":     res["cliente"],
            "assigned":    assigned,
            "source":      source,
            "note":        note,
            "suggestions": alt_suggestions,
        })

    return assignments, garaje_pool, ret_pool

# ─────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────
now = datetime.now()

if "sim_hour"    not in st.session_state: st.session_state.sim_hour = now.hour
if "sim_min"     not in st.session_state: st.session_state.sim_min  = now.minute
if "use_sim"     not in st.session_state: st.session_state.use_sim  = False
if "threshold"   not in st.session_state: st.session_state.threshold = 2
if "overrides"   not in st.session_state: st.session_state.overrides = {}   # idx -> matricula override

# ─────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────
st.markdown(f"""
<div class="rfm-header">
  <div>
    <h1>🚗 Roig Fleet Manager</h1>
    <div class="sub">Roig Rent a Car · Gestión de flota</div>
  </div>
  <div>
    <div class="clock">{now.strftime('%H:%M:%S')}</div>
    <div class="date">{now.strftime('%A %d %B %Y').capitalize()}</div>
  </div>
</div>
<div class="demo-pill">🎯 MODO DEMO — datos de ejemplo · En producción se cargan desde PDFs con IA</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# SIDEBAR — controls
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Controles")
    st.session_state.threshold = st.number_input("Umbral alerta stock", min_value=0, max_value=10, value=st.session_state.threshold)
    st.divider()
    st.markdown("### ⏱ Simular hora")
    st.caption("Mueve el slider para ver cómo cambian las asignaciones a lo largo del día.")
    st.session_state.sim_hour = st.slider("Hora", 0, 23, st.session_state.sim_hour)
    st.session_state.sim_min  = st.slider("Minuto", 0, 59, st.session_state.sim_min)
    st.session_state.use_sim  = st.checkbox("Activar hora simulada", value=st.session_state.use_sim)
    if st.session_state.use_sim:
        st.info(f"⏱ Simulando **{st.session_state.sim_hour:02d}:{st.session_state.sim_min:02d}**")
    if st.button("🔄 Resetear asignaciones manuales", use_container_width=True):
        st.session_state.overrides = {}
        st.rerun()
    st.divider()
    st.markdown("### ℹ️ Flota demo")
    st.caption(f"**{len(DEMO_GARAJE)}** coches en garaje")
    st.caption(f"**{len(DEMO_RETORNOS)}** retornos programados")
    st.caption(f"**{len(DEMO_RESERVAS)}** reservas hoy")

# ─────────────────────────────────────────
# COMPUTE
# ─────────────────────────────────────────
sim_now = now.replace(
    hour=st.session_state.sim_hour,
    minute=st.session_state.sim_min, second=0
) if st.session_state.use_sim else now

base_assignments, garaje_pool, ret_pool = auto_assign(
    DEMO_RESERVAS, DEMO_GARAJE, DEMO_RETORNOS, sim_now
)

# Apply manual overrides
# Build full car list for selector
all_cars = []
for c in DEMO_GARAJE:
    all_cars.append({"label": f"{c['matricula']} — {c['modelo']} (garaje)", "matricula": c["matricula"], "modelo": c["modelo"], "grupo": c["grupo"], "source": "garaje"})
for r in DEMO_RETORNOS:
    av = avail_str(r["hora"], r["zona"])
    grupo = next((c["grupo"] for c in DEMO_GARAJE if c["modelo"] == r["modelo"]), "—")
    all_cars.append({"label": f"{r['matricula']} — {r['modelo']} (retorno {r['hora']} → disp. {av})", "matricula": r["matricula"], "modelo": r["modelo"], "grupo": grupo, "source": f"retorno {r['hora']}", "avail": av})

# ─────────────────────────────────────────
# TABS
# ─────────────────────────────────────────
tab1, tab2 = st.tabs(["📋  Asignación de reservas", "📊  Stock disponible para vender"])

# ══════════════════════════════════════════
# TAB 1 — RESERVATIONS
# ══════════════════════════════════════════
with tab1:

    # Re-apply overrides on top of auto assignments
    assignments = []
    for i, a in enumerate(base_assignments):
        if i in st.session_state.overrides:
            mat = st.session_state.overrides[i]
            car = next((c for c in all_cars if c["matricula"] == mat), None)
            if car:
                src = car["source"]
                note = f"Asignación manual · {car['modelo']}"
                if "retorno" in src:
                    note += f" · disp. {car.get('avail','')}"
                assignments.append({**a, "assigned": mat, "source": "manual", "note": note})
            else:
                assignments.append(a)
        else:
            assignments.append(a)

    # Summary counts
    n_ok   = sum(1 for a in assignments if a["assigned"] and a["source"] not in ["garaje_alt","retorno_alt"])
    n_alt  = sum(1 for a in assignments if a["assigned"] and a["source"] in ["garaje_alt","retorno_alt"])
    n_man  = sum(1 for a in assignments if a["source"] == "manual")
    n_err  = sum(1 for a in assignments if not a["assigned"])

    st.markdown(f"""
    <div class="summary-bar">
      <div class="sum-item">
        <div class="sum-val sum-ok">{n_ok + n_man}</div>
        <div class="sum-lbl">🟢 Cubiertas</div>
      </div>
      <div class="sum-item">
        <div class="sum-val sum-warn">{n_alt}</div>
        <div class="sum-lbl">🟡 Alternativa</div>
      </div>
      <div class="sum-item">
        <div class="sum-val sum-err">{n_err}</div>
        <div class="sum-lbl">🔴 Sin coche</div>
      </div>
      <div class="sum-item">
        <div class="sum-val" style="color:#6B7280">{len(assignments)}</div>
        <div class="sum-lbl">Total reservas</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── One card per reservation ──────────────
    for i, a in enumerate(assignments):
        src    = a["source"] or ""
        ok     = bool(a["assigned"])
        is_alt = src in ["garaje_alt", "retorno_alt"]
        is_man = src == "manual"

        # Card color
        if not ok:
            card_cls = "red"
        elif is_alt:
            card_cls = "yellow"
        else:
            card_cls = "green"

        # Assignment badge
        if not ok:
            badge_cls = "assign-none"
            badge_txt = "❌ Sin coche disponible"
        elif is_man:
            badge_cls = "assign-ok"
            badge_txt = f"✅ {a['assigned']} (manual)"
        elif src == "garaje":
            badge_cls = "assign-ok"
            badge_txt = f"✅ {a['assigned']} — garaje"
        elif src == "retorno":
            badge_cls = "assign-ret"
            badge_txt = f"🔁 {a['assigned']} — retorno"
        elif is_alt:
            badge_cls = "assign-warn"
            badge_txt = f"⚠️ {a['assigned']} — alternativa"
        else:
            badge_cls = "assign-ok"
            badge_txt = f"✅ {a['assigned']}"

        col_card, col_ctrl = st.columns([3, 2])

        with col_card:
            note_html = f'<div style="font-size:.73rem;color:#6B7280;margin-top:4px">ℹ️ {a["note"]}</div>' if a["note"] else ""
            st.markdown(f"""
            <div class="res-card {card_cls}">
              <span class="status-dot dot-{'green' if card_cls=='green' else 'red' if card_cls=='red' else 'yellow'}"></span>
              <span class="res-time">{a['hora']}</span>
              &nbsp;&nbsp;
              <span class="res-model">{a['modelo']}</span>
              <span style="font-size:.72rem;background:#F3F4F6;border-radius:4px;padding:2px 7px;margin-left:8px;color:#6B7280">{a['grupo']}</span>
              <div class="res-client">👤 {a['cliente']}</div>
              <span class="res-assign {badge_cls}">{badge_txt}</span>
              {note_html}
            </div>
            """, unsafe_allow_html=True)

        with col_ctrl:
            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

            # Car selector — show all cars, current selection first
            car_labels = [c["label"] for c in all_cars]
            # Find current assigned index
            current_mat = a["assigned"]
            current_label = next((c["label"] for c in all_cars if c["matricula"] == current_mat), None)
            default_idx = car_labels.index(current_label) + 1 if current_label in car_labels else 0

            options = ["— Seleccionar coche manualmente —"] + car_labels
            chosen = st.selectbox(
                f"Asignar coche #{i+1}",
                options=options,
                index=default_idx,
                key=f"sel_{i}",
                label_visibility="collapsed",
            )

            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("✅ Asignar", key=f"btn_assign_{i}", use_container_width=True):
                    if chosen != "— Seleccionar coche manualmente —":
                        mat = next((c["matricula"] for c in all_cars if c["label"] == chosen), None)
                        if mat:
                            st.session_state.overrides[i] = mat
                            st.rerun()
            with col_btn2:
                if i in st.session_state.overrides:
                    if st.button("↩ Auto", key=f"btn_reset_{i}", use_container_width=True):
                        del st.session_state.overrides[i]
                        st.rerun()

            # Show suggestions if no car found
            if not ok and a["suggestions"]:
                st.markdown("<div style='font-size:.72rem;color:#B45309;margin-top:4px'><b>Sugerencias:</b></div>", unsafe_allow_html=True)
                for s in a["suggestions"]:
                    st.markdown(f"<div style='font-size:.7rem;color:#6B7280'>· {s}</div>", unsafe_allow_html=True)

        st.markdown("<div style='height:2px'></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════
# TAB 2 — DASHBOARD
# ══════════════════════════════════════════
with tab2:

    # Recalculate stock ignoring assignments (pure inventory view)
    ret_proc = []
    for r in DEMO_RETORNOS:
        av = avail_dt(r["hora"], r["zona"])
        ret_proc.append({**r,
            "avail_dt": av,
            "avail_str": avail_str(r["hora"], r["zona"]),
            "disponible": av <= sim_now,
            "grupo": next((c["grupo"] for c in DEMO_GARAJE if c["modelo"] == r["modelo"]), "—"),
        })

    res_proc = []
    for s in DEMO_RESERVAS:
        res_proc.append({**s, "realizada": to_dt(s["hora"]) <= sim_now})

    # Global metrics
    total_garaje  = len(DEMO_GARAJE)
    ret_disp_now  = sum(1 for r in ret_proc if r["disponible"])
    ret_total     = len(ret_proc)
    sal_hechas    = sum(1 for s in res_proc if s["realizada"])
    sal_pend      = sum(1 for s in res_proc if not s["realizada"])
    stock_now     = total_garaje + ret_disp_now - sal_hechas
    stock_eod     = total_garaje + ret_total - len(res_proc)

    thr = st.session_state.threshold
    st.caption(f"🟢 Datos a las {sim_now.strftime('%H:%M')} {'(simulado)' if st.session_state.use_sim else '(tiempo real)'}")

    # Metric cards
    c1, c2, c3, c4, c5 = st.columns(5)
    metrics = [
        ("neutral", "Coches en garaje",          total_garaje,   "inventario base",              ""),
        ("",        "Retornos disponibles",       ret_disp_now,   f"de {ret_total} retornos hoy", "ok"),
        ("warn",    "Salidas realizadas",         sal_hechas,     "ya entregados",                "warn"),
        ("warn",    "Reservas pendientes",        sal_pend,       "por salir hoy",                "warn"),
        ("" if stock_now > thr else "crit", "Stock disponible ahora", stock_now, f"fin de día: {stock_eod}", "ok" if stock_now > thr else "crit"),
    ]
    for col, (card_cls, lbl, val, sub, val_cls) in zip([c1,c2,c3,c4,c5], metrics):
        with col:
            st.markdown(f"""<div class="metric-box {card_cls}">
                <div class="metric-lbl">{lbl}</div>
                <div class="metric-val {val_cls}">{val}</div>
                <div class="metric-sub">{sub}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── By category ───────────────────────────
    st.markdown("#### 📦 Disponibilidad por categoría — lo que puedes vender ahora")

    grupos = sorted(set(c["grupo"] for c in DEMO_GARAJE))
    cat_rows = []
    for g in grupos:
        g_garaje  = [c for c in DEMO_GARAJE if c["grupo"] == g]
        g_ret_d   = [r for r in ret_proc   if r["grupo"] == g and r["disponible"]]
        g_ret_t   = [r for r in ret_proc   if r["grupo"] == g]
        g_sal_h   = [s for s in res_proc   if s["grupo"] == g and s["realizada"]]
        g_sal_p   = [s for s in res_proc   if s["grupo"] == g and not s["realizada"]]

        g_stock_now = len(g_garaje) + len(g_ret_d) - len(g_sal_h)
        g_stock_eod = len(g_garaje) + len(g_ret_t) - len(g_sal_h) - len(g_sal_p)

        cat_rows.append({
            "grupo":       g,
            "garaje":      len(g_garaje),
            "ret_disp":    len(g_ret_d),
            "ret_total":   len(g_ret_t),
            "sal_hechas":  len(g_sal_h),
            "sal_pend":    len(g_sal_p),
            "stock_now":   g_stock_now,
            "stock_eod":   g_stock_eod,
        })

    # Render table
    header_html = """
    <table class="cat-table">
    <thead><tr>
      <th>Categoría</th>
      <th>Garaje</th>
      <th>Ret. disp.</th>
      <th>Ret. total</th>
      <th>Salidas hechas</th>
      <th>Res. pendientes</th>
      <th>🟢 Disponible ahora</th>
      <th>📅 Fin de día</th>
    </tr></thead><tbody>
    """
    rows_html = ""
    for r2 in cat_rows:
        sn = r2["stock_now"]
        se = r2["stock_eod"]
        sn_cls = "avail-ok" if sn > thr else ("avail-warn" if sn > 0 else "avail-crit")
        se_cls = "avail-ok" if se > thr else ("avail-warn" if se > 0 else "avail-crit")
        rows_html += f"""<tr>
          <td><strong>{r2['grupo']}</strong></td>
          <td>{r2['garaje']}</td>
          <td>{r2['ret_disp']}</td>
          <td>{r2['ret_total']}</td>
          <td>{r2['sal_hechas']}</td>
          <td>{r2['sal_pend']}</td>
          <td><span class="avail-big {sn_cls}">{sn}</span></td>
          <td><span class="avail-big {se_cls}">{se}</span></td>
        </tr>"""

    st.markdown(header_html + rows_html + "</tbody></table>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Próximos retornos ─────────────────────
    st.markdown("#### 🔁 Próximos retornos disponibles")
    pending_rets = sorted([r for r in ret_proc if not r["disponible"]], key=lambda x: x["avail_dt"])
    if pending_rets:
        pr_df = pd.DataFrame([{
            "Disponible a":  r["avail_str"],
            "Hora retorno":  r["hora"],
            "Modelo":        r["modelo"],
            "Matrícula":     r["matricula"],
            "Zona":          r["zona"],
            "Categoría":     r["grupo"],
        } for r in pending_rets])
        st.dataframe(pr_df, use_container_width=True, hide_index=True)
    else:
        st.success("✅ Todos los retornos del día ya están disponibles.")

    st.divider()

    # ── Export ────────────────────────────────
    st.markdown("**📥 Exportar**")
    ex1, ex2 = st.columns(2)
    with ex1:
        out = io.StringIO()
        w   = csv.writer(out)
        w.writerow(["Categoría","Garaje","Ret.disp.","Ret.total","Salidas","Res.pend.","Stock ahora","Stock fin día"])
        for r2 in cat_rows:
            w.writerow([r2["grupo"], r2["garaje"], r2["ret_disp"], r2["ret_total"],
                        r2["sal_hechas"], r2["sal_pend"], r2["stock_now"], r2["stock_eod"]])
        st.download_button("⬇ Descargar CSV stock",
            data="\ufeff" + out.getvalue(),
            file_name=f"roig_stock_{now.strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv", use_container_width=True)
    with ex2:
        out2 = io.StringIO()
        out2.write(f"ROIG FLEET MANAGER — STOCK POR CATEGORÍA\n{'='*45}\n")
        out2.write(f"Fecha: {now.strftime('%d/%m/%Y')}  Hora: {sim_now.strftime('%H:%M')}\n\n")
        for r2 in cat_rows:
            sn = r2["stock_now"]; se = r2["stock_eod"]
            estado = "SIN STOCK" if sn <= 0 else ("BAJO" if sn <= thr else "OK")
            out2.write(f"{r2['grupo']:15} | Ahora: {sn:3} | Fin día: {se:3} | {estado}\n")
        st.download_button("📄 Descargar TXT",
            data=out2.getvalue(),
            file_name=f"roig_stock_{now.strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain", use_container_width=True)

st.markdown("""
<div style="text-align:center;padding:18px 0 6px;font-size:.7rem;color:#9CA3AF">
  Roig Fleet Manager · Modo Demo · Roig Rent a Car
</div>
""", unsafe_allow_html=True)
