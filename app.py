"""
Roig Fleet Manager — app.py
Streamlit + Gemini AI · Roig Rent a Car
"""

import streamlit as st
import google.generativeai as genai
import pdfplumber
import json
import re
import csv
import io
from datetime import datetime, timedelta

# ─────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────
st.set_page_config(
    page_title="Roig Fleet Manager",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────
st.markdown("""
<style>
/* Brand palette */
:root {
    --green:  #0F6E56;
    --green2: #18966F;
    --green-bg: #EAF5F2;
}

/* Hide default Streamlit menu */
#MainMenu, footer { visibility: hidden; }

/* Topbar replacement */
.rfm-header {
    background: #0A4A39;
    color: white;
    padding: 14px 24px;
    border-radius: 10px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.rfm-header h1 { font-size: 1.2rem; margin: 0; font-weight: 700; }
.rfm-header span { font-size: .8rem; opacity: .7; }

/* Metric cards */
.metric-box {
    background: white;
    border: 1px solid #E5E7EB;
    border-radius: 10px;
    padding: 16px;
    text-align: center;
    border-top: 4px solid #0F6E56;
    box-shadow: 0 1px 3px rgba(0,0,0,.06);
}
.metric-box.warn { border-top-color: #B45309; }
.metric-box.crit { border-top-color: #B91C1C; }
.metric-val { font-size: 2.2rem; font-weight: 800; color: #111827; }
.metric-val.ok   { color: #0F6E56; }
.metric-val.warn { color: #B45309; }
.metric-val.crit { color: #B91C1C; }
.metric-lbl { font-size: .72rem; font-weight: 700; text-transform: uppercase;
              letter-spacing: .06em; color: #6B7280; margin-bottom: 6px; }
.metric-sub { font-size: .72rem; color: #9CA3AF; margin-top: 4px; }

/* Alert banners */
.alert-crit {
    background: #FFF5F5; border-left: 4px solid #B91C1C;
    border-radius: 6px; padding: 10px 14px; margin-bottom: 8px;
    font-size: .83rem; color: #111827;
}
.alert-warn {
    background: #FFFBEB; border-left: 4px solid #B45309;
    border-radius: 6px; padding: 10px 14px; margin-bottom: 8px;
    font-size: .83rem; color: #111827;
}
.alert-title { font-weight: 700; margin-bottom: 4px; }
.alert-crit .alert-title { color: #B91C1C; }
.alert-warn .alert-title { color: #B45309; }

/* Upload card visual */
.up-card {
    background: white; border: 2px dashed #D1D5DB;
    border-radius: 10px; padding: 18px 14px;
    text-align: center; margin-bottom: 8px;
}
.up-card.ok { border-color: #0F6E56; background: #EAF5F2; border-style: solid; }

/* Section label */
.sec-lbl {
    font-size: .7rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: .08em; color: #6B7280; margin-bottom: 8px;
}

/* Badge */
.badge { display:inline-block; padding: 2px 8px; border-radius:20px;
         font-size:.68rem; font-weight:700; text-transform:uppercase; }
.badge-ok   { background:#EAF5F2; color:#0A4A39; border:1px solid #A7D9CC; }
.badge-warn { background:#FEF3C7; color:#B45309; border:1px solid #FCD34D; }
.badge-crit { background:#FEE2E2; color:#B91C1C; border:1px solid #FCA5A5; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────
for key, default in {
    "result": None,
    "history": [],
    "calc_time": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ─────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────
now = datetime.now()
st.markdown(f"""
<div class="rfm-header">
  <div>
    <h1>🚗 Roig Fleet Manager</h1>
    <span>Roig Rent a Car · Gestión de flota</span>
  </div>
  <div style="text-align:right">
    <div style="font-size:1.1rem;font-weight:700;font-family:monospace">{now.strftime('%H:%M:%S')}</div>
    <div style="font-size:.75rem;opacity:.7">{now.strftime('%A %d %B %Y')}</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# SIDEBAR — Config + History
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configuración")

    # API Key
    api_key = st.text_input(
        "API Key de Gemini",
        type="password",
        placeholder="AIza…",
        help="Obtenla gratis en aistudio.google.com",
        value=st.session_state.get("gemini_key", "")
    )
    if api_key:
        st.session_state["gemini_key"] = api_key

    # Threshold
    threshold = st.number_input(
        "Umbral alerta stock bajo",
        min_value=0, max_value=20, value=2,
        help="Alerta cuando el stock de un modelo cae a este número o menos"
    )

    st.divider()

    # History
    st.markdown("### 🕐 Historial")
    if st.session_state["history"]:
        for i, h in enumerate(reversed(st.session_state["history"])):
            idx = len(st.session_state["history"]) - 1 - i
            label = h["label"]
            alerts = h.get("alertas", 0)
            badge = "🔴" if alerts > 0 else "🟢"
            if st.button(f"{badge} {label}", key=f"hist_{i}", use_container_width=True):
                st.session_state["result"]    = h["data"]
                st.session_state["calc_time"] = h["ts"]
        if st.button("🗑 Limpiar historial", use_container_width=True):
            st.session_state["history"] = []
            st.rerun()
    else:
        st.caption("Sin cálculos guardados aún.")

# ─────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────
def extract_pdf_text(uploaded_file) -> str:
    """Extract all text from an uploaded PDF using pdfplumber."""
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


def build_prompt(garaje: str, recogidas: str, reservas: str, now: datetime) -> str:
    time_str = now.strftime("%H:%M")
    date_str = now.strftime("%A %d de %B de %Y")
    return f"""Eres el sistema de análisis de flota de "Roig Rent a Car".
Analiza los 3 documentos adjuntos y devuelve ÚNICAMENTE un objeto JSON válido, sin texto adicional ni bloques markdown.

HORA Y FECHA ACTUAL: {date_str}, {time_str}

=== PDF 1 — GARAJE (inventario base) ===
{garaje}

=== PDF 2 — RECOGIDAS DEL DÍA (retornos previstos) ===
{recogidas}

=== PDF 3 — RESERVAS DEL DÍA (salidas previstas) ===
{reservas}

REGLAS DE NEGOCIO (aplica todas con precisión):
1. Retornos zona SHUTT: disponible 45 minutos DESPUÉS de la hora de retorno.
2. Retornos zona AEROP: disponible 60 minutos DESPUÉS de la hora de retorno.
3. Retornos cualquier otra zona: disponible inmediatamente a la hora de retorno.
4. Un retorno está "disponible_ahora" si hora_disponible <= {time_str}.
5. Una salida está "realizada" si hora_salida <= {time_str}.
6. stock_ahora = garaje + retornos_disponibles_ahora - salidas_hechas
7. stock_fin_dia = garaje + total_retornos_hoy - total_reservas_hoy
8. Para cubrir reservas futuras: asignar primero retornos pendientes, luego garaje.

DEVUELVE SOLO ESTE JSON:
{{
  "resumen": {{
    "total_garaje": <int>,
    "total_retornos_disponibles_ahora": <int>,
    "total_retornos_hoy": <int>,
    "total_salidas_hechas": <int>,
    "total_reservas_pendientes": <int>,
    "stock_disponible_ahora": <int>,
    "stock_fin_dia": <int>
  }},
  "modelos": [
    {{
      "grupo": "<Económico|Compacto|SUV|Premium|Familiar|Lujo|Minivan>",
      "modelo": "<Marca Modelo>",
      "matriculas_garaje": ["<MAT>"],
      "garaje": <int>,
      "retornos_disponibles_ahora": <int>,
      "retornos_total_hoy": <int>,
      "salidas_hechas": <int>,
      "reservas_pendientes": <int>,
      "stock_ahora": <int>,
      "stock_fin_dia": <int>
    }}
  ],
  "retornos": [
    {{
      "hora_retorno": "<HH:MM>",
      "hora_disponible": "<HH:MM calculada según zona>",
      "modelo": "<Marca Modelo>",
      "matricula": "<MAT>",
      "zona": "<zona>",
      "disponible_ahora": <bool>
    }}
  ],
  "salidas": [
    {{
      "hora": "<HH:MM>",
      "modelo": "<Marca Modelo>",
      "matricula": "<MAT o vacío>",
      "cliente": "<nombre o vacío>",
      "realizada": <bool>
    }}
  ]
}}"""


def call_gemini(prompt: str, api_key: str) -> dict:
    """Call Gemini API and return parsed JSON result."""
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(
            temperature=0.1,
            max_output_tokens=4096,
        )
    )
    raw = response.text.strip()
    # Strip markdown fences if present
    raw = re.sub(r'^```(?:json)?\s*', '', raw, flags=re.IGNORECASE)
    raw = re.sub(r'\s*```\s*$', '', raw)
    return json.loads(raw)


def save_to_history(result: dict, now: datetime, threshold: int):
    modelos = result.get("modelos", [])
    alertas = len([m for m in modelos if m.get("stock_ahora", 0) <= 0])
    bajos   = len([m for m in modelos if 0 < m.get("stock_ahora", 0) <= threshold])
    entry = {
        "ts":      now.isoformat(),
        "label":   now.strftime("%d/%m %H:%M"),
        "alertas": alertas,
        "bajos":   bajos,
        "data":    result,
    }
    st.session_state["history"].insert(0, entry)
    if len(st.session_state["history"]) > 7:
        st.session_state["history"] = st.session_state["history"][:7]


def export_csv(result: dict, threshold: int) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Grupo", "Modelo", "Matrículas garaje",
        "Garaje", "Ret. disp. ahora", "Ret. total hoy",
        "Salidas hechas", "Reservas pendientes",
        "Stock ahora", "Stock fin día", "Estado"
    ])
    for m in result.get("modelos", []):
        stock = m.get("stock_ahora", 0)
        estado = "SIN STOCK" if stock <= 0 else ("BAJO" if stock <= threshold else "OK")
        writer.writerow([
            m.get("grupo", ""),
            m.get("modelo", ""),
            " · ".join(m.get("matriculas_garaje", [])),
            m.get("garaje", 0),
            m.get("retornos_disponibles_ahora", 0),
            m.get("retornos_total_hoy", 0),
            m.get("salidas_hechas", 0),
            m.get("reservas_pendientes", 0),
            m.get("stock_ahora", 0),
            m.get("stock_fin_dia", 0),
            estado,
        ])
    return output.getvalue()


def export_txt(result: dict, calc_time: datetime, threshold: int) -> str:
    r   = result.get("resumen", {})
    t   = "ROIG FLEET MANAGER — RESUMEN DE STOCK\n"
    t  += "=" * 50 + "\n"
    t  += f"Empresa : Roig Rent a Car\n"
    t  += f"Fecha   : {calc_time.strftime('%A %d de %B de %Y')}\n"
    t  += f"Hora    : {calc_time.strftime('%H:%M:%S')}\n\n"
    t  += "RESUMEN GLOBAL\n" + "-" * 30 + "\n"
    t  += f"Garaje (inventario base)      : {r.get('total_garaje', '—')}\n"
    t  += f"Retornos disponibles ahora    : {r.get('total_retornos_disponibles_ahora', '—')}\n"
    t  += f"Retornos totales hoy          : {r.get('total_retornos_hoy', '—')}\n"
    t  += f"Salidas ya realizadas         : {r.get('total_salidas_hechas', '—')}\n"
    t  += f"Reservas pendientes           : {r.get('total_reservas_pendientes', '—')}\n"
    t  += f"STOCK DISPONIBLE AHORA        : {r.get('stock_disponible_ahora', '—')}\n"
    t  += f"STOCK ESTIMADO FIN DE DÍA     : {r.get('stock_fin_dia', '—')}\n\n"
    t  += "DETALLE POR MODELO\n" + "-" * 50 + "\n"
    for m in result.get("modelos", []):
        stock  = m.get("stock_ahora", 0)
        estado = "[SIN STOCK]" if stock <= 0 else ("[BAJO]" if stock <= threshold else "[OK]")
        t += f"\n{m.get('modelo','')} ({m.get('grupo','')}) {estado}\n"
        plates = m.get("matriculas_garaje", [])
        if plates:
            t += f"  Matrículas: {', '.join(plates)}\n"
        t += f"  Garaje: {m.get('garaje',0)} | Ret. disp: {m.get('retornos_disponibles_ahora',0)}/{m.get('retornos_total_hoy',0)}"
        t += f" | Salidas: {m.get('salidas_hechas',0)} | Pendientes: {m.get('reservas_pendientes',0)}\n"
        t += f"  Stock ahora: {m.get('stock_ahora',0)} | Fin de día: {m.get('stock_fin_dia',0)}\n"
    t += "\n" + "-" * 50 + "\nGenerado por Roig Fleet Manager\n"
    return t


# ─────────────────────────────────────────
# UPLOAD SECTION
# ─────────────────────────────────────────
st.markdown('<div class="sec-lbl">📁 Documentos del día — sube los 3 PDFs</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**🏗️ Coches en garaje**")
    st.caption("Inventario base · matrícula y modelo")
    pdf_garaje = st.file_uploader("PDF Garaje", type="pdf", key="pdf0", label_visibility="collapsed")
    if pdf_garaje:
        st.success(f"✓ {pdf_garaje.name}")

with col2:
    st.markdown("**🔁 Recogidas del día**")
    st.caption("Retornos previstos · hora y zona")
    pdf_recogidas = st.file_uploader("PDF Recogidas", type="pdf", key="pdf1", label_visibility="collapsed")
    if pdf_recogidas:
        st.success(f"✓ {pdf_recogidas.name}")

with col3:
    st.markdown("**📋 Reservas del día**")
    st.caption("Salidas previstas · hora y modelo")
    pdf_reservas = st.file_uploader("PDF Reservas", type="pdf", key="pdf2", label_visibility="collapsed")
    if pdf_reservas:
        st.success(f"✓ {pdf_reservas.name}")

st.divider()

# ─────────────────────────────────────────
# CALCULATE BUTTON
# ─────────────────────────────────────────
all_pdfs   = all([pdf_garaje, pdf_recogidas, pdf_reservas])
has_key    = bool(st.session_state.get("gemini_key", "").strip())
can_calc   = all_pdfs and has_key

if not has_key:
    st.warning("⚙️ Introduce tu API key de Gemini en el panel lateral para continuar.")
elif not all_pdfs:
    st.info("📂 Sube los 3 PDFs para activar el cálculo.")

calc_btn = st.button(
    "⚡ Calcular stock ahora",
    disabled=not can_calc,
    type="primary",
    use_container_width=True,
)

if calc_btn and can_calc:
    now_calc = datetime.now()
    with st.spinner("Extrayendo texto de los PDFs…"):
        try:
            text_garaje   = extract_pdf_text(pdf_garaje)
            text_recogidas = extract_pdf_text(pdf_recogidas)
            text_reservas  = extract_pdf_text(pdf_reservas)
        except Exception as e:
            st.error(f"Error al leer los PDFs: {e}")
            st.stop()

    with st.spinner("Gemini analizando inventario, retornos y reservas…"):
        try:
            prompt = build_prompt(text_garaje, text_recogidas, text_reservas, now_calc)
            result = call_gemini(prompt, st.session_state["gemini_key"])
        except json.JSONDecodeError as e:
            st.error(f"Gemini devolvió una respuesta no válida. Intenta de nuevo. ({e})")
            st.stop()
        except Exception as e:
            st.error(f"Error al llamar a Gemini: {e}")
            st.stop()

    st.session_state["result"]    = result
    st.session_state["calc_time"] = now_calc
    save_to_history(result, now_calc, threshold)
    st.rerun()

# ─────────────────────────────────────────
# RESULTS
# ─────────────────────────────────────────
result    = st.session_state.get("result")
calc_time = st.session_state.get("calc_time")

if result:
    modelos = result.get("modelos", [])
    resumen = result.get("resumen", {})
    thr     = threshold

    # Timestamp
    if calc_time:
        ts_str = calc_time.strftime("Calculado el %A %d/%m/%Y a las %H:%M:%S")
        st.caption(f"🟢 {ts_str}")

    # ── METRICS ──────────────────────────────────────
    alert_count = len([m for m in modelos if m.get("stock_ahora", 0) <= 0])
    warn_count  = len([m for m in modelos if 0 < m.get("stock_ahora", 0) <= thr])
    total_alerts = alert_count + warn_count

    mc1, mc2, mc3, mc4 = st.columns(4)
    with mc1:
        st.markdown(f"""<div class="metric-box neutral">
            <div class="metric-lbl">En garaje</div>
            <div class="metric-val">{resumen.get('total_garaje','—')}</div>
            <div class="metric-sub">unidades base</div>
        </div>""", unsafe_allow_html=True)
    with mc2:
        st.markdown(f"""<div class="metric-box">
            <div class="metric-lbl">Retornos disponibles</div>
            <div class="metric-val ok">{resumen.get('total_retornos_disponibles_ahora','—')}</div>
            <div class="metric-sub">de {resumen.get('total_retornos_hoy','—')} retornos hoy</div>
        </div>""", unsafe_allow_html=True)
    with mc3:
        st.markdown(f"""<div class="metric-box warn">
            <div class="metric-lbl">Reservas pendientes</div>
            <div class="metric-val warn">{resumen.get('total_reservas_pendientes','—')}</div>
            <div class="metric-sub">salidas por realizar</div>
        </div>""", unsafe_allow_html=True)
    with mc4:
        alert_cls = "crit" if alert_count > 0 else ("warn" if warn_count > 0 else "")
        val_cls   = "crit" if alert_count > 0 else ("warn" if warn_count > 0 else "ok")
        st.markdown(f"""<div class="metric-box {alert_cls}">
            <div class="metric-lbl">Modelos en alerta</div>
            <div class="metric-val {val_cls}">{total_alerts}</div>
            <div class="metric-sub">{alert_count} sin stock · {warn_count} bajo umbral</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── ALERTS ────────────────────────────────────────
    sin_stock = [m for m in modelos if m.get("stock_ahora", 0) <= 0]
    stock_bajo = [m for m in modelos if 0 < m.get("stock_ahora", 0) <= thr]

    if sin_stock:
        items = "".join([f"<div>· {m['modelo']} — ahora: <b>{m['stock_ahora']}</b> · fin día: <b>{m['stock_fin_dia']}</b></div>" for m in sin_stock])
        st.markdown(f"""<div class="alert-crit">
            <div class="alert-title">🚨 Sin stock disponible ahora mismo</div>{items}</div>""",
            unsafe_allow_html=True)

    if stock_bajo:
        items = "".join([f"<div>· {m['modelo']} — ahora: <b>{m['stock_ahora']}</b> · fin día: <b>{m['stock_fin_dia']}</b></div>" for m in stock_bajo])
        st.markdown(f"""<div class="alert-warn">
            <div class="alert-title">⚠️ Stock bajo — {len(stock_bajo)} modelo(s) por debajo del umbral (≤ {thr})</div>{items}</div>""",
            unsafe_allow_html=True)

    # ── TABLE + PANELS ────────────────────────────────
    tab_table, tab_returns, tab_depart = st.tabs(["📊 Stock por modelo", "🔁 Retornos del día", "🚗 Salidas del día"])

    with tab_table:
        if modelos:
            import pandas as pd
            rows = []
            for m in modelos:
                stock = m.get("stock_ahora", 0)
                eod   = m.get("stock_fin_dia", 0)
                if stock <= 0:
                    estado = "🔴 SIN STOCK"
                elif stock <= thr:
                    estado = "🟡 BAJO"
                else:
                    estado = "🟢 OK"
                rows.append({
                    "Grupo":          m.get("grupo", "—"),
                    "Modelo":         m.get("modelo", "—"),
                    "Matrículas":     " · ".join(m.get("matriculas_garaje", [])),
                    "Garaje":         m.get("garaje", 0),
                    "Ret. disp.":     m.get("retornos_disponibles_ahora", 0),
                    "Ret. total":     m.get("retornos_total_hoy", 0),
                    "Salidas":        m.get("salidas_hechas", 0),
                    "Res. pend.":     m.get("reservas_pendientes", 0),
                    "Stock ahora":    stock,
                    "Fin de día":     eod,
                    "Estado":         estado,
                })
            df = pd.DataFrame(rows)

            def color_stock(val):
                if isinstance(val, int):
                    if val <= 0:   return "color: #B91C1C; font-weight: 800"
                    if val <= thr: return "color: #B45309; font-weight: 700"
                    return "color: #0F6E56; font-weight: 700"
                return ""

            styled = df.style.applymap(color_stock, subset=["Stock ahora", "Fin de día"])
            st.dataframe(styled, use_container_width=True, hide_index=True)
        else:
            st.info("Sin datos de modelos en los PDFs analizados.")

    with tab_returns:
        retornos = sorted(result.get("retornos", []), key=lambda x: x.get("hora_disponible", ""))
        if retornos:
            import pandas as pd
            rows_r = []
            for r in retornos:
                disp = "✅ Disponible" if r.get("disponible_ahora") else "⏳ Pendiente"
                rows_r.append({
                    "Hora retorno":    r.get("hora_retorno", "—"),
                    "Disponible a":    r.get("hora_disponible", "—"),
                    "Modelo":          r.get("modelo", "—"),
                    "Matrícula":       r.get("matricula", "—"),
                    "Zona":            r.get("zona", "—"),
                    "Estado":          disp,
                })
            st.dataframe(pd.DataFrame(rows_r), use_container_width=True, hide_index=True)
        else:
            st.info("Sin retornos registrados hoy.")

    with tab_depart:
        salidas = sorted(result.get("salidas", []), key=lambda x: x.get("hora", ""))
        if salidas:
            import pandas as pd
            rows_s = []
            for s in salidas:
                estado = "✅ Realizada" if s.get("realizada") else "⏳ Pendiente"
                rows_s.append({
                    "Hora":      s.get("hora", "—"),
                    "Modelo":    s.get("modelo", "—"),
                    "Matrícula": s.get("matricula", "—"),
                    "Cliente":   s.get("cliente", "—"),
                    "Estado":    estado,
                })
            st.dataframe(pd.DataFrame(rows_s), use_container_width=True, hide_index=True)
        else:
            st.info("Sin salidas registradas hoy.")

    st.divider()

    # ── EXPORT ────────────────────────────────────────
    st.markdown("**📥 Exportar resultados**")
    exp1, exp2 = st.columns(2)
    with exp1:
        csv_data = export_csv(result, thr)
        st.download_button(
            "⬇ Descargar CSV",
            data="\ufeff" + csv_data,   # BOM for Excel
            file_name=f"roig_fleet_{now.strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with exp2:
        txt_data = export_txt(result, calc_time or now, thr)
        st.download_button(
            "📄 Descargar TXT resumen",
            data=txt_data,
            file_name=f"roig_fleet_resumen_{now.strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
            use_container_width=True,
        )

else:
    # Empty state
    st.markdown("""
    <div style="text-align:center; padding: 60px 20px; background:white;
                border:1px solid #E5E7EB; border-radius:12px; color:#6B7280">
        <div style="font-size:2.5rem; margin-bottom:12px; opacity:.4">📊</div>
        <h3 style="color:#111827; margin-bottom:8px">Sin resultados todavía</h3>
        <p style="font-size:.85rem; line-height:1.6">
            Sube los tres PDFs del día e introduce tu API key de Gemini<br>
            en el panel lateral, luego pulsa <strong>Calcular stock ahora</strong>.
        </p>
    </div>
    """, unsafe_allow_html=True)
