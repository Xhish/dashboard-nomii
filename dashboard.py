import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime
import hmac

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NOMII · Finance Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ─── AUTHENTICATION ─────────────────────────────────────────────────────────
def check_password():
    """Returns True if the user has entered a correct password."""

    def login_form():
        """Display the login form."""
        st.markdown(
            """
            <div style="display:flex; justify-content:center; align-items:center; min-height:60vh;">
                <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:16px;
                     padding:2.5rem; max-width:400px; width:100%; box-shadow:0 4px 24px rgba(0,0,0,0.08);">
                    <h2 style="text-align:center; color:#0f172a; margin-bottom:0.3rem;">🔐 NOMII Dashboard</h2>
                    <p style="text-align:center; color:#64748b; font-size:0.9rem; margin-bottom:1.5rem;">
                        Ingresa tus credenciales para acceder</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        with st.form("credentials"):
            st.text_input("Usuario", key="username")
            st.text_input("Contraseña", type="password", key="password")
            st.form_submit_button("Iniciar sesión", on_click=password_entered)

    def password_entered():
        """Check whether a password entered by the user is correct."""
        users = st.secrets.get("passwords", {})
        if st.session_state["username"] in users and hmac.compare_digest(
            st.session_state["password"],
            users[st.session_state["username"]],
        ):
            st.session_state["password_correct"] = True
            st.session_state["current_user"] = st.session_state["username"]
            del st.session_state["password"]  # Don't store password
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    # Return True if already authenticated
    if st.session_state.get("password_correct", False):
        return True

    # Show login form
    login_form()
    if "password_correct" in st.session_state and not st.session_state["password_correct"]:
        st.error("😕 Usuario o contraseña incorrectos")
    return False


if not check_password():
    st.stop()

# ─── DARK MODE STATE ────────────────────────────────────────────────────────
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

dark = st.session_state.dark_mode

# ─── THEME COLORS ───────────────────────────────────────────────────────────
if dark:
    T = {
        "bg": "#0E1117", "bg2": "#161B22", "card_bg": "#1C2128",
        "card_border": "#30363D", "text": "#E6EDF3", "text2": "#8B949E",
        "heading": "#58A6FF", "sidebar_bg": "#161B22", "sidebar_border": "#30363D",
        "card_highlight_bg": "linear-gradient(135deg, #0d1f3c 0%, #0e2a40 100%)",
        "card_highlight_border": "#58A6FF", "kpi_value": "#E6EDF3",
        "label_color": "#8B949E", "grid_color": "#21262D",
        "section_border": "#20C6B6", "tag_bg": "#1C3D5A",
        "toggle_bg": "rgba(30,35,45,0.95)", "toggle_border": "#58A6FF",
    }
else:
    T = {
        "bg": "#FFFFFF", "bg2": "#F9F9F9", "card_bg": "#FFFFFF",
        "card_border": "#B3D9EA", "text": "#333333", "text2": "#4D7EA8",
        "heading": "#003366", "sidebar_bg": "#F9F9F9", "sidebar_border": "#B3D9EA",
        "card_highlight_bg": "linear-gradient(135deg, #f0f7ff 0%, #e8f4f8 100%)",
        "card_highlight_border": "#003366", "kpi_value": "#003366",
        "label_color": "#4D7EA8", "grid_color": "#f1f5f9",
        "section_border": "#20C6B6", "tag_bg": "#003366",
        "toggle_bg": "rgba(255,255,255,0.95)", "toggle_border": "#003366",
    }

# ─── CUSTOM CSS ─────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {{ font-family: 'DM Sans', sans-serif; }}
.block-container {{ padding-top: 1.5rem; padding-bottom: 1rem; }}

/* Theme background */
.stApp {{ background-color: {T['bg']} !important; color: {T['text']} !important; }}

/* Header */
.main-header {{
    background: linear-gradient(135deg, #002244 0%, #003366 50%, #002244 100%);
    padding: 1.8rem 2.2rem; border-radius: 16px; margin-bottom: 1.5rem;
    border: 1px solid rgba(32,198,182,0.2); box-shadow: 0 4px 24px rgba(0,51,102,0.15);
}}
.stApp .main-header h1 {{ color: #f8fafc !important; font-size: 1.7rem; font-weight: 700; margin: 0; letter-spacing: -0.5px; }}
.stApp .main-header p {{ color: #B3D9EA !important; font-size: 0.88rem; margin: 0.3rem 0 0 0; }}
.stApp .main-header .accent-dot {{ color: #20C6B6 !important; }}

/* KPI Cards */
.kpi-card {{
    background: {T['card_bg']}; border: 1px solid {T['card_border']};
    border-radius: 14px; padding: 1.3rem 1.5rem; text-align: left;
    box-shadow: 0 1px 4px rgba(0,0,0,{'0.15' if dark else '0.04'});
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}}
.kpi-card:hover {{ transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0,0,0,{'0.3' if dark else '0.07'}); }}
.kpi-label {{ font-size: 0.72rem; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.8px; color: {T['label_color']}; margin-bottom: 0.35rem; }}
.kpi-value {{ font-family: 'JetBrains Mono', monospace; font-size: 1.55rem;
    font-weight: 700; color: {T['kpi_value']}; line-height: 1.2; }}
.kpi-delta {{ font-size: 0.78rem; font-weight: 600; margin-top: 0.25rem; }}
.kpi-delta.positive {{ color: #20C6B6; }}
.kpi-delta.negative {{ color: #ef4444; }}

/* Section titles */
.section-title {{ font-size: 1.05rem; font-weight: 700; color: {T['heading']};
    margin: 1.8rem 0 0.8rem 0; padding-bottom: 0.5rem;
    border-bottom: 2px solid {T['section_border']}; letter-spacing: -0.3px; }}

/* Sidebar */
section[data-testid="stSidebar"] {{ background: {T['sidebar_bg']}; border-right: 1px solid {T['sidebar_border']}; }}
section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] .stMarkdown h3 {{ color: {T['heading']}; }}
section[data-testid="stSidebar"] .stMarkdown h3 {{ font-size: 0.8rem; text-transform: uppercase;
    letter-spacing: 1px; font-weight: 600; margin-top: 1rem; }}
section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span {{ color: {T['text']} !important; }}

/* Branding */
#MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}} header {{visibility: hidden;}}

/* Plotly */
.stPlotlyChart {{ border-radius: 12px; overflow: hidden; }}

/* Tags */
span[data-baseweb="tag"] {{ background-color: {T['tag_bg']} !important; color: white !important; border-radius: 6px !important; }}
span[data-baseweb="tag"] span[role="presentation"] {{ color: white !important; }}

/* Buttons */
.stButton > button {{ background-color: {'#1C3D5A' if dark else '#003366'}; color: white; border: none; border-radius: 8px; }}
.stButton > button:hover {{ background-color: #20C6B6; color: white; }}

/* Slider */
.stSlider > div > div > div[role="slider"] {{ background-color: #20C6B6 !important; }}

/* Sidebar toggle */
button[data-testid="stSidebarCollapse"],
[data-testid="collapsedControl"],
[data-testid="collapsedControl"] > button {{
    visibility: visible !important; display: block !important; position: fixed !important;
    top: 10px !important; left: 10px !important; z-index: 999999 !important;
    color: {T['heading']} !important; background: {T['toggle_bg']} !important;
    border: 2px solid {T['toggle_border']} !important; border-radius: 8px !important;
    box-shadow: 0 2px 10px rgba(0,0,0,0.2) !important;
}}

/* Text & headings */
.stApp p, .stApp span, .stApp label {{ color: {T['text']}; }}
.stApp h2, .stApp h3, .stApp h4 {{ color: {T['heading']}; }}

/* Tabs */
.stTabs [data-baseweb="tab"] {{ color: {T['text2']}; }}
.stTabs [aria-selected="true"] {{ color: {T['heading']} !important; }}

/* Inputs globales */
.stSelectbox div[data-baseweb="select"] > div,
.stMultiSelect div[data-baseweb="select"] > div {{
    background-color: {T['card_bg']} !important; color: {T['text']} !important;
    border-color: {T['card_border']} !important;
}}

/* ── FILTROS: campo de selección → azul oscuro NOMII ── */
.stExpander .stSelectbox div[data-baseweb="select"] > div,
.stExpander .stMultiSelect div[data-baseweb="select"] > div {{
    background-color: #002244 !important;
    color: #f8fafc !important;
    border-color: rgba(32,198,182,0.35) !important;
}}
/* Etiquetas y títulos de filtros: blanco */
.stExpander label, .stExpander .stMarkdown p, .stExpander .stMarkdown span,
.stExpander .stSelectbox label, .stExpander .stMultiSelect label,
.stExpander .stDateInput label {{
    color: #f8fafc !important;
}}
/* Texto toggle del expander */
.stExpander summary span, .stExpander [data-testid="stExpanderToggleIcon"] {{
    color: #f8fafc !important;
}}
/* Fondo del expander (filtros y cuotas): azul oscuro siempre */
.stExpander, .stExpander > details, .stExpander > details[open] {{
    background: {'rgba(22,27,34,0.85)' if dark else '#002244'} !important;
    border-radius: 12px; padding: 0.5rem;
    border: 1px solid {'#30363D' if dark else 'rgba(32,198,182,0.25)'} !important;
}}
/* Header del expander: mismo azul oscuro, letras blancas, sin cambio al abrir */
.streamlit-expanderHeader,
.stExpander [data-testid="stExpanderHeader"],
.stExpander summary {{
    color: #f8fafc !important;
    background-color: {'rgba(22,27,34,0.85)' if dark else '#002244'} !important;
    border-radius: 8px !important;
}}
/* Contenido interno del expander: mismo fondo */
.streamlit-expanderContent,
.stExpander [data-testid="stExpanderDetails"] {{
    background-color: {'rgba(22,27,34,0.85)' if dark else '#002244'} !important;
    border-radius: 0 0 8px 8px !important;
}}

/* Lista desplegable de opciones: azul oscuro NOMII */
[data-baseweb="popover"] ul,
ul[data-baseweb="menu"],
[data-baseweb="menu"] {{
    background-color: #002244 !important;
}}
[data-baseweb="option"] {{
    background-color: #002244 !important;
    color: #f8fafc !important;
}}
[data-baseweb="option"]:hover, [data-baseweb="option"][aria-selected="true"] {{
    background-color: #003d7a !important;
    color: #20C6B6 !important;
}}

/* Modo oscuro: ocultar recuadro blanco de búsqueda en multiselect */
{'div[data-baseweb="select"] input[type="text"], div[data-baseweb="input"] input[type="text"], input[aria-autocomplete="list"] { background-color: transparent !important; color: #E6EDF3 !important; width: 2px !important; min-width: 2px !important; caret-color: #E6EDF3; }' if dark else 'div[data-baseweb="select"] input[type="text"], input[aria-autocomplete="list"] { background-color: transparent !important; color: #f8fafc !important; caret-color: #f8fafc; }'}

.stDataFrame {{ border-radius: 12px; overflow: hidden; }}
</style>
""", unsafe_allow_html=True)

# ─── NOMII INSTITUTIONAL COLORS ────────────────────────────────────────────
NOMII = {
    "primary": "#003366",
    "secondary": "#20C6B6",
    "accent": "#FFCC00",
    "text": T["text"],
    "background": T["bg2"],
    "light_blue": "#4D7EA8",
    "pale_blue": "#B3D9EA",
    "heading": T["heading"],
    "card_bg": T["card_bg"],
    "card_border": T["card_border"],
    "grid_color": T["grid_color"],
}

PALETTE = [
    "#003366", "#20C6B6", "#4D7EA8", "#FFCC00", "#B3D9EA",
    "#005599", "#17a89c", "#6A9BC3", "#FFD633", "#CCE5F0",
    "#001a33", "#0f8a7e", "#3a6d8c", "#CC9900", "#8AB8D0",
]
if dark:
    PALETTE = [
        "#4D99CC", "#20C6B6", "#6AB0D2", "#FFCC00", "#8FCAE8",
        "#3388BB", "#2ED8C8", "#89C4DE", "#FFD633", "#A8D8F0",
        "#2677AA", "#17A89C", "#5BA0C4", "#E6B800", "#6EBBDA",
    ]

CHART_LAYOUT = dict(
    font=dict(family="DM Sans", color=T["text"]),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=40, r=20, t=40, b=40),
    title_font_color=T["text"],
    legend_font_color=T["text"],
    hoverlabel=dict(
        bgcolor="#1C2128" if dark else "#003366",
        font_size=12, font_family="DM Sans",
        font_color="#E6EDF3" if dark else "#f8fafc",
        bordercolor="rgba(0,0,0,0)",
    ),
)



# ─── LOAD DATA ──────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)  # Refresca los datos cada hora
def load_data():
    import requests
    from io import BytesIO

    sharepoint_url = st.secrets.get("sharepoint", {}).get("url", "")

    if sharepoint_url:
        try:
            # Convertir link de SharePoint a URL de descarga directa
            if "?" in sharepoint_url:
                download_url = sharepoint_url + "&download=1"
            else:
                download_url = sharepoint_url + "?download=1"
            response = requests.get(download_url, timeout=30)
            response.raise_for_status()
            df = pd.read_excel(
                BytesIO(response.content),
                sheet_name="SALIDAS",
                engine="openpyxl",
            )
            st.sidebar.success("📡 Datos cargados desde SharePoint")
        except Exception as e:
            st.sidebar.warning(f"⚠️ Error SharePoint, usando archivo local: {e}")
            df = pd.read_excel(
                "Maestro Pagos NOMII 07-03-2026.xlsx",
                sheet_name="SALIDAS",
                engine="openpyxl",
            )
    else:
        df = pd.read_excel(
            "Maestro Pagos NOMII 07-03-2026.xlsx",
            sheet_name="SALIDAS",
            engine="openpyxl",
        )

    df["Date"] = pd.to_datetime(df["Date"])
    df["Abs_Amount"] = df["Amount in EUR"].abs()
    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.month
    df["Month_Name"] = df["Date"].dt.strftime("%m/%Y")
    df["Year_Month"] = df["Date"].dt.to_period("M").astype(str)
    return df


df_raw = load_data()


@st.cache_data(ttl=3600)
def load_ingresos():
    import requests
    from io import BytesIO

    sharepoint_url = st.secrets.get("sharepoint", {}).get("url", "")

    if sharepoint_url:
        try:
            if "?" in sharepoint_url:
                download_url = sharepoint_url + "&download=1"
            else:
                download_url = sharepoint_url + "?download=1"
            response = requests.get(download_url, timeout=30)
            response.raise_for_status()
            df = pd.read_excel(
                BytesIO(response.content),
                sheet_name="INGRESOS",
                engine="openpyxl",
            )
        except Exception:
            df = pd.read_excel(
                "Maestro Pagos NOMII 07-03-2026.xlsx",
                sheet_name="INGRESOS",
                engine="openpyxl",
            )
    else:
        df = pd.read_excel(
            "Maestro Pagos NOMII 07-03-2026.xlsx",
            sheet_name="INGRESOS",
            engine="openpyxl",
        )

    df["FECHA"] = pd.to_datetime(df["FECHA"], errors="coerce")
    df = df.dropna(subset=["FECHA"])

    # Limpiar montos numéricos
    for col in ["IMPORTE", "CARGO", " INGRESO NETO"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df["Ingreso_Abs"] = df[" INGRESO NETO"].abs() if " INGRESO NETO" in df.columns else df["IMPORTE"].abs()
    df["Year"] = df["FECHA"].dt.year
    df["Month"] = df["FECHA"].dt.month
    df["Year_Month"] = df["FECHA"].dt.to_period("M").astype(str)
    df["Month_Name"] = df["FECHA"].dt.strftime("%m/%Y")
    return df


df_ingresos_raw = load_ingresos()


def _get_excel_source():
    """Helper to get Excel bytes from SharePoint or local."""
    import requests
    from io import BytesIO
    sharepoint_url = st.secrets.get("sharepoint", {}).get("url", "")
    if sharepoint_url:
        try:
            download_url = sharepoint_url + ("&download=1" if "?" in sharepoint_url else "?download=1")
            resp = requests.get(download_url, timeout=30)
            resp.raise_for_status()
            return BytesIO(resp.content)
        except Exception:
            pass
    return "Maestro Pagos NOMII 07-03-2026.xlsx"


@st.cache_data(ttl=3600)
def load_calendario():
    src = _get_excel_source()
    df = pd.read_excel(src, sheet_name="CALENDARIO INGRESOS", engine="openpyxl")
    df["FECHA"] = pd.to_datetime(df["FECHA"], errors="coerce")
    df["MONTO"] = pd.to_numeric(df["MONTO"], errors="coerce").fillna(0)
    return df


@st.cache_data(ttl=3600)
def load_resumen_clientes():
    src = _get_excel_source()
    return pd.read_excel(src, sheet_name="RESUMEN CLIENTES", engine="openpyxl")


@st.cache_data(ttl=3600)
def load_cohortes():
    src = _get_excel_source()
    df = pd.read_excel(src, sheet_name="COHORTES INGRESO", engine="openpyxl")
    df["MES"] = pd.to_datetime(df["MES"], errors="coerce")
    return df


df_calendario = load_calendario()
df_clientes = load_resumen_clientes()
df_cohortes = load_cohortes()

# ─── Defaults de fecha (mes actual + 2 meses anteriores) ────────────────────
from datetime import date
import calendar
min_date = df_raw["Date"].min().date()
max_date = df_raw["Date"].max().date()
today = date.today()
# 3 months: current + 2 previous
_m = today.month - 2
_y = today.year
if _m <= 0:
    _m += 12
    _y -= 1
default_start = max(date(_y, _m, 1), min_date)
last_day = calendar.monthrange(today.year, today.month)[1]
default_end = min(date(today.year, today.month, last_day), max_date)

# ─── HEADER ─────────────────────────────────────────────────────────────────
hdr_col1, hdr_col2 = st.columns([9, 1])
with hdr_col1:
    st.markdown(
        f"""
        <div class="main-header">
            <div style="color: #f8fafc; font-size: 1.7rem; font-weight: 700; margin: 0; letter-spacing: -0.5px; font-family: 'DM Sans', sans-serif;">
                NOMII<span style="color: #20C6B6;"> · </span>Finance Dashboard</div>
            <div style="color: #B3D9EA; font-size: 0.88rem; margin: 0.3rem 0 0 0; font-family: 'DM Sans', sans-serif;">
                {default_start.strftime('%d/%m/%Y')} → {default_end.strftime('%d/%m/%Y')}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with hdr_col2:
    def toggle_dark():
        st.session_state.dark_mode = not st.session_state.dark_mode
    dm_icon = "☀️" if dark else "🌙"
    st.button(dm_icon, on_click=toggle_dark, help="Activar/Desactivar Modo Nocturno")

# ─── FILTROS (en área principal, siempre visibles) ──────────────────────────
with st.expander("🔎 **Filtros** — clic para expandir", expanded=False):
    f_col1, f_col2 = st.columns(2)
    with f_col1:
        date_range = st.date_input(
            "📅 Rango de fechas",
            value=(default_start, default_end),
            min_value=min_date,
            max_value=max_date,
        )
    with f_col2:
        all_cats = sorted(df_raw["Category"].dropna().unique())
        sel_cats = st.multiselect("📂 Categoría", all_cats, default=all_cats)

    f_col3, f_col4, f_col5 = st.columns(3)
    with f_col3:
        all_deps = sorted(df_raw["Department"].dropna().unique())
        sel_deps = st.multiselect("🏢 Departamento", all_deps, default=all_deps)
    with f_col4:
        all_acct = sorted(df_raw["Accounting Type"].dropna().unique())
        sel_acct = st.multiselect("📋 Tipo Contable", all_acct, default=all_acct)
    with f_col5:
        all_bfn = sorted(df_raw["Business Function"].dropna().unique())
        sel_bfn = st.multiselect("⚙️ Función de Negocio", all_bfn, default=all_bfn)

    f_col6, f_col7 = st.columns(2)
    with f_col6:
        all_fac = sorted(df_raw["Facturacion"].dropna().unique())
        sel_fac = st.multiselect("🧾 Facturación", all_fac, default=all_fac)
    with f_col7:
        all_cb = sorted(df_raw["Cost Behavior"].dropna().unique())
        sel_cb = st.multiselect("📊 Comportamiento del Costo", all_cb, default=all_cb)

# ─── APPLY FILTERS ──────────────────────────────────────────────────────────
if isinstance(date_range, tuple) and len(date_range) == 2:
    d_start, d_end = date_range
else:
    d_start, d_end = min_date, max_date

df = df_raw[
    (df_raw["Date"].dt.date >= d_start)
    & (df_raw["Date"].dt.date <= d_end)
    & (df_raw["Category"].isin(sel_cats))
    & (df_raw["Department"].isin(sel_deps))
    & (df_raw["Accounting Type"].isin(sel_acct))
    & (df_raw["Business Function"].isin(sel_bfn))
    & (df_raw["Facturacion"].isin(sel_fac))
    & (df_raw["Cost Behavior"].isin(sel_cb))
].copy()

# ─── PAGE TABS ──────────────────────────────────────────────────────────────
tab_kpis, tab_eerr, tab_ingresos, tab_gastos = st.tabs(["📊 KPIs Ejecutivos", "📑 Estado de Resultados", "💰 Ingresos", "💸 Gastos"])

# ═════════════════════════════════════════════════════════════════════════════
# TAB 4: GASTOS (SALIDAS)
# ═════════════════════════════════════════════════════════════════════════════
with tab_gastos:
    total_spend = df["Abs_Amount"].sum()
    n_transactions = len(df)
    avg_ticket = total_spend / n_transactions if n_transactions else 0
    n_counterparties = df["Counterparty"].nunique()
    median_spend = df["Abs_Amount"].median()
    
    # MoM change
    monthly_totals = df.groupby("Year_Month")["Abs_Amount"].sum().sort_index()
    if len(monthly_totals) >= 2:
        last_m = monthly_totals.iloc[-1]
        prev_m = monthly_totals.iloc[-2]
        mom_change = ((last_m - prev_m) / prev_m * 100) if prev_m else 0
        mom_cls = "positive" if mom_change <= 0 else "negative"
        mom_arrow = "↓" if mom_change <= 0 else "↑"
        mom_str = f'<div class="kpi-delta {mom_cls}">{mom_arrow} {abs(mom_change):.1f}% vs mes anterior</div>'
    else:
        mom_str = ""
    
    # Calculate Gasto % sobre Ingresos
    ingresos_cobrados_total = df_eerr["Ingreso Cobrado"].sum() if "df_eerr" in locals() and not df_eerr.empty else (
        df_ingresos_raw["Ingreso_Abs"].sum() if "df_ingresos_raw" in locals() and not df_ingresos_raw.empty else 0
    )
    gasto_pct_ingresos = (total_spend / ingresos_cobrados_total * 100) if ingresos_cobrados_total > 0 else 0
    pct_cls = "positive" if gasto_pct_ingresos <= 80 else "negative"
    
    cols = st.columns(5)
    kpis = [
        ("Gasto Total", f"€{total_spend:,.0f}", mom_str),
        ("Gasto % s/ Ingresos", f"{gasto_pct_ingresos:.1f}%", f'<div class="kpi-delta {pct_cls}">Objetivo: < 80%</div>'),
        ("Transacciones", f"{n_transactions:,}", ""),
        ("Ticket Promedio", f"€{avg_ticket:,.0f}", ""),
        ("Proveedores", f"{n_counterparties}", ""),
    ]
    for col, (label, value, delta) in zip(cols, kpis):
        col.markdown(
            f'<div class="kpi-card"><div class="kpi-label">{label}</div>'
            f'<div class="kpi-value">{value}</div>{delta}</div>',
            unsafe_allow_html=True,
        )
    
    # ═══════════════════════════════════════════════════════════════════════════
    # ROW 1: Monthly Trend + Category Breakdown
    # ═══════════════════════════════════════════════════════════════════════════
    st.markdown('<div class="section-title">📈 Tendencia Mensual & Composición de Gasto</div>', unsafe_allow_html=True)
    
    c1, c2 = st.columns([3, 2])
    
    # ── Monthly Trend (bar + line)
    with c1:
        monthly = (
            df.groupby("Year_Month")["Abs_Amount"]
            .sum()
            .reset_index()
            .rename(columns={"Year_Month": "Mes", "Abs_Amount": "Gasto"})
            .sort_values("Mes")
        )
        monthly["Mes"] = monthly["Mes"].str[5:7] + "/" + monthly["Mes"].str[:4]
        monthly["Acumulado"] = monthly["Gasto"].cumsum()
    
        fig_trend = make_subplots(specs=[[{"secondary_y": True}]])
        fig_trend.add_trace(
            go.Bar(
                x=monthly["Mes"], y=monthly["Gasto"],
                name="Gasto Mensual",
                marker=dict(color=NOMII["primary"], cornerradius=4),
                hovertemplate="<b>%{x}</b><br>€%{y:,.0f}<extra></extra>",
            ),
            secondary_y=False,
        )
        fig_trend.add_trace(
            go.Scatter(
                x=monthly["Mes"], y=monthly["Acumulado"],
                name="Acumulado",
                mode="lines+markers",
                line=dict(color=NOMII["secondary"], width=2.5),
                marker=dict(size=5),
                hovertemplate="<b>%{x}</b><br>Acum: €%{y:,.0f}<extra></extra>",
            ),
            secondary_y=True,
        )
        fig_trend.update_layout(
            **CHART_LAYOUT,
            title=dict(text="Gasto Mensual vs Acumulado", font=dict(size=14)),
            height=400,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=11)),
            yaxis=dict(gridcolor=NOMII["grid_color"], tickformat="€,.0f"),
            yaxis2=dict(gridcolor="rgba(0,0,0,0)", tickformat="€,.0f"),
            xaxis=dict(tickangle=-45, tickfont=dict(size=10, color=T["text"])),
        )
        st.plotly_chart(fig_trend, use_container_width=True)
    
    # ── Category Donut
    with c2:
        cat_spend = (
            df.groupby("Category")["Abs_Amount"]
            .sum()
            .sort_values(ascending=False)
            .reset_index()
        )
        fig_donut = go.Figure(
            go.Pie(
                labels=cat_spend["Category"],
                values=cat_spend["Abs_Amount"],
                hole=0.55,
                marker=dict(colors=PALETTE),
                textinfo="percent",
                textfont=dict(size=11, color=T["text"]),
                hovertemplate="<b>%{label}</b><br>€%{value:,.0f}<br>%{percent}<extra></extra>",
            )
        )
        fig_donut.update_layout(
            **CHART_LAYOUT,
            title=dict(text="Distribución por Categoría", font=dict(size=14)),
            height=400,
            legend=dict(font=dict(size=10), y=0.5),
            showlegend=True,
        )
        st.plotly_chart(fig_donut, use_container_width=True)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # ROW 2: Department Spend
    # ═══════════════════════════════════════════════════════════════════════════
    st.markdown('<div class="section-title">🏢 Gasto por Departamento</div>', unsafe_allow_html=True)
    
    # Department horizontal bar
    with st.container():
        dept_spend = (
            df.groupby("Department")["Abs_Amount"]
            .sum()
            .sort_values()
            .reset_index()
        )
        fig_dept = go.Figure(
            go.Bar(
                y=dept_spend["Department"],
                x=dept_spend["Abs_Amount"],
                orientation="h",
                marker=dict(color=PALETTE[:len(dept_spend)], cornerradius=4),
                hovertemplate="<b>%{y}</b><br>€%{x:,.0f}<extra></extra>",
                text=[f"€{v:,.0f}" for v in dept_spend["Abs_Amount"]],
                textposition="outside",
                textfont=dict(size=10, color=T["text"]),
            )
        )
        fig_dept.update_layout(
            **CHART_LAYOUT,
            title=dict(text="Gasto por Departamento", font=dict(size=14)),
            height=420,
            xaxis=dict(gridcolor=NOMII["grid_color"], tickformat="€,.0f"),
            yaxis=dict(tickfont=dict(size=11, color=T["text"])),
        )
        st.plotly_chart(fig_dept, use_container_width=True)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # ROW 3: Accounting Type (OPEX/CAPEX/COR) + Cost Behavior + Business Function
    # ═══════════════════════════════════════════════════════════════════════════
    st.markdown('<div class="section-title">⚙️ Estructura Contable & Comportamiento de Costos</div>', unsafe_allow_html=True)
    
    c5, c6, c7 = st.columns(3)
    
    # ── Accounting Type stacked over time
    with c5:
        acct_monthly = (
            df.groupby(["Year_Month", "Accounting Type"])["Abs_Amount"]
            .sum()
            .reset_index()
            .sort_values("Year_Month")
        )
        acct_months_ordered = [f"{m[5:7]}/{m[0:4]}" for m in acct_monthly["Year_Month"].unique()]
        acct_monthly["Year_Month"] = acct_monthly["Year_Month"].str[5:7] + "/" + acct_monthly["Year_Month"].str[:4]
        color_map_acct = {"OPEX": NOMII["primary"], "CAPEX": NOMII["secondary"], "COR": NOMII["accent"]}
        fig_acct = px.bar(
            acct_monthly,
            x="Year_Month", y="Abs_Amount", color="Accounting Type",
            color_discrete_map=color_map_acct,
            labels={"Abs_Amount": "EUR", "Year_Month": "Mes"},
            category_orders={"Year_Month": acct_months_ordered},
        )
        fig_acct.update_layout(
            **CHART_LAYOUT,
            title=dict(text="OPEX / CAPEX / COR por Mes", font=dict(size=14)),
            height=380,
            barmode="stack",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10)),
            xaxis=dict(tickangle=-45, tickfont=dict(size=9, color=T["text"])),
            yaxis=dict(gridcolor=NOMII["grid_color"], tickformat="€,.0f"),
        )
        fig_acct.update_traces(hovertemplate="<b>%{x}</b><br>€%{y:,.0f}<extra></extra>")
        st.plotly_chart(fig_acct, use_container_width=True)
    
    # ── Cost Behavior pie
    with c6:
        cb_data = df.groupby("Cost Behavior")["Abs_Amount"].sum().reset_index()
        color_map_cb = {"Costo fijo": NOMII["primary"], "Costo variable": NOMII["secondary"], "Costo único": NOMII["accent"]}
        fig_cb = go.Figure(
            go.Pie(
                labels=cb_data["Cost Behavior"],
                values=cb_data["Abs_Amount"],
                hole=0.5,
                marker=dict(colors=[color_map_cb.get(c, "#94a3b8") for c in cb_data["Cost Behavior"]]),
                textinfo="label+percent",
                textfont=dict(size=10, color=T["text"]),
                hovertemplate="<b>%{label}</b><br>€%{value:,.0f}<br>%{percent}<extra></extra>",
            )
        )
        fig_cb.update_layout(
            **CHART_LAYOUT,
            title=dict(text="Comportamiento del Costo", font=dict(size=14)),
            height=380,
            showlegend=False,
        )
        st.plotly_chart(fig_cb, use_container_width=True)
    
    # ── Business Function treemap
    with c7:
        bf_data = df.groupby("Business Function")["Abs_Amount"].sum().reset_index()
        fig_bf = px.treemap(
            bf_data,
            path=["Business Function"],
            values="Abs_Amount",
            color="Abs_Amount",
            color_continuous_scale=[NOMII["pale_blue"], NOMII["primary"], "#001a33"],
        )
        fig_bf.update_layout(
            **CHART_LAYOUT,
            title=dict(text="Función de Negocio", font=dict(size=14)),
            height=380,
            coloraxis_showscale=False,
        )
        fig_bf.update_traces(
            hovertemplate="<b>%{label}</b><br>€%{value:,.0f}<extra></extra>",
            textinfo="label+value",
            texttemplate="<b>%{label}</b><br>€%{value:,.0f}",
        )
        st.plotly_chart(fig_bf, use_container_width=True)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # ROW 4: Trimestre / Facturación / Top Counterparties
    # ═══════════════════════════════════════════════════════════════════════════
    st.markdown('<div class="section-title">🏢 Trimestres, Facturación & Top Proveedores</div>', unsafe_allow_html=True)
    
    c8, c9 = st.columns(2)
    
    # ── Trimestre bar
    with c8:
        tri_data = (
            df.groupby("Trimestre")["Abs_Amount"]
            .sum()
            .reset_index()
            .sort_values("Trimestre")
        )
        fig_tri = go.Figure(
            go.Bar(
                x=tri_data["Trimestre"],
                y=tri_data["Abs_Amount"],
                marker=dict(
                    color=tri_data["Abs_Amount"],
                    colorscale=[[0, NOMII["pale_blue"]], [1, NOMII["primary"]]],
                    cornerradius=6,
                ),
                hovertemplate="<b>%{x}</b><br>€%{y:,.0f}<extra></extra>",
                text=[f"€{v:,.0f}" for v in tri_data["Abs_Amount"]],
                textposition="outside",
                textfont=dict(size=10, color=T["text"]),
            )
        )
        fig_tri.update_layout(
            **CHART_LAYOUT,
            title=dict(text="Gasto por Trimestre", font=dict(size=14)),
            height=380,
            xaxis=dict(tickfont=dict(size=11, color=T["text"])),
            yaxis=dict(gridcolor=NOMII["grid_color"], tickformat="€,.0f"),
        )
        st.plotly_chart(fig_tri, use_container_width=True)
    
    # ── Facturación (GmbH vs SpA) stacked area
    with c9:
        fac_monthly = (
            df.groupby(["Year_Month", "Facturacion"])["Abs_Amount"]
            .sum()
            .reset_index()
            .sort_values("Year_Month")
        )
        fac_months_ordered = [f"{m[5:7]}/{m[0:4]}" for m in fac_monthly["Year_Month"].unique()]
        fac_monthly["Year_Month"] = fac_monthly["Year_Month"].str[5:7] + "/" + fac_monthly["Year_Month"].str[:4]
        color_map_fac = {"GmbH": NOMII["primary"], "SpA": NOMII["secondary"]}
        fig_fac = px.area(
            fac_monthly,
            x="Year_Month", y="Abs_Amount", color="Facturacion",
            color_discrete_map=color_map_fac,
            labels={"Abs_Amount": "EUR", "Year_Month": "Mes"},
            category_orders={"Year_Month": fac_months_ordered},
        )
        fig_fac.update_layout(
            **CHART_LAYOUT,
            title=dict(text="Gasto por Entidad de Facturación", font=dict(size=14)),
            height=380,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=11)),
            xaxis=dict(tickangle=-45, tickfont=dict(size=9, color=T["text"])),
            yaxis=dict(gridcolor=NOMII["grid_color"], tickformat="€,.0f"),
        )
        fig_fac.update_traces(hovertemplate="<b>%{x}</b><br>€%{y:,.0f}<extra></extra>")
        st.plotly_chart(fig_fac, use_container_width=True)
    
    # ── Top 15 Counterparties
    st.markdown('<div class="section-title">🏦 Top 15 Proveedores por Gasto</div>', unsafe_allow_html=True)
    
    top_cp = (
        df.groupby("Counterparty")["Abs_Amount"]
        .sum()
        .nlargest(15)
        .sort_values()
        .reset_index()
    )
    fig_cp = go.Figure(
        go.Bar(
            y=top_cp["Counterparty"],
            x=top_cp["Abs_Amount"],
            orientation="h",
            marker=dict(
                color=top_cp["Abs_Amount"],
                colorscale=[[0, NOMII["pale_blue"]], [0.5, NOMII["light_blue"]], [1, NOMII["primary"]]],
                cornerradius=4,
            ),
            hovertemplate="<b>%{y}</b><br>€%{x:,.0f}<extra></extra>",
            text=[f"€{v:,.0f}" for v in top_cp["Abs_Amount"]],
            textposition="outside",
            textfont=dict(size=10, family="JetBrains Mono", color=T["text"]),
        )
    )
    fig_cp.update_layout(
        **{k: v for k, v in CHART_LAYOUT.items() if k != "margin"},
        height=480,
        xaxis=dict(gridcolor=NOMII["grid_color"], tickformat="€,.0f"),
        yaxis=dict(tickfont=dict(size=11, color=T["text"])),
        margin=dict(l=180, r=80, t=20, b=40),
    )
    st.plotly_chart(fig_cp, use_container_width=True)
    

    
    # ═══════════════════════════════════════════════════════════════════════════
    # DETAIL TABLE
    # ═══════════════════════════════════════════════════════════════════════════
    st.markdown('<div class="section-title">📋 Detalle de Transacciones</div>', unsafe_allow_html=True)
    
    display_cols = [
        "Date", "Invoice", "Amount in EUR", "Counterparty", "Account",
        "Category", "Sub-Category 1", "Sub-Category 2", "Trimestre",
        "Responsible Employee", "Department", "Cost Behavior",
        "Accounting Type", "Business Function", "Facturacion",
    ]
    df_display = df[display_cols].copy()
    df_display["Date"] = df_display["Date"].dt.strftime("%d/%m/%Y")
    df_display = df_display.sort_values("Date", ascending=False)
    
    st.dataframe(
        df_display,
        use_container_width=True,
        height=450,
        column_config={
            "Amount in EUR": st.column_config.NumberColumn("Amount €", format="€%.2f"),
            "Date": st.column_config.TextColumn("Date"),
        },
    )
    
# ═════════════════════════════════════════════════════════════════════════════
# TAB 3: INGRESOS
# ═════════════════════════════════════════════════════════════════════════════
with tab_ingresos:
    # Filter ingresos by date range
    df_ing = df_ingresos_raw[
        (df_ingresos_raw["FECHA"].dt.date >= d_start)
        & (df_ingresos_raw["FECHA"].dt.date <= d_end)
    ].copy()

    # ── KPI CARDS ────────────────────────────────────────────────────────────
    total_rev = df_ing["Ingreso_Abs"].sum()
    n_ing = len(df_ing)
    avg_ing = total_rev / n_ing if n_ing else 0
    n_clients = df_ing["ID CLIENTE"].nunique() if "ID CLIENTE" in df_ing.columns else 0
    total_cargo = df_ing["CARGO"].sum() if "CARGO" in df_ing.columns else 0

    # MoM change
    monthly_rev = df_ing.groupby("Year_Month")["Ingreso_Abs"].sum().sort_index()
    if len(monthly_rev) >= 2:
        last_r = monthly_rev.iloc[-1]
        prev_r = monthly_rev.iloc[-2]
        mom_rev = ((last_r - prev_r) / prev_r * 100) if prev_r else 0
        mom_cls_r = "positive" if mom_rev >= 0 else "negative"
        mom_arrow_r = "↑" if mom_rev >= 0 else "↓"
        mom_str_r = f'<div class="kpi-delta {mom_cls_r}">{mom_arrow_r} {abs(mom_rev):.1f}% vs mes anterior</div>'
    else:
        mom_str_r = ""

    # Extraer datos de clientes para MRR y Churn desde RESUMEN CLIENTES
    df_clientes = load_resumen_clientes()
    
    if df_clientes is not None and len(df_clientes) > 0 and len(df_ing) > 0:
        activos = len(df_clientes[df_clientes["ESTADO"].isin(["OK", "¡REGULARIZAR!"])])
        eliminados = len(df_clientes[df_clientes["ESTADO"] == "ELIMINADO"])
        
        avg_mrr = avg_ing  # Estimación simple de MRR promedio por cliente
        mrr_total = activos * avg_mrr if activos > 0 else total_rev
        churn_rate = (eliminados / (activos + eliminados) * 100) if (activos + eliminados) > 0 else 0
    else:
        mrr_total = total_rev
        churn_rate = 0
        activos = n_clients

    cols_r = st.columns(5)
    kpis_r = [
        ("Ingreso Neto Total", f"€{total_rev:,.0f}", mom_str_r),
        ("MRR Estimado", f"€{mrr_total:,.0f}", ""),
        ("Ticket Promedio (ARPU)", f"€{avg_ing:,.0f}", ""),
        ("Clientes Activos", f"{activos}", ""),
        ("Churn Rate", f"{churn_rate:.1f}%", f'<div class="kpi-delta {"negative" if churn_rate > 5 else "positive"}">Objetivo: < 5%</div>'),
    ]
    for col, (label, value, delta) in zip(cols_r, kpis_r):
        col.markdown(
            f'<div class="kpi-card"><div class="kpi-label">{label}</div>'
            f'<div class="kpi-value">{value}</div>{delta}</div>',
            unsafe_allow_html=True,
        )

    # ── ROW 1: Monthly Revenue Trend + Country Donut ─────────────────────
    st.markdown('<div class="section-title">📈 Tendencia de Ingresos</div>', unsafe_allow_html=True)
    ci1, ci2 = st.columns(2)

    with ci1:
        monthly_ing = (
            df_ing.groupby("Year_Month")["Ingreso_Abs"]
            .sum()
            .reset_index()
            .rename(columns={"Year_Month": "Mes", "Ingreso_Abs": "Ingreso"})
            .sort_values("Mes")
        )
        monthly_ing["Mes"] = monthly_ing["Mes"].str[5:7] + "/" + monthly_ing["Mes"].str[:4]
        monthly_ing["Acumulado"] = monthly_ing["Ingreso"].cumsum()

        fig_ing_trend = make_subplots(specs=[[{"secondary_y": True}]])
        fig_ing_trend.add_trace(
            go.Bar(
                x=monthly_ing["Mes"], y=monthly_ing["Ingreso"],
                name="Ingreso Mensual",
                marker=dict(color=NOMII["secondary"], cornerradius=4),
                hovertemplate="<b>%{x}</b><br>€%{y:,.0f}<extra></extra>",
            ),
            secondary_y=False,
        )
        fig_ing_trend.add_trace(
            go.Scatter(
                x=monthly_ing["Mes"], y=monthly_ing["Acumulado"],
                name="Acumulado",
                mode="lines+markers",
                line=dict(color=NOMII["primary"], width=2.5),
                marker=dict(size=5),
                hovertemplate="<b>%{x}</b><br>Acum: €%{y:,.0f}<extra></extra>",
            ),
            secondary_y=True,
        )
        fig_ing_trend.update_layout(
            **CHART_LAYOUT,
            title=dict(text="Ingreso Mensual vs Acumulado", font=dict(size=14)),
            height=400,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=11)),
            yaxis=dict(gridcolor=NOMII["grid_color"], tickformat="€,.0f"),
            yaxis2=dict(gridcolor="rgba(0,0,0,0)", tickformat="€,.0f"),
            xaxis=dict(tickangle=-45, tickfont=dict(size=10, color=T["text"])),
        )
        st.plotly_chart(fig_ing_trend, use_container_width=True)

    with ci2:
        if "COHORTE PAIS" in df_ing.columns:
            pais_data = (
                df_ing.groupby("COHORTE PAIS")["Ingreso_Abs"]
                .sum()
                .sort_values(ascending=False)
                .reset_index()
            )
            fig_pais = go.Figure(
                go.Pie(
                    labels=pais_data["COHORTE PAIS"],
                    values=pais_data["Ingreso_Abs"],
                    hole=0.55,
                    marker=dict(colors=PALETTE),
                    textinfo="percent",
                    textfont=dict(size=11, color=T["text"]),
                    hovertemplate="<b>%{label}</b><br>€%{value:,.0f}<br>%{percent}<extra></extra>",
                )
            )
            fig_pais.update_layout(
                **CHART_LAYOUT,
                title=dict(text="Distribución por País", font=dict(size=14)),
                height=400,
                legend=dict(font=dict(size=10), y=0.5),
                showlegend=True,
            )
            st.plotly_chart(fig_pais, use_container_width=True)
        else:
            st.info("No hay datos de país disponibles.")

    # ── ROW 2: Cohort Revenue + Monthly Clients ─────────────────────────
    st.markdown('<div class="section-title">👥 Cohortes & Clientes</div>', unsafe_allow_html=True)
    ci3, ci4 = st.columns(2)

    with ci3:
        if "COHORTE INGRESO" in df_ing.columns:
            # Primero, obtener los ingresos por cohorte y periodo (mes)
            coh_trend = df_ing.groupby(["Year_Month", "COHORTE INGRESO"])["Ingreso_Abs"].sum().reset_index()
            
            # Para no tener demasiadas capas (son muchas cohortes), filtramos a las 12 mayores
            top_cohortes = (
                df_ing.groupby("COHORTE INGRESO")["Ingreso_Abs"]
                .sum()
                .nlargest(12)
                .index
            )
            coh_trend = coh_trend[coh_trend["COHORTE INGRESO"].isin(top_cohortes)]
            
            # Crear figura de área apilada (Layer Cake)
            fig_coh = go.Figure()
            
            colors = PALETTE[:len(top_cohortes)]
            
            # Formatear el nombre de la cohorte para display
            def format_cohorte(c):
                if isinstance(c, pd.Timestamp):
                    return c.strftime('%m/%Y')
                return str(c).replace(" 00:00:00", "")

            # Ordenar cohortes: Invertimos para que las más grandes/antiguas tiendan a quedar en la base
            sorted_cohortes = list(top_cohortes)[::-1] 

            for idx, cohorte in enumerate(sorted_cohortes):
                df_c = coh_trend[coh_trend["COHORTE INGRESO"] == cohorte].sort_values("Year_Month").copy()
                df_c["Year_Month"] = df_c["Year_Month"].str[5:7] + "/" + df_c["Year_Month"].str[:4]
                cohorte_name = format_cohorte(cohorte)

                fig_coh.add_trace(go.Scatter(
                    x=df_c["Year_Month"],
                    y=df_c["Ingreso_Abs"],
                    mode="lines",
                    stackgroup="one", # Esto crea el efecto Layer Cake
                    name=cohorte_name,
                    line=dict(width=0, color=colors[idx % len(colors)]),
                    hovertemplate=f"<b>Cohorte {cohorte_name}</b><br>Mes: %{{x}}<br>Ingreso: €%{{y:,.0f}}<extra></extra>"
                ))

            fig_coh.update_layout(
                **{k: v for k, v in CHART_LAYOUT.items() if k != "margin"},
                title=dict(text="Evolución Ingresos por Cohorte (Top 12)", font=dict(size=14)),
                height=420,
                xaxis=dict(gridcolor=NOMII["grid_color"], type="category", tickangle=-45),
                yaxis=dict(gridcolor=NOMII["grid_color"], tickformat="€,.0f", tickfont=dict(size=10, color=T["text"])),
                margin=dict(l=40, r=20, t=40, b=40),
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.5, xanchor="center", x=0.5, font=dict(size=10))
            )
            st.plotly_chart(fig_coh, use_container_width=True)
        else:
            st.info("No hay datos de cohorte disponibles.")

    with ci4:
        if "ID CLIENTE" in df_ing.columns:
            clients_monthly = (
                df_ing.groupby("Year_Month")["ID CLIENTE"]
                .nunique()
                .reset_index()
                .rename(columns={"Year_Month": "Mes", "ID CLIENTE": "Clientes"})
                .sort_values("Mes")
            )
            clients_monthly["Mes"] = clients_monthly["Mes"].str[5:7] + "/" + clients_monthly["Mes"].str[:4]
            fig_clients = go.Figure(
                go.Scatter(
                    x=clients_monthly["Mes"],
                    y=clients_monthly["Clientes"],
                    mode="lines+markers+text",
                    line=dict(color=NOMII["secondary"], width=3),
                    marker=dict(size=8, color=NOMII["primary"]),
                    text=clients_monthly["Clientes"],
                    textposition="top center",
                    textfont=dict(size=10, color=NOMII["text"]),
                    hovertemplate="<b>%{x}</b><br>%{y} clientes<extra></extra>",
                )
            )
            fig_clients.update_layout(
                **CHART_LAYOUT,
                title=dict(text="Clientes Activos por Mes", font=dict(size=14)),
                height=420,
                xaxis=dict(tickangle=-45, tickfont=dict(size=10, color=T["text"])),
                yaxis=dict(gridcolor=NOMII["grid_color"]),
            )
            st.plotly_chart(fig_clients, use_container_width=True)
        else:
            st.info("No hay datos de clientes disponibles.")

    # ── DETAIL TABLE ────────────────────────────────────────────────────
    st.markdown('<div class="section-title">📋 Detalle de Ingresos</div>', unsafe_allow_html=True)

    ing_cols = [c for c in ["FECHA", "NOMBRE", "ID CLIENTE", "IMPORTE", "CARGO", " INGRESO NETO",
                            "MONEDA", "CL / DE", "COHORTE INGRESO", "COHORTE PAIS"] if c in df_ing.columns]
    df_ing_display = df_ing[ing_cols].copy()
    df_ing_display["FECHA"] = df_ing_display["FECHA"].dt.strftime("%d/%m/%Y")
    df_ing_display = df_ing_display.sort_values("FECHA", ascending=False)

    st.dataframe(
        df_ing_display,
        use_container_width=True,
        height=450,
        column_config={
            "IMPORTE": st.column_config.NumberColumn("Importe €", format="€%.2f"),
            " INGRESO NETO": st.column_config.NumberColumn("Ingreso Neto €", format="€%.2f"),
            "CARGO": st.column_config.NumberColumn("Cargo €", format="€%.2f"),
        },
    )

# ═════════════════════════════════════════════════════════════════════════════
# TAB 1: KPIs EJECUTIVOS
# ═════════════════════════════════════════════════════════════════════════════
with tab_kpis:
    # ── Month Selector ──────────────────────────────────────────────────────
    available_months = sorted(df_calendario["FECHA"].dropna().dt.to_period("M").unique())
    month_labels_internal = [str(m) for m in available_months]  # "YYYY-MM" para uso interno
    month_labels = [m.strftime("%m/%Y") for m in available_months]  # "MM/YYYY" para mostrar
    current_month_str = datetime.now().strftime("%Y-%m")
    if current_month_str in month_labels_internal:
        default_idx = month_labels_internal.index(current_month_str)
    else:
        default_idx = len(month_labels_internal) - 1 if month_labels_internal else 0
    sel_month_label = st.selectbox("📅 Selecciona el mes", month_labels, index=default_idx)
    sel_period = available_months[month_labels.index(sel_month_label)]

    # ── Filter data for selected month ─────────────────────────────────────
    cal_month = df_calendario[df_calendario["FECHA"].dt.to_period("M") == sel_period]

    # Revenue KPIs
    total_planificado = cal_month["MONTO"].sum()
    pagadas = cal_month[cal_month["ESTADO FACTURA"] == "PAGADA"]
    ingreso_cobrado = pagadas["MONTO"].sum()
    cantidad_cobrada = len(pagadas)
    ratio_cobranza = (ingreso_cobrado / total_planificado * 100) if total_planificado else 0

    # Receivables KPIs
    pendiente = total_planificado - ingreso_cobrado
    atrasadas = cal_month[cal_month["ESTADO FACTURA"] == "EMITIDA"]
    cuotas_atrasadas_monto = atrasadas["MONTO"].sum()
    cuotas_atrasadas_cant = len(atrasadas)
    por_cobrar = cal_month[cal_month["ESTADO FACTURA"] == "POR EMITIR"]
    cuotas_por_cobrar_monto = por_cobrar["MONTO"].sum()
    cuotas_por_cobrar_cant = len(por_cobrar)

    # Expenses KPI
    sal_month = df[
        (df["Date"].dt.to_period("M") == sel_period)
    ] if "Date" in df.columns else pd.DataFrame()
    total_salidas = sal_month["Amount in EUR"].sum() if len(sal_month) > 0 else 0

    # Margin and EBITDA
    margen_bruto = ingreso_cobrado + total_salidas  # salidas is negative
    # EBITDA = Margen Bruto - (COR expenses which are recurrent SaaS-like costs)
    cor_expenses = sal_month[sal_month["Accounting Type"] == "COR"]["Amount in EUR"].sum().item() if len(sal_month) > 0 and "Accounting Type" in sal_month.columns else 0
    ebitda = margen_bruto + cor_expenses  # cor_expenses is negative, so this subtracts

    # Client KPIs
    coh_month = df_cohortes[df_cohortes["MES"].dt.to_period("M") == sel_period]
    if len(coh_month) > 0:
        row_coh = coh_month.iloc[0]
        clientes_activos = int(row_coh.get("CANTIDAD CLIENTES ACTIVOS X MES", 0))
        nuevos_clientes = int(row_coh.get("NUEVOS CLIENTES TOTAL", 0))
        eliminados_mes = int(row_coh.get("ELIMINADOS X MES", 0))
    else:
        # Fallback to RESUMEN CLIENTES
        clientes_activos = len(df_clientes[df_clientes["ESTADO"] == "OK"])
        nuevos_clientes = 0
        eliminados_mes = 0

    # ── RENDER KPIs ───────────────────────────────────────────────────────
    st.markdown(f"""
    <style>
    .exec-row {{ display: flex; gap: 1rem; margin-bottom: 1.2rem; flex-wrap: wrap; }}
    .exec-card {{
        flex: 1; min-width: 180px; background: {T['card_bg']}; border: 1px solid {T['card_border']};
        border-radius: 14px; padding: 1.3rem 1.5rem; text-align: left;
        box-shadow: 0 1px 4px rgba(0,0,0,{'0.15' if dark else '0.04'});
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }}
    .exec-card:hover {{ transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0,0,0,{'0.3' if dark else '0.07'}); }}
    .exec-card.highlight {{ border-color: {T['section_border']}; }}
    .exec-card.warn {{ border-color: #e74c3c; }}
    .exec-card.green {{ border-color: #20C6B6; }}
    .exec-label {{ font-size: 0.72rem; font-weight: 600; text-transform: uppercase;
                   letter-spacing: 0.8px; color: {T['label_color']}; margin-bottom: 0.35rem; }}
    .exec-value {{ font-family: 'JetBrains Mono', monospace; font-size: 1.55rem;
                   font-weight: 700; color: {T['kpi_value']}; line-height: 1.2; }}
    .exec-value.turquoise {{ color: #20C6B6; }}
    .exec-value.red {{ color: {'#FF6B6B' if dark else '#e74c3c'}; }}
    .exec-value.green {{ color: {'#3BC97C' if dark else '#0a8f5f'}; }}
    .exec-sub {{ font-size: 0.75rem; color: {T['text2']}; margin-top: 0.2rem; }}
    .exec-section {{ font-size: 0.9rem; font-weight: 700; color: {T['heading']}; margin: 1.5rem 0 0.6rem;
                     border-bottom: 2px solid {T['section_border']}; padding-bottom: 0.3rem; }}
    </style>

    <div class="exec-section">💰 Ingresos — {sel_month_label}</div>
    <div class="exec-row">
        <div class="exec-card highlight">
            <div class="exec-label">Total Ingreso Planificado</div>
            <div class="exec-value">€{total_planificado:,.0f}</div>
        </div>
        <div class="exec-card">
            <div class="exec-label">Ingreso Cobrado</div>
            <div class="exec-value turquoise">€{ingreso_cobrado:,.0f}</div>
        </div>
        <div class="exec-card">
            <div class="exec-label">Cantidad</div>
            <div class="exec-value">{cantidad_cobrada}</div>
        </div>
        <div class="exec-card highlight">
            <div class="exec-label">Ratio Cobranza</div>
            <div class="exec-value turquoise">{ratio_cobranza:.0f}%</div>
        </div>
    </div>

    <div class="exec-section">📋 Cuentas por Cobrar</div>
    <div class="exec-row">
        <div class="exec-card warn">
            <div class="exec-label">Ingreso Pendiente por Cobrar</div>
            <div class="exec-value red">€{pendiente:,.0f}</div>
        </div>
        <div class="exec-card">
            <div class="exec-label">Cuotas Atrasadas</div>
            <div class="exec-value red">€{cuotas_atrasadas_monto:,.0f}</div>
            <div class="exec-sub">Cantidad: {cuotas_atrasadas_cant}</div>
        </div>
        <div class="exec-card">
            <div class="exec-label">Cuotas por Cobrar</div>
            <div class="exec-value">€{cuotas_por_cobrar_monto:,.0f}</div>
            <div class="exec-sub">Cantidad: {cuotas_por_cobrar_cant}</div>
        </div>
    </div>

    <div class="exec-section">📊 Resultados Financieros</div>
    <div class="exec-row">
        <div class="exec-card">
            <div class="exec-label">Total Salidas</div>
            <div class="exec-value red">€{total_salidas:,.2f}</div>
        </div>
        <div class="exec-card highlight">
            <div class="exec-label">Margen Bruto</div>
            <div class="exec-value {'green' if margen_bruto >= 0 else 'red'}">€{margen_bruto:,.2f}</div>
        </div>
        <div class="exec-card highlight">
            <div class="exec-label">EBITDA</div>
            <div class="exec-value {'green' if ebitda >= 0 else 'red'}">€{ebitda:,.2f}</div>
        </div>
    </div>

    <div class="exec-section">👥 Clientes — {sel_month_label}</div>
    <div class="exec-row">
        <div class="exec-card green">
            <div class="exec-label">Total Clientes Activos</div>
            <div class="exec-value">{clientes_activos}</div>
        </div>
        <div class="exec-card">
            <div class="exec-label">Nuevos Clientes</div>
            <div class="exec-value turquoise">{nuevos_clientes}</div>
        </div>
        <div class="exec-card">
            <div class="exec-label">Clientes Eliminados</div>
            <div class="exec-value">{eliminados_mes}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # CAMBIO 5: Expander con detalle de clientes atrasados
    if cuotas_atrasadas_cant > 0:
        with st.expander(f"⚠️ Ver {cuotas_atrasadas_cant} cuota(s) atrasada(s) — Detalle de clientes"):
            detail_cols = [c for c in ["NOMBRE", "MONTO", "N° FACTURA", "FECHA", "PAIS", "ESTADO", "NOTA"] if c in atrasadas.columns]
            df_atrasadas_display = atrasadas[detail_cols].copy()
            if "FECHA" in df_atrasadas_display.columns:
                df_atrasadas_display["FECHA"] = pd.to_datetime(df_atrasadas_display["FECHA"]).dt.strftime("%d/%m/%Y")
            df_atrasadas_display = df_atrasadas_display.sort_values("MONTO", ascending=False)
            st.dataframe(
                df_atrasadas_display,
                use_container_width=True,
                height=min(38 * len(df_atrasadas_display) + 50, 400),
                column_config={
                    "MONTO": st.column_config.NumberColumn("Monto €", format="€%.2f"),
                    "NOMBRE": st.column_config.TextColumn("Cliente", width="large"),
                    "N° FACTURA": st.column_config.TextColumn("N° Factura"),
                    "FECHA": st.column_config.TextColumn("Fecha"),
                    "PAIS": st.column_config.TextColumn("País"),
                    "NOTA": st.column_config.LinkColumn("Link Factura", display_text="Ver factura"),
                },
                hide_index=True,
            )

    # ── Mini Charts ──────────────────────────────────────────────────────
    st.markdown('<div class="section-title">📈 Evolución Mensual</div>', unsafe_allow_html=True)
    ck1, ck2 = st.columns(2)

    with ck1:
        # Monthly planned vs collected
        plan_hist = (
            df_calendario.groupby(df_calendario["FECHA"].dt.to_period("M"))
            .agg(Planificado=("MONTO", "sum"))
            .reset_index()
        )
        paid_hist = (
            df_calendario[df_calendario["ESTADO FACTURA"] == "PAGADA"]
            .groupby(df_calendario.loc[df_calendario["ESTADO FACTURA"] == "PAGADA", "FECHA"].dt.to_period("M"))
            .agg(Cobrado=("MONTO", "sum"))
            .reset_index()
        )
        plan_hist["Mes"] = plan_hist["FECHA"].astype(str)
        paid_hist["Mes"] = paid_hist["FECHA"].astype(str)
        merged = plan_hist.merge(paid_hist[["Mes", "Cobrado"]], on="Mes", how="left").fillna(0).sort_values("Mes")
        merged["Mes"] = merged["Mes"].str[5:7] + "/" + merged["Mes"].str[:4]

        fig_plan = go.Figure()
        fig_plan.add_trace(go.Bar(x=merged["Mes"], y=merged["Planificado"], name="Planificado",
                                   marker=dict(color=NOMII["pale_blue"], cornerradius=4)))
        fig_plan.add_trace(go.Bar(x=merged["Mes"], y=merged["Cobrado"], name="Cobrado",
                                   marker=dict(color=NOMII["secondary"], cornerradius=4)))
        fig_plan.update_layout(
            **CHART_LAYOUT,
            title=dict(text="Planificado vs Cobrado por Mes", font=dict(size=14)),
            barmode="overlay", height=380,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=11)),
            yaxis=dict(gridcolor=NOMII["grid_color"], tickformat="€,.0f"),
            xaxis=dict(tickangle=-45, tickfont=dict(size=10, color=T["text"])),
        )
        st.plotly_chart(fig_plan, use_container_width=True)

    with ck2:
        # Client evolution
        coh_sorted = df_cohortes.dropna(subset=["MES"]).sort_values("MES").copy()
        coh_sorted["Mes"] = coh_sorted["MES"].dt.strftime("%m/%Y")
        if "CANTIDAD CLIENTES ACTIVOS X MES" in coh_sorted.columns:
            fig_cli = go.Figure()
            fig_cli.add_trace(go.Scatter(
                x=coh_sorted["Mes"],
                y=coh_sorted["CANTIDAD CLIENTES ACTIVOS X MES"],
                mode="lines+markers+text",
                name="Clientes Activos",
                line=dict(color=NOMII["primary"], width=3),
                marker=dict(size=8),
                text=coh_sorted["CANTIDAD CLIENTES ACTIVOS X MES"].astype(int),
                textposition="top center",
                textfont=dict(size=10, color=T["text"]),
            ))
            if "NUEVOS CLIENTES TOTAL" in coh_sorted.columns:
                fig_cli.add_trace(go.Bar(
                    x=coh_sorted["Mes"],
                    y=coh_sorted["NUEVOS CLIENTES TOTAL"],
                    name="Nuevos",
                    marker=dict(color=NOMII["secondary"], cornerradius=4),
                    opacity=0.7,
                ))
            fig_cli.update_layout(
                **CHART_LAYOUT,
                title=dict(text="Evolución de Clientes", font=dict(size=14)),
                height=380,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=11)),
                yaxis=dict(gridcolor=NOMII["grid_color"]),
                xaxis=dict(tickangle=-45, tickfont=dict(size=10, color=T["text"])),
            )
            st.plotly_chart(fig_cli, use_container_width=True)

# ═════════════════════════════════════════════════════════════════════════════
# TAB 2: ESTADO DE RESULTADOS (EERR)
# ═════════════════════════════════════════════════════════════════════════════
with tab_eerr:
    st.markdown('<div class="section-title">📑 Estado de Resultados Mensual</div>', unsafe_allow_html=True)

    # ── Build P&L from INGRESOS and SALIDAS ─────────────────────────────
    ing_raw = df_ingresos_raw.copy()
    sal_raw = df_raw.copy()

    all_months = sorted(set(
        list(ing_raw["FECHA"].dt.to_period("M").dropna().unique()) +
        list(sal_raw["Date"].dt.to_period("M").dropna().unique())
    ))

    eerr_rows = []
    for period in all_months:
        ing_m = ing_raw[ing_raw["FECHA"].dt.to_period("M") == period]
        ingreso_cobrado = ing_m["Ingreso_Abs"].sum() if len(ing_m) > 0 else 0

        sal_m = sal_raw[sal_raw["Date"].dt.to_period("M") == period]
        cor = sal_m[sal_m["Accounting Type"] == "COR"]["Amount in EUR"].sum() if len(sal_m) > 0 else 0
        opex = sal_m[sal_m["Accounting Type"] == "OPEX"]["Amount in EUR"].sum() if len(sal_m) > 0 else 0
        capex = sal_m[sal_m["Accounting Type"] == "CAPEX"]["Amount in EUR"].sum() if len(sal_m) > 0 else 0

        # OPEX sub-categorías mutuamente excluyentes: Software primero, luego por Departamento
        opex_sw = sal_m[
            (sal_m["Accounting Type"] == "OPEX") & (sal_m["Category"] == "Software")
        ]["Amount in EUR"].sum() if len(sal_m) > 0 else 0
        opex_mkt = sal_m[
            (sal_m["Accounting Type"] == "OPEX") &
            (sal_m["Department"] == "Marketing") &
            (sal_m["Category"] != "Software")
        ]["Amount in EUR"].sum() if len(sal_m) > 0 else 0
        opex_ops = sal_m[
            (sal_m["Accounting Type"] == "OPEX") &
            (sal_m["Department"] == "Operaciones") &
            (sal_m["Category"] != "Software")
        ]["Amount in EUR"].sum() if len(sal_m) > 0 else 0
        opex_gen = opex - opex_sw - opex_mkt - opex_ops

        margen_bruto = ingreso_cobrado + cor
        ebitda = margen_bruto + opex
        fcf = ebitda + capex

        eerr_rows.append({
            "Mes": period.strftime("%m/%Y"),
            "Ingreso Cobrado": ingreso_cobrado,
            "COR": cor,
            "Margen Bruto": margen_bruto,
            "% Margen": (margen_bruto / ingreso_cobrado * 100) if ingreso_cobrado > 0 else 0,
            "OPEX Total": opex,
            "OPEX Software": opex_sw,
            "OPEX Marketing": opex_mkt,
            "OPEX Operaciones": opex_ops,
            "OPEX General": opex_gen,
            "EBITDA": ebitda,
            "% EBITDA": (ebitda / ingreso_cobrado * 100) if ingreso_cobrado > 0 else 0,
            "CAPEX": capex,
            "FCF": fcf,
        })

    df_eerr = pd.DataFrame(eerr_rows)

    # ── Month selector ────────────────────────────────────────────────────
    months_with_data = [r["Mes"] for r in eerr_rows if r["Ingreso Cobrado"] != 0 or r["OPEX Total"] != 0]
    if not months_with_data:
        months_with_data = [r["Mes"] for r in eerr_rows]
    sel_eerr_month = st.selectbox(
        "📅 Mes para Cascada P&L",
        options=months_with_data,
        index=len(months_with_data) - 1,
        key="sel_eerr_month",
    )
    sel_row = df_eerr[df_eerr["Mes"] == sel_eerr_month].iloc[0]

    # ── KPI Cards ─────────────────────────────────────────────────────────
    kpi_cols_e = st.columns(6)
    eerr_kpis = [
        ("Ingreso Cobrado", f"€{sel_row['Ingreso Cobrado']:,.0f}", ""),
        ("COR", f"€{sel_row['COR']:,.0f}", ""),
        ("Margen Bruto", f"€{sel_row['Margen Bruto']:,.0f}",
         f'<div class="kpi-delta {"positive" if sel_row["Margen Bruto"] >= 0 else "negative"}">'
         f'{sel_row["% Margen"]:.1f}%</div>'),
        ("OPEX Total", f"€{sel_row['OPEX Total']:,.0f}", ""),
        ("EBITDA", f"€{sel_row['EBITDA']:,.0f}",
         f'<div class="kpi-delta {"positive" if sel_row["EBITDA"] >= 0 else "negative"}">'
         f'{sel_row["% EBITDA"]:.1f}%</div>'),
        ("FCF", f"€{sel_row['FCF']:,.0f}", ""),
    ]
    for col, (label, value, delta) in zip(kpi_cols_e, eerr_kpis):
        col.markdown(
            f'<div class="kpi-card"><div class="kpi-label">{label}</div>'
            f'<div class="kpi-value">{value}</div>{delta}</div>',
            unsafe_allow_html=True,
        )

    # ── ROW 1: P&L Waterfall (mes seleccionado) + Evolución márgenes ─────
    ce1, ce2 = st.columns(2)

    with ce1:
        wf_labels = ["Ingreso", "COR", "Margen Bruto", "OPEX", "Total Salidas", "EBITDA", "CAPEX", "FCF"]
        
        # Calculate Total Salidas
        total_salidas = sel_row["COR"] + sel_row["OPEX Total"] + sel_row["CAPEX"]
        
        wf_values = [
            sel_row["Ingreso Cobrado"],
            sel_row["COR"],
            sel_row["Margen Bruto"],
            sel_row["OPEX Total"],
            total_salidas,
            sel_row["EBITDA"],
            sel_row["CAPEX"],
            sel_row["FCF"],
        ]
        wf_measure = ["absolute", "relative", "total", "relative", "total", "total", "relative", "total"]

        # Format text to show negative values as absolute numbers for readability
        wf_text = [f"€{abs(v):,.0f}" for v in wf_values]

        fig_wf = go.Figure(go.Waterfall(
            x=wf_labels,
            y=wf_values,
            measure=wf_measure,
            connector=dict(line=dict(color="#B3D9EA", width=1)),
            increasing=dict(marker=dict(color=NOMII["secondary"])),
            decreasing=dict(marker=dict(color="#e74c3c")),
            totals=dict(marker=dict(color=NOMII["primary"])),
            textposition="outside",
            text=wf_text,
            textfont=dict(size=10, color=T["text"]),
        ))
        fig_wf.update_layout(
            **CHART_LAYOUT,
            title=dict(text=f"Cascada P&L — {sel_eerr_month}", font=dict(size=14)),
            height=420,
            yaxis=dict(gridcolor=NOMII["grid_color"], tickformat="€,.0f"),
            showlegend=False,
        )
        st.plotly_chart(fig_wf, use_container_width=True)

    with ce2:
        fig_margin = go.Figure()
        fig_margin.add_trace(go.Scatter(
            x=df_eerr["Mes"], y=df_eerr["% Margen"],
            name="% Margen Bruto",
            mode="lines+markers",
            line=dict(color=NOMII["secondary"], width=2.5),
            marker=dict(size=6),
            hovertemplate="<b>%{x}</b><br>Margen: %{y:.1f}%<extra></extra>",
        ))
        fig_margin.add_trace(go.Scatter(
            x=df_eerr["Mes"], y=df_eerr["% EBITDA"],
            name="% EBITDA",
            mode="lines+markers",
            line=dict(color=NOMII["primary"], width=2.5),
            marker=dict(size=6),
            hovertemplate="<b>%{x}</b><br>EBITDA: %{y:.1f}%<extra></extra>",
        ))
        fig_margin.add_vline(x=sel_eerr_month, line_dash="dot", line_color=NOMII["accent"], line_width=2)
        fig_margin.add_hline(y=0, line_dash="dash", line_color="#94a3b8", line_width=1)
        fig_margin.update_layout(
            **CHART_LAYOUT,
            title=dict(text="Evolución de Márgenes (%)", font=dict(size=14)),
            height=420,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=11)),
            yaxis=dict(gridcolor=NOMII["grid_color"], ticksuffix="%"),
            xaxis=dict(tickangle=-45, tickfont=dict(size=10, color=T["text"])),
        )
        st.plotly_chart(fig_margin, use_container_width=True)

    # ── ROW 2: OPEX Breakdown + FCF con eje Y secundario ─────────────────
    st.markdown('<div class="section-title">📊 Desglose OPEX & Flujo de Caja</div>', unsafe_allow_html=True)
    ce3, ce4 = st.columns(2)

    with ce3:
        fig_opex = go.Figure()
        opex_cats = [
            ("Software", "OPEX Software", NOMII["primary"]),
            ("Marketing", "OPEX Marketing", NOMII["secondary"]),
            ("Operaciones", "OPEX Operaciones", NOMII["accent"]),
            ("General", "OPEX General", NOMII["light_blue"]),
        ]
        for name, col, color in opex_cats:
            fig_opex.add_trace(go.Bar(
                x=df_eerr["Mes"],
                y=df_eerr[col].abs(),
                name=name,
                marker=dict(color=color, cornerradius=2),
                hovertemplate=f"<b>{name}</b><br>%{{x}}<br>€%{{y:,.0f}}<extra></extra>",
            ))
        fig_opex.update_layout(
            **CHART_LAYOUT,
            title=dict(text="Desglose OPEX por Área", font=dict(size=14)),
            barmode="stack", height=420,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=11)),
            yaxis=dict(gridcolor=NOMII["grid_color"], tickformat="€,.0f"),
            xaxis=dict(tickangle=-45, tickfont=dict(size=10, color=T["text"])),
        )
        st.plotly_chart(fig_opex, use_container_width=True)

    with ce4:
        df_eerr["FCF_Acum"] = df_eerr["FCF"].cumsum()
        fig_fcf = make_subplots(specs=[[{"secondary_y": True}]])
        fig_fcf.add_trace(
            go.Bar(
                x=df_eerr["Mes"], y=df_eerr["FCF"],
                name="FCF Mensual",
                marker=dict(
                    color=[NOMII["secondary"] if v >= 0 else "#e74c3c" for v in df_eerr["FCF"]],
                    cornerradius=4,
                ),
                hovertemplate="<b>%{x}</b><br>FCF: €%{y:,.0f}<extra></extra>",
            ),
            secondary_y=False,
        )
        fig_fcf.add_trace(
            go.Scatter(
                x=df_eerr["Mes"], y=df_eerr["FCF_Acum"],
                name="FCF Acumulado",
                mode="lines+markers",
                line=dict(color=NOMII["primary"], width=2.5),
                marker=dict(size=5),
                hovertemplate="<b>%{x}</b><br>Acum: €%{y:,.0f}<extra></extra>",
            ),
            secondary_y=True,
        )
        fig_fcf.add_hline(y=0, line_dash="dash", line_color="#94a3b8", line_width=1)
        fig_fcf.update_layout(
            **CHART_LAYOUT,
            title=dict(text="Flujo de Caja Libre (FCF)", font=dict(size=14)),
            height=420,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=11)),
            yaxis=dict(gridcolor=NOMII["grid_color"], tickformat="€,.0f", title_text="FCF Mensual"),
            yaxis2=dict(gridcolor="rgba(0,0,0,0)", tickformat="€,.0f", title_text="FCF Acumulado"),
            xaxis=dict(tickangle=-45, tickfont=dict(size=10, color=T["text"])),
        )
        st.plotly_chart(fig_fcf, use_container_width=True)

    # ── ROW 3: Ingreso vs EBITDA bars ─────────────────────────────────────
    st.markdown('<div class="section-title">💶 Ingreso vs EBITDA</div>', unsafe_allow_html=True)
    fig_ie = go.Figure()
    fig_ie.add_trace(go.Bar(
        x=df_eerr["Mes"], y=df_eerr["Ingreso Cobrado"],
        name="Ingreso", marker=dict(color=NOMII["pale_blue"], cornerradius=4),
    ))
    fig_ie.add_trace(go.Bar(
        x=df_eerr["Mes"], y=df_eerr["EBITDA"],
        name="EBITDA",
        marker=dict(
            color=[NOMII["secondary"] if v >= 0 else "#e74c3c" for v in df_eerr["EBITDA"]],
            cornerradius=4,
        ),
    ))
    fig_ie.update_layout(
        **CHART_LAYOUT,
        title=dict(text="Ingreso Cobrado vs EBITDA por Mes", font=dict(size=14)),
        barmode="group", height=400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=11)),
        yaxis=dict(gridcolor=NOMII["grid_color"], tickformat="€,.0f"),
        xaxis=dict(tickangle=-45, tickfont=dict(size=10, color=T["text"])),
    )
    st.plotly_chart(fig_ie, use_container_width=True)

    # ── Financial Table ──────────────────────────────────────────────────
    st.markdown('<div class="section-title">📋 Tabla Estado de Resultados</div>', unsafe_allow_html=True)

    # Sort descending so the latest month is first
    display_eerr = df_eerr[["Mes", "Ingreso Cobrado", "COR", "Margen Bruto", "% Margen",
                             "OPEX Total", "EBITDA", "% EBITDA", "CAPEX", "FCF"]].copy()
    display_eerr = display_eerr.sort_values(by="Mes", ascending=False)

    st.dataframe(
        display_eerr,
        use_container_width=True,
        height=450,
        column_config={
            "Ingreso Cobrado": st.column_config.NumberColumn(format="€%.0f"),
            "COR": st.column_config.NumberColumn(format="€%.0f"),
            "Margen Bruto": st.column_config.NumberColumn(format="€%.0f"),
            "% Margen": st.column_config.NumberColumn(format="%.1f%%"),
            "OPEX Total": st.column_config.NumberColumn(format="€%.0f"),
            "EBITDA": st.column_config.NumberColumn(format="€%.0f"),
            "% EBITDA": st.column_config.NumberColumn(format="%.1f%%"),
            "CAPEX": st.column_config.NumberColumn(format="€%.0f"),
            "FCF": st.column_config.NumberColumn(format="€%.0f"),
        },
    )

# ─── FOOTER ─────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<p style="text-align:center; color:#94a3b8; font-size:0.78rem;">'
    'NOMII Finance Dashboard · Datos actualizados desde Excel/SharePoint · '
    f'Generado el {datetime.now().strftime("%d/%m/%Y %H:%M")}'
    '<br>Desarrollado por Giovanny Bravo para NOMII GmbH</p>',
    unsafe_allow_html=True,
)
