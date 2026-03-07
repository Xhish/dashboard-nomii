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

# ─── CUSTOM CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* Global */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}
.block-container { padding-top: 1.5rem; padding-bottom: 1rem; }

/* Header */
.main-header {
    background: linear-gradient(135deg, #002244 0%, #003366 50%, #002244 100%);
    padding: 1.8rem 2.2rem;
    border-radius: 16px;
    margin-bottom: 1.5rem;
    border: 1px solid rgba(32,198,182,0.2);
    box-shadow: 0 4px 24px rgba(0,51,102,0.15);
}
.main-header h1 {
    color: #f8fafc;
    font-size: 1.7rem;
    font-weight: 700;
    margin: 0;
    letter-spacing: -0.5px;
}
.main-header p {
    color: #B3D9EA;
    font-size: 0.88rem;
    margin: 0.3rem 0 0 0;
}
.accent-dot { color: #20C6B6; }

/* KPI Cards */
.kpi-card {
    background: #ffffff;
    border: 1px solid #B3D9EA;
    border-radius: 14px;
    padding: 1.3rem 1.5rem;
    text-align: left;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.kpi-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0,0,0,0.07);
}
.kpi-label {
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: #4D7EA8;
    margin-bottom: 0.35rem;
}
.kpi-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.55rem;
    font-weight: 700;
    color: #003366;
    line-height: 1.2;
}
.kpi-delta {
    font-size: 0.78rem;
    font-weight: 600;
    margin-top: 0.25rem;
}
.kpi-delta.positive { color: #20C6B6; }
.kpi-delta.negative { color: #ef4444; }

/* Section titles */
.section-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: #003366;
    margin: 1.8rem 0 0.8rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #20C6B6;
    letter-spacing: -0.3px;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #F9F9F9;
    border-right: 1px solid #B3D9EA;
}
section[data-testid="stSidebar"] .stMarkdown h3 {
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #003366;
    font-weight: 600;
    margin-top: 1rem;
}

/* Hide streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Plotly charts container */
.stPlotlyChart {
    border-radius: 12px;
    overflow: hidden;
}
</style>
""", unsafe_allow_html=True)

# ─── NOMII INSTITUTIONAL COLORS ────────────────────────────────────────────
NOMII = {
    "primary": "#003366",      # Azul Profundo
    "secondary": "#20C6B6",    # Turquesa Clínico
    "accent": "#FFCC00",       # Dorado
    "text": "#333333",         # Gris oscuro
    "background": "#F9F9F9",   # Fondo suave
    "light_blue": "#4D7EA8",
    "pale_blue": "#B3D9EA",
}

PALETTE = [
    "#003366", "#20C6B6", "#4D7EA8", "#FFCC00", "#B3D9EA",  # NOMII core
    "#005599", "#17a89c", "#6A9BC3", "#FFD633", "#CCE5F0",  # NOMII lighter
    "#001a33", "#0f8a7e", "#3a6d8c", "#CC9900", "#8AB8D0",  # NOMII darker
]

CHART_LAYOUT = dict(
    font=dict(family="DM Sans", color=NOMII["text"]),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=40, r=20, t=40, b=40),
    hoverlabel=dict(
        bgcolor=NOMII["primary"],
        font_size=12,
        font_family="DM Sans",
        font_color="#f8fafc",
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
            download_url = sharepoint_url.replace("?e=", "?download=1&e=")
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
    df["Month_Name"] = df["Date"].dt.strftime("%b %Y")
    df["Year_Month"] = df["Date"].dt.to_period("M").astype(str)
    return df


df_raw = load_data()

# ─── SIDEBAR FILTERS ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔎 Filtros")

    st.markdown("### Período")
    min_date = df_raw["Date"].min().date()
    max_date = df_raw["Date"].max().date()
    date_range = st.date_input(
        "Rango de fechas",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    st.markdown("### Categoría")
    all_cats = sorted(df_raw["Category"].dropna().unique())
    sel_cats = st.multiselect("Category", all_cats, default=all_cats)

    st.markdown("### Departamento")
    all_deps = sorted(df_raw["Department"].dropna().unique())
    sel_deps = st.multiselect("Department", all_deps, default=all_deps)

    st.markdown("### Tipo Contable")
    all_acct = sorted(df_raw["Accounting Type"].dropna().unique())
    sel_acct = st.multiselect("Accounting Type", all_acct, default=all_acct)

    st.markdown("### Función de Negocio")
    all_bfn = sorted(df_raw["Business Function"].dropna().unique())
    sel_bfn = st.multiselect("Business Function", all_bfn, default=all_bfn)

    st.markdown("### Facturación")
    all_fac = sorted(df_raw["Facturacion"].dropna().unique())
    sel_fac = st.multiselect("Facturación", all_fac, default=all_fac)

    st.markdown("### Comportamiento del Costo")
    all_cb = sorted(df_raw["Cost Behavior"].dropna().unique())
    sel_cb = st.multiselect("Cost Behavior", all_cb, default=all_cb)

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

# ─── HEADER ─────────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div class="main-header">
        <h1>NOMII<span class="accent-dot"> · </span>Expense Control Dashboard</h1>
        <p>Hoja <b>SALIDAS</b> · {d_start.strftime('%d %b %Y')} → {d_end.strftime('%d %b %Y')} · {len(df):,} transacciones</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ─── KPI CARDS ──────────────────────────────────────────────────────────────
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

cols = st.columns(5)
kpis = [
    ("Gasto Total", f"€{total_spend:,.0f}", mom_str),
    ("Transacciones", f"{n_transactions:,}", ""),
    ("Ticket Promedio", f"€{avg_ticket:,.0f}", ""),
    ("Mediana", f"€{median_spend:,.0f}", ""),
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
        yaxis=dict(gridcolor="#f1f5f9", tickformat="€,.0f"),
        yaxis2=dict(gridcolor="rgba(0,0,0,0)", tickformat="€,.0f"),
        xaxis=dict(tickangle=-45, tickfont=dict(size=10)),
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
            textfont=dict(size=11),
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
# ROW 2: Category Heatmap + Department Spend
# ═══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">🔥 Análisis por Categoría, Departamento & Función</div>', unsafe_allow_html=True)

c3, c4 = st.columns(2)

# ── Heatmap: Category × Month
with c3:
    heatmap_data = (
        df.groupby(["Category", "Year_Month"])["Abs_Amount"]
        .sum()
        .reset_index()
        .pivot(index="Category", columns="Year_Month", values="Abs_Amount")
        .fillna(0)
    )
    heatmap_data = heatmap_data[sorted(heatmap_data.columns)]

    fig_heat = go.Figure(
        go.Heatmap(
            z=heatmap_data.values,
            x=heatmap_data.columns.tolist(),
            y=heatmap_data.index.tolist(),
            colorscale=[[0, "#F9F9F9"], [0.3, "#B3D9EA"], [0.6, "#4D7EA8"], [1, "#003366"]],
            hovertemplate="<b>%{y}</b><br>%{x}<br>€%{z:,.0f}<extra></extra>",
            colorbar=dict(title="EUR", tickformat="€,.0f", len=0.8),
        )
    )
    fig_heat.update_layout(
        **CHART_LAYOUT,
        title=dict(text="Heatmap — Categoría × Mes", font=dict(size=14)),
        height=420,
        xaxis=dict(tickangle=-45, tickfont=dict(size=9)),
        yaxis=dict(tickfont=dict(size=10)),
    )
    st.plotly_chart(fig_heat, use_container_width=True)

# ── Department horizontal bar
with c4:
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
            textfont=dict(size=10),
        )
    )
    fig_dept.update_layout(
        **CHART_LAYOUT,
        title=dict(text="Gasto por Departamento", font=dict(size=14)),
        height=420,
        xaxis=dict(gridcolor="#f1f5f9", tickformat="€,.0f"),
        yaxis=dict(tickfont=dict(size=11)),
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
    color_map_acct = {"OPEX": NOMII["primary"], "CAPEX": NOMII["secondary"], "COR": NOMII["accent"]}
    fig_acct = px.bar(
        acct_monthly,
        x="Year_Month", y="Abs_Amount", color="Accounting Type",
        color_discrete_map=color_map_acct,
        labels={"Abs_Amount": "EUR", "Year_Month": "Mes"},
    )
    fig_acct.update_layout(
        **CHART_LAYOUT,
        title=dict(text="OPEX / CAPEX / COR por Mes", font=dict(size=14)),
        height=380,
        barmode="stack",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10)),
        xaxis=dict(tickangle=-45, tickfont=dict(size=9)),
        yaxis=dict(gridcolor="#f1f5f9", tickformat="€,.0f"),
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
            textfont=dict(size=10),
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
            textfont=dict(size=10),
        )
    )
    fig_tri.update_layout(
        **CHART_LAYOUT,
        title=dict(text="Gasto por Trimestre", font=dict(size=14)),
        height=380,
        xaxis=dict(tickfont=dict(size=11)),
        yaxis=dict(gridcolor="#f1f5f9", tickformat="€,.0f"),
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
    color_map_fac = {"GmbH": NOMII["primary"], "SpA": NOMII["secondary"]}
    fig_fac = px.area(
        fac_monthly,
        x="Year_Month", y="Abs_Amount", color="Facturacion",
        color_discrete_map=color_map_fac,
        labels={"Abs_Amount": "EUR", "Year_Month": "Mes"},
    )
    fig_fac.update_layout(
        **CHART_LAYOUT,
        title=dict(text="Gasto por Entidad de Facturación", font=dict(size=14)),
        height=380,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=11)),
        xaxis=dict(tickangle=-45, tickfont=dict(size=9)),
        yaxis=dict(gridcolor="#f1f5f9", tickformat="€,.0f"),
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
        textfont=dict(size=10, family="JetBrains Mono"),
    )
)
fig_cp.update_layout(
    **{k: v for k, v in CHART_LAYOUT.items() if k != "margin"},
    height=480,
    xaxis=dict(gridcolor="#f1f5f9", tickformat="€,.0f"),
    yaxis=dict(tickfont=dict(size=11)),
    margin=dict(l=180, r=80, t=20, b=40),
)
st.plotly_chart(fig_cp, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════
# ROW 5: Sub-Category Sunburst + Employee Spend + Category Trend
# ═══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">🌐 Desglose Detallado & Responsables</div>', unsafe_allow_html=True)

c10, c11 = st.columns(2)

# ── Sunburst: Category → SubCat1 → SubCat2
with c10:
    sun_data = (
        df.groupby(["Category", "Sub-Category 1", "Sub-Category 2"])["Abs_Amount"]
        .sum()
        .reset_index()
    )
    fig_sun = px.sunburst(
        sun_data,
        path=["Category", "Sub-Category 1", "Sub-Category 2"],
        values="Abs_Amount",
        color="Abs_Amount",
        color_continuous_scale=[NOMII["pale_blue"], NOMII["light_blue"], NOMII["primary"]],
    )
    fig_sun.update_layout(
        **CHART_LAYOUT,
        title=dict(text="Jerarquía: Categoría → Sub-Cat 1 → Sub-Cat 2", font=dict(size=14)),
        height=500,
        coloraxis_showscale=False,
    )
    fig_sun.update_traces(
        hovertemplate="<b>%{label}</b><br>€%{value:,.0f}<extra></extra>",
    )
    st.plotly_chart(fig_sun, use_container_width=True)

# ── Responsible Employee bar
with c11:
    emp_data = (
        df.groupby("Responsible Employee")["Abs_Amount"]
        .sum()
        .nlargest(12)
        .sort_values()
        .reset_index()
    )
    fig_emp = go.Figure(
        go.Bar(
            y=emp_data["Responsible Employee"],
            x=emp_data["Abs_Amount"],
            orientation="h",
            marker=dict(color=PALETTE[:len(emp_data)], cornerradius=4),
            hovertemplate="<b>%{y}</b><br>€%{x:,.0f}<extra></extra>",
            text=[f"€{v:,.0f}" for v in emp_data["Abs_Amount"]],
            textposition="outside",
            textfont=dict(size=10),
        )
    )
    fig_emp.update_layout(
        **{k: v for k, v in CHART_LAYOUT.items() if k != "margin"},
        title=dict(text="Top 12 Responsables por Gasto", font=dict(size=14)),
        height=500,
        xaxis=dict(gridcolor="#f1f5f9", tickformat="€,.0f"),
        yaxis=dict(tickfont=dict(size=11)),
        margin=dict(l=160, r=80, t=40, b=40),
    )
    st.plotly_chart(fig_emp, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════
# ROW 6: Category monthly stacked area + Account usage
# ═══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">📊 Evolución por Categoría & Medios de Pago</div>', unsafe_allow_html=True)

c12, c13 = st.columns([3, 2])

with c12:
    cat_monthly = (
        df.groupby(["Year_Month", "Category"])["Abs_Amount"]
        .sum()
        .reset_index()
        .sort_values("Year_Month")
    )
    fig_cat_area = px.area(
        cat_monthly,
        x="Year_Month", y="Abs_Amount", color="Category",
        color_discrete_sequence=PALETTE,
        labels={"Abs_Amount": "EUR", "Year_Month": "Mes"},
    )
    fig_cat_area.update_layout(
        **CHART_LAYOUT,
        title=dict(text="Evolución Mensual por Categoría (Stacked Area)", font=dict(size=14)),
        height=420,
        legend=dict(font=dict(size=9), y=0.5),
        xaxis=dict(tickangle=-45, tickfont=dict(size=9)),
        yaxis=dict(gridcolor="#f1f5f9", tickformat="€,.0f"),
    )
    fig_cat_area.update_traces(hovertemplate="<b>%{fullData.name}</b><br>%{x}<br>€%{y:,.0f}<extra></extra>")
    st.plotly_chart(fig_cat_area, use_container_width=True)

with c13:
    acct_data = (
        df.groupby("Account")["Abs_Amount"]
        .sum()
        .nlargest(10)
        .sort_values()
        .reset_index()
    )
    fig_acct2 = go.Figure(
        go.Bar(
            y=acct_data["Account"],
            x=acct_data["Abs_Amount"],
            orientation="h",
            marker=dict(color=PALETTE[:len(acct_data)], cornerradius=4),
            hovertemplate="<b>%{y}</b><br>€%{x:,.0f}<extra></extra>",
            text=[f"€{v:,.0f}" for v in acct_data["Abs_Amount"]],
            textposition="outside",
            textfont=dict(size=9),
        )
    )
    fig_acct2.update_layout(
        **{k: v for k, v in CHART_LAYOUT.items() if k != "margin"},
        title=dict(text="Top 10 Cuentas / Medios de Pago", font=dict(size=14)),
        height=420,
        xaxis=dict(gridcolor="#f1f5f9", tickformat="€,.0f"),
        yaxis=dict(tickfont=dict(size=9)),
        margin=dict(l=180, r=80, t=40, b=40),
    )
    st.plotly_chart(fig_acct2, use_container_width=True)

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
df_display["Date"] = df_display["Date"].dt.strftime("%Y-%m-%d")
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

# ─── FOOTER ─────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<p style="text-align:center; color:#94a3b8; font-size:0.78rem;">'
    'NOMII Finance Dashboard · Datos actualizados desde Excel/SharePoint · '
    f'Generado el {datetime.now().strftime("%d %b %Y %H:%M")}</p>',
    unsafe_allow_html=True,
)
