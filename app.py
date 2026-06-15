"""
Roig Fleet Manager — DEMO MODE
Streamlit · Roig Rent a Car
Datos de ejemplo pregrabados · Sin API · Sin PDFs
"""

import streamlit as st
import pandas as pd
import csv
import io
from datetime import datetime, timedelta

# ─────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────
st.set_page_config(
    page_title="Roig Fleet Manager · Demo",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────
st.markdown("""
<style>
#MainMenu, footer { visibility: hidden; }

.rfm-header {
    background: linear-gradient(135deg, #0A4A39 0%, #0F6E56 100%);
    color: white;
    padding: 18px 24px;
    border-radius: 12px;
    margin-bottom: 22px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 4px 12px rgba(15,110,86,0.3);
}
.rfm-header h1 { font-size: 1.25rem; margin: 0; font-weight: 800; letter-spacing: -.01em; }
.rfm-header .sub { font-size: .78rem; opacity: .75; margin-top: 2px; }
.rfm-header .clock { font-size: 1.4rem; font-weight: 800; font-family: monospace; }
.rfm-header .date  { font-size: .72rem; opacity: .7; text-align: right; margin-top: 2px; }

.demo-banner {
    background: #FEF3C7;
    border: 1.5px solid #FCD34D;
    border-radius: 8px;
    padding: 10px 16px;
    font-size: .82rem;
    color: #92400E;
    margin-bottom: 18px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.metric-box {
    background: white;
    border: 1px solid #E5E7EB;
    border-radius: 12px;
    padding: 18px 16px;
    text-align: center;
    border-top: 4px solid #0F6E56;
    box-shadow: 0 1px 4px rgba(0,0,0,.07);
}
.metric-box.warn    { border-top-color: #B45309; }
.metric-box.crit    { border-top-color: #B91C1C; }
.metric-box.neutral { border-top-color: #9CA3AF; }
.metric-val { font-size: 2.4rem; font-weight: 900; color: #111827; line-height: 1; }
.metric-val.ok   { color: #0F6E56; }
.metric-val.warn { color: #B45309; }
.metric-val.crit { color: #B91C1C; }
.metric-lbl { font-size: .7rem; font-weight: 700; text-transform: uppercase;
              letter-spacing: .07em; color: #6B7280; margin-bottom: 8px; }
.metric-sub { font-size: .72rem; color: #9CA3AF; margin-top: 5px; }

.alert-crit {
    background: #FFF5F5; border-left: 4px solid #B91C1C;
    border-radius: 8px; padding: 12px 16px; margin-bottom: 10px;
    font-size: .83rem;
}
.alert-warn {
    background: #FFFBEB; border-left: 4px solid #B45309;
    border-radius: 8px; padding: 12px 16px; margin-bottom: 10px;
    font-size: .83rem;
}
.alert-title { font-weight: 700; margin-bottom: 5px; font-size: .85rem; }
.alert-crit .alert-title { color: #B91C1C; }
.alert-warn .alert-title { color: #B45309; }
.alert-item { padding: 2px 0; color: #374151; }
.alert-item::before { content: '· '; color: #9CA3AF; }

.sec-lbl {
    font-size: .69rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: .08em; color: #6B7280; margin-bottom: 10px;
    padding-bottom: 6px; border-bottom: 1px solid #E5E7EB;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# DEMO DATA — realistic Mallorca fleet
# ─────────────────────────────────────────
DEMO_GARAJE = [
    {"modelo": "Seat Ibiza",       "grupo": "Económico",  "matricula": "4523 MLL"},
    {"modelo": "Seat Ibiza",       "grupo": "Económico",  "matricula": "7821 PKR"},
    {"modelo": "Opel Corsa",       "grupo": "Económico",  "matricula": "3190 HBT"},
    {"modelo": "VW Polo",          "grupo": "Económico",  "matricula": "9902 DFS"},
    {"modelo": "Seat León",        "grupo": "Compacto",   "matricula": "6614 NMW"},
    {"modelo": "Seat León",        "grupo": "Compacto",   "matricula": "1147 QVX"},
    {"modelo": "Ford Focus",       "grupo": "Compacto",   "matricula": "8830 JTL"},
    {"modelo": "Toyota Corolla",   "grupo": "Compacto",   "matricula": "2255 RPK"},
    {"modelo": "Dacia Duster",     "grupo": "SUV",        "matricula": "5571 CBN"},
    {"modelo": "Hyundai Tucson",   "grupo": "SUV",        "matricula": "3348 LVZ"},
    {"modelo": "VW Tiguan",        "grupo": "SUV",        "matricula": "7709 MXQ"},
    {"modelo": "Seat Tarraco",     "grupo": "SUV",        "matricula": "1123 WKF"},
    {"modelo": "Mercedes Clase A", "grupo": "Premium",    "matricula": "6680 GTY"},
    {"modelo": "BMW Serie 1",      "grupo": "Premium",    "matricula": "4412 BRD"},
    {"modelo": "Ford Galaxy",      "grupo": "Familiar",   "matricula": "9934 CPM"},
    {"modelo": "Seat Alhambra",    "grupo": "Minivan",    "matricula": "2267 NHJ"},
]

DEMO_RETORNOS = [
    {"hora": "07:30", "modelo": "Seat Ibiza",       "matricula": "1198 ZZT", "zona": "AEROP"},
    {"hora": "08:00", "modelo": "VW Polo",           "matricula": "4456 KLM", "zona": "SHUTT"},
    {"hora": "08:45", "modelo": "Seat León",         "matricula": "7723 OPQ", "zona": "AEROP"},
    {"hora": "09:15", "modelo": "Dacia Duster",      "matricula": "3381 RST", "zona": "OFICINA"},
    {"hora": "10:00", "modelo": "Toyota Corolla",    "matricula": "6690 UVW", "zona": "SHUTT"},
    {"hora": "10:30", "modelo": "Hyundai Tucson",    "matricula": "8812 XYZ", "zona": "AEROP"},
    {"hora": "11:00", "modelo": "Ford Focus",        "matricula": "2234 ABC", "zona": "OFICINA"},
    {"hora": "12:00", "modelo": "Opel Corsa",        "matricula": "5567 DEF", "zona": "AEROP"},
    {"hora": "13:30", "modelo": "VW Tiguan",         "matricula": "9901 GHI", "zona": "SHUTT"},
    {"hora": "14:00", "modelo": "Seat Ibiza",        "matricula": "1145 JKL", "zona": "AEROP"},
    {"hora": "15:30", "modelo": "BMW Serie 1",       "matricula": "4478 MNO", "zona": "OFICINA"},
    {"hora": "16:00", "modelo": "Seat Tarraco",      "matricula": "7712 PQR", "zona": "AEROP"},
    {"hora": "17:00", "modelo": "Ford Galaxy",       "matricula": "3345 STU", "zona": "SHUTT"},
    {"hora": "18:30", "modelo": "Mercedes Clase A",  "matricula": "6678 VWX", "zona": "AEROP"},
    {"hora": "19:00", "modelo": "Seat León",         "matricula": "9923 YZA", "zona": "OFICINA"},
]

DEMO_RESERVAS = [
    {"hora": "07:00", "modelo": "Seat Ibiza",       "cliente": "García López, M.",    "matricula": ""},
    {"hora": "07:30", "modelo": "VW Polo",           "cliente": "Müller, H.",          "matricula": ""},
    {"hora": "08:00", "modelo": "Dacia Duster",      "cliente": "Smith, J.",           "matricula": "5571 CBN"},
    {"hora": "08:30", "modelo": "Seat León",         "cliente": "Martínez Ruiz, A.",   "matricula": ""},
    {"hora": "09:00", "modelo": "Hyundai Tucson",    "cliente": "Rossi, G.",           "matricula": "3348 LVZ"},
    {"hora": "09:30", "modelo": "Ford Focus",        "cliente": "Dupont, C.",          "matricula": ""},
    {"hora": "10:00", "modelo": "Toyota Corolla",    "cliente": "Fernández, R.",       "matricula": "2255 RPK"},
    {"hora": "10:30", "modelo": "Opel Corsa",        "cliente": "Williams, T.",        "matricula": ""},
    {"hora": "11:00", "modelo": "VW Tiguan",         "cliente": "Sánchez Mora, P.",    "matricula": "7709 MXQ"},
    {"hora": "12:00", "modelo": "Seat Ibiza",        "cliente": "Johnson, K.",         "matricula": ""},
    {"hora": "13:00", "modelo": "BMW Serie 1",       "cliente": "Nakamura, Y.",        "matricula": "4412 BRD"},
    {"hora": "14:00", "modelo": "Seat León",         "cliente": "Pérez Vidal, L.",     "matricula": ""},
    {"hora": "15:00", "modelo": "Mercedes Clase A",  "cliente": "Brown, A.",           "matricula": "6680 GTY"},
    {"hora": "16:00", "modelo": "Seat Tarraco",      "cliente": "González, C.",        "matricula": ""},
    {"hora": "17:00", "modelo": "Ford Galaxy",       "cliente": "Hoffmann, E.",        "matricula": "9934 CPM"},
    {"hora": "18:00", "modelo": "Seat Alhambra",     "cliente": "López Torres, S.",    "matricula": "2267 NHJ"},
    {"hora": "19:00", "modelo": "Dacia Duster",      "cliente": "Davies, R.",          "matricula": ""},
    {"hora": "20:00", "modelo": "VW Polo",           "cliente": "Moreau, F.",          "matricula": ""},
]

# ─────────────────────────────────────────
# CORE LOGIC
# ─────────────────────────────────────────
ZONA_OFFSET = {"AEROP": 60, "SHUTT": 45}

def parse_time(s: str) -> datetime:
    t = datetime.strptime(s, "%H:%M")
    return datetime.now().replace(hour=t.hour, minute=t.minute, second=0, microsecond=0)

def available_time(hora: str, zona: str) -> datetime:
    offset = ZONA_OFFSET.get(zona.upper(), 0)
    return parse_time(hora) + timedelta(minutes=offset)

def calc_stock(now: datetime, threshold: int) -> dict:
    # ── Build per-model garaje inventory ──
    garaje_map = {}
    plates_map = {}
    for c in DEMO_GARAJE:
        m = c["modelo"]
        garaje_map[m] = garaje_map.get(m, 0) + 1
        plates_map.setdefault(m, []).append(c["matricula"])

    all_models = sorted(set(
        list(garaje_map.keys()) +
        [r["modelo"] for r in DEMO_RETORNOS] +
        [s["modelo"] for s in DEMO_RESERVAS]
    ))

    # ── Process retornos ──
    retornos_proc = []
    for r in DEMO_RETORNOS:
        av = available_time(r["hora"], r["zona"])
        disponible = av <= now
        retornos_proc.append({**r, "hora_disponible": av.strftime("%H:%M"), "disponible_ahora": disponible})

    # ── Process salidas ──
    salidas_proc = []
    for s in DEMO_RESERVAS:
        realizada = parse_time(s["hora"]) <= now
        salidas_proc.append({**s, "realizada": realizada})

    # ── Per-model aggregation ──
    modelos_result = []
    for modelo in all_models:
        garaje      = garaje_map.get(modelo, 0)
        grupo       = next((c["grupo"] for c in DEMO_GARAJE if c["modelo"] == modelo), "—")
        plates      = plates_map.get(modelo, [])

        ret_total   = [r for r in retornos_proc if r["modelo"] == modelo]
        ret_disp    = [r for r in ret_total if r["disponible_ahora"]]

        sal_hechas  = [s for s in salidas_proc if s["modelo"] == modelo and s["realizada"]]
        sal_pend    = [s for s in salidas_proc if s["modelo"] == modelo and not s["realizada"]]

        stock_ahora = garaje + len(ret_disp) - len(sal_hechas)
        stock_eod   = garaje + len(ret_total) - len(sal_hechas) - len(sal_pend)

        modelos_result.append({
            "grupo":                     grupo,
            "modelo":                    modelo,
            "matriculas_garaje":         plates,
            "garaje":                    garaje,
            "retornos_disponibles_ahora": len(ret_disp),
            "retornos_total_hoy":        len(ret_total),
            "salidas_hechas":            len(sal_hechas),
            "reservas_pendientes":       len(sal_pend),
            "stock_ahora":               stock_ahora,
            "stock_fin_dia":             stock_eod,
        })

    # ── Global summary ──
    resumen = {
        "total_garaje":                    len(DEMO_GARAJE),
        "total_retornos_disponibles_ahora": sum(1 for r in retornos_proc if r["disponible_ahora"]),
        "total_retornos_hoy":              len(retornos_proc),
        "total_salidas_hechas":            sum(1 for s in salidas_proc if s["realizada"]),
        "total_reservas_pendientes":       sum(1 for s in salidas_proc if not s["realizada"]),
        "stock_disponible_ahora":          len(DEMO_GARAJE) + sum(1 for r in retornos_proc if r["disponible_ahora"]) - sum(1 for s in salidas_proc if s["realizada"]),
        "stock_fin_dia":                   len(DEMO_GARAJE) + len(retornos_proc) - len(salidas_proc),
    }

    return {
        "resumen":  resumen,
        "modelos":  modelos_result,
        "retornos": retornos_proc,
        "salidas":  salidas_proc,
    }

def export_csv(result: dict, threshold: int) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Grupo","Modelo","Matrículas garaje","Garaje",
                     "Ret. disp. ahora","Ret. total hoy","Salidas hechas",
                     "Reservas pendientes","Stock ahora","Stock fin día","Estado"])
    for m in result["modelos"]:
        stock  = m["stock_ahora"]
        estado = "SIN STOCK" if stock <= 0 else ("BAJO" if stock <= threshold else "OK")
        writer.writerow([
            m["grupo"], m["modelo"], " · ".join(m["matriculas_garaje"]),
            m["garaje"], m["retornos_disponibles_ahora"], m["retornos_total_hoy"],
            m["salidas_hechas"], m["reservas_pendientes"],
            m["stock_ahora"], m["stock_fin_dia"], estado,
        ])
    return output.getvalue()

def export_txt(result: dict, now: datetime, threshold: int) -> str:
    r  = result["resumen"]
    t  = "ROIG FLEET MANAGER — RESUMEN DE STOCK\n"
    t += "=" * 50 + "\n"
    t += f"Empresa : Roig Rent a Car\n"
    t += f"Fecha   : {now.strftime('%A %d de %B de %Y')}\n"
    t += f"Hora    : {now.strftime('%H:%M:%S')}\n\n"
    t += "RESUMEN GLOBAL\n" + "-" * 30 + "\n"
    t += f"Garaje (inventario base)      : {r['total_garaje']}\n"
    t += f"Retornos disponibles ahora    : {r['total_retornos_disponibles_ahora']}\n"
    t += f"Retornos totales hoy          : {r['total_retornos_hoy']}\n"
    t += f"Salidas ya realizadas         : {r['total_salidas_hechas']}\n"
    t += f"Reservas pendientes           : {r['total_reservas_pendientes']}\n"
    t += f"STOCK DISPONIBLE AHORA        : {r['stock_disponible_ahora']}\n"
    t += f"STOCK ESTIMADO FIN DE DÍA     : {r['stock_fin_dia']}\n\n"
    t += "DETALLE POR MODELO\n" + "-" * 50 + "\n"
    for m in result["modelos"]:
        stock  = m["stock_ahora"]
        estado = "[SIN STOCK]" if stock <= 0 else ("[BAJO]" if stock <= threshold else "[OK]")
        t += f"\n{m['modelo']} ({m['grupo']}) {estado}\n"
        if m["matriculas_garaje"]:
            t += f"  Matrículas: {', '.join(m['matriculas_garaje'])}\n"
        t += f"  Garaje: {m['garaje']} | Ret. disp: {m['retornos_disponibles_ahora']}/{m['retornos_total_hoy']}"
        t += f" | Salidas: {m['salidas_hechas']} | Pendientes: {m['reservas_pendientes']}\n"
        t += f"  Stock ahora: {m['stock_ahora']} | Fin de día: {m['stock_fin_dia']}\n"
    t += "\n" + "-" * 50 + "\nGenerado por Roig Fleet Manager · MODO DEMO\n"
    return t

# ─────────────────────────────────────────
# RENDER
# ─────────────────────────────────────────
now = datetime.now()

# Header
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
""", unsafe_allow_html=True)

# Demo banner
st.markdown("""
<div class="demo-banner">
  🎯 <strong>MODO DEMO</strong> — Datos de ejemplo de una flota real en Mallorca.
  En producción, estos datos se extraen automáticamente de los PDFs diarios con IA.
</div>
""", unsafe_allow_html=True)

# ── SIDEBAR ──────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configuración demo")
    threshold = st.number_input("Umbral alerta stock bajo", min_value=0, max_value=20, value=2,
                                 help="Alerta cuando el stock de un modelo cae a este número o menos")
    
    st.divider()
    st.markdown("### 🕐 Simular hora del día")
    st.caption("Mueve el slider para ver cómo cambia el stock a lo largo del día.")
    sim_hour = st.slider("Hora simulada", 0, 23, now.hour, format="%d:00h")
    sim_min  = st.slider("Minuto", 0, 59, now.minute)
    use_sim  = st.checkbox("Usar hora simulada", value=False)

    if use_sim:
        sim_now = now.replace(hour=sim_hour, minute=sim_min, second=0)
        st.info(f"⏱ Simulando: **{sim_now.strftime('%H:%M')}**")
    else:
        sim_now = now

    st.divider()
    st.markdown("### ℹ️ Flota demo")
    st.caption(f"**{len(DEMO_GARAJE)}** coches en garaje")
    st.caption(f"**{len(DEMO_RETORNOS)}** retornos programados")
    st.caption(f"**{len(DEMO_RESERVAS)}** reservas del día")
    st.caption("Zonas: AEROP (+60 min) · SHUTT (+45 min) · OFICINA (inmediato)")

# ── CALCULATE ─────────────────────────────
result = calc_stock(sim_now, threshold)
r      = result["resumen"]
modelos = result["modelos"]

calc_label = sim_now.strftime("Calculado a las %H:%M:%S") + (" (simulado)" if use_sim else " (tiempo real)")
st.caption(f"🟢 {calc_label}")

# ── METRICS ───────────────────────────────
alert_count = len([m for m in modelos if m["stock_ahora"] <= 0])
warn_count  = len([m for m in modelos if 0 < m["stock_ahora"] <= threshold])

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""<div class="metric-box neutral">
        <div class="metric-lbl">En garaje</div>
        <div class="metric-val">{r['total_garaje']}</div>
        <div class="metric-sub">unidades base</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""<div class="metric-box">
        <div class="metric-lbl">Retornos disponibles</div>
        <div class="metric-val ok">{r['total_retornos_disponibles_ahora']}</div>
        <div class="metric-sub">de {r['total_retornos_hoy']} retornos hoy</div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""<div class="metric-box warn">
        <div class="metric-lbl">Reservas pendientes</div>
        <div class="metric-val warn">{r['total_reservas_pendientes']}</div>
        <div class="metric-sub">salidas por realizar</div>
    </div>""", unsafe_allow_html=True)
with c4:
    total_al  = alert_count + warn_count
    val_cls   = "crit" if alert_count > 0 else ("warn" if warn_count > 0 else "ok")
    card_cls  = "crit" if alert_count > 0 else ("warn" if warn_count > 0 else "")
    sub_txt   = f"{alert_count} sin stock · {warn_count} stock bajo" if total_al > 0 else "todos los modelos OK"
    st.markdown(f"""<div class="metric-box {card_cls}">
        <div class="metric-lbl">Modelos en alerta</div>
        <div class="metric-val {val_cls}">{total_al}</div>
        <div class="metric-sub">{sub_txt}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── ALERTS ────────────────────────────────
sin_stock  = [m for m in modelos if m["stock_ahora"] <= 0]
stock_bajo = [m for m in modelos if 0 < m["stock_ahora"] <= threshold]

if sin_stock:
    items = "".join([f'<div class="alert-item">{m["modelo"]} — ahora: <b>{m["stock_ahora"]}</b> · fin día: <b>{m["stock_fin_dia"]}</b></div>' for m in sin_stock])
    st.markdown(f'<div class="alert-crit"><div class="alert-title">🚨 Sin stock disponible ahora mismo</div>{items}</div>', unsafe_allow_html=True)

if stock_bajo:
    items = "".join([f'<div class="alert-item">{m["modelo"]} — ahora: <b>{m["stock_ahora"]}</b> · fin día: <b>{m["stock_fin_dia"]}</b></div>' for m in stock_bajo])
    st.markdown(f'<div class="alert-warn"><div class="alert-title">⚠️ Stock bajo — {len(stock_bajo)} modelo(s) por debajo del umbral (≤ {threshold})</div>{items}</div>', unsafe_allow_html=True)

# ── TABS ──────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📊 Stock por modelo", "🔁 Retornos del día", "🚗 Salidas del día"])

with tab1:
    st.markdown('<div class="sec-lbl">Inventario en tiempo real</div>', unsafe_allow_html=True)
    rows = []
    for m in modelos:
        stock = m["stock_ahora"]
        eod   = m["stock_fin_dia"]
        estado = "🔴 SIN STOCK" if stock <= 0 else ("🟡 BAJO" if stock <= threshold else "🟢 OK")
        rows.append({
            "Grupo":         m["grupo"],
            "Modelo":        m["modelo"],
            "Matrículas":    " · ".join(m["matriculas_garaje"]) if m["matriculas_garaje"] else "—",
            "Garaje":        m["garaje"],
            "Ret. disp.":    m["retornos_disponibles_ahora"],
            "Ret. total":    m["retornos_total_hoy"],
            "Salidas":       m["salidas_hechas"],
            "Res. pend.":    m["reservas_pendientes"],
            "Stock ahora":   stock,
            "Fin de día":    eod,
            "Estado":        estado,
        })
    df = pd.DataFrame(rows)

    def color_num(val):
        if isinstance(val, int):
            if val <= 0:            return "color:#B91C1C;font-weight:800"
            if val <= threshold:    return "color:#B45309;font-weight:700"
            return "color:#0F6E56;font-weight:600"
        return ""

    styled = df.style.applymap(color_num, subset=["Stock ahora", "Fin de día"])
    st.dataframe(styled, use_container_width=True, hide_index=True, height=420)

with tab2:
    st.markdown('<div class="sec-lbl">Retornos programados — hora de disponibilidad según zona</div>', unsafe_allow_html=True)
    rows_r = []
    for r2 in sorted(result["retornos"], key=lambda x: x["hora_disponible"]):
        estado = "✅ Disponible" if r2["disponible_ahora"] else "⏳ Pendiente"
        rows_r.append({
            "Hora retorno":   r2["hora"],
            "Disponible a":   r2["hora_disponible"],
            "Modelo":         r2["modelo"],
            "Matrícula":      r2["matricula"],
            "Zona":           r2["zona"],
            "Estado":         estado,
        })
    st.dataframe(pd.DataFrame(rows_r), use_container_width=True, hide_index=True, height=420)

with tab3:
    st.markdown('<div class="sec-lbl">Reservas del día — salidas programadas</div>', unsafe_allow_html=True)
    rows_s = []
    for s in sorted(result["salidas"], key=lambda x: x["hora"]):
        estado = "✅ Realizada" if s["realizada"] else "⏳ Pendiente"
        rows_s.append({
            "Hora":      s["hora"],
            "Modelo":    s["modelo"],
            "Matrícula": s.get("matricula", "—") or "—",
            "Cliente":   s.get("cliente", "—"),
            "Estado":    estado,
        })
    st.dataframe(pd.DataFrame(rows_s), use_container_width=True, hide_index=True, height=460)

st.divider()

# ── EXPORT ────────────────────────────────
st.markdown("**📥 Exportar resultados**")
e1, e2 = st.columns(2)
with e1:
    csv_data = export_csv(result, threshold)
    st.download_button(
        "⬇ Descargar CSV",
        data="\ufeff" + csv_data,
        file_name=f"roig_fleet_demo_{now.strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv",
        use_container_width=True,
    )
with e2:
    txt_data = export_txt(result, sim_now, threshold)
    st.download_button(
        "📄 Descargar TXT resumen",
        data=txt_data,
        file_name=f"roig_fleet_resumen_demo_{now.strftime('%Y%m%d_%H%M')}.txt",
        mime="text/plain",
        use_container_width=True,
    )

st.markdown("""
<div style="text-align:center;padding:20px 0 8px;font-size:.72rem;color:#9CA3AF">
  Roig Fleet Manager · Modo Demo · En producción los datos se cargan desde PDFs con IA
</div>
""", unsafe_allow_html=True)
