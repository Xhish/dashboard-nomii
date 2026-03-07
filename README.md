# NOMII · Finance Dashboard — Hoja SALIDAS

Dashboard profesional de control de gastos construido con **Streamlit + Plotly**.

---

## 🚀 Ejecución rápida

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Colocar el Excel en la misma carpeta que dashboard.py
#    (El archivo debe llamarse: Maestro_Pagos_NOMII_07-03-2026.xlsx)

# 3. Ejecutar
streamlit run dashboard.py
```

El dashboard se abrirá en `http://localhost:8501`.

---

## 📊 Contenido del Dashboard

| Sección | Gráficos |
|---------|----------|
| **KPIs** | Gasto total, transacciones, ticket promedio, mediana, proveedores únicos, MoM% |
| **Tendencia** | Barras mensuales + línea acumulada |
| **Categoría** | Donut de distribución, heatmap categoría×mes, sunburst jerárquico |
| **Departamento** | Barras horizontales por departamento |
| **Contabilidad** | OPEX/CAPEX/COR stacked, comportamiento del costo (fijo/variable/único) |
| **Negocio** | Treemap de funciones de negocio |
| **Trimestres** | Barras por trimestre, área stacked por entidad de facturación (GmbH/SpA) |
| **Proveedores** | Top 15 counterparties |
| **Responsables** | Top 12 employees por gasto |
| **Medios de pago** | Top 10 cuentas |
| **Detalle** | Tabla interactiva con todas las transacciones |

### Filtros disponibles (sidebar)
- Rango de fechas
- Categoría
- Departamento
- Tipo contable (OPEX/CAPEX/COR)
- Función de negocio
- Entidad de facturación
- Comportamiento del costo

---

## 🔗 Integración con SharePoint (datos en tiempo real)

Para conectar directamente al Excel en SharePoint y tener datos actualizados,
reemplaza la función `load_data()` en `dashboard.py` con una de estas opciones:

### Opción A — Office365-REST-Python-Client (recomendada)

```bash
pip install Office365-REST-Python-Client
```

```python
from office365.runtime.auth.client_credential import ClientCredential
from office365.sharepoint.client_context import ClientContext
import io

@st.cache_data(ttl=300)  # cache 5 minutos
def load_data():
    site_url   = "https://tu-empresa.sharepoint.com/sites/TuSitio"
    client_id  = st.secrets["sp_client_id"]
    client_sec = st.secrets["sp_client_secret"]
    file_url   = "/sites/TuSitio/Shared Documents/Maestro_Pagos_NOMII_07-03-2026.xlsx"

    ctx = ClientContext(site_url).with_credentials(
        ClientCredential(client_id, client_sec)
    )
    response = File.open_binary(ctx, file_url)
    
    df = pd.read_excel(
        io.BytesIO(response.content),
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
```

Crea `.streamlit/secrets.toml`:
```toml
sp_client_id = "tu-app-id"
sp_client_secret = "tu-app-secret"
```

### Opción B — Microsoft Graph API

```bash
pip install msal requests
```

```python
import msal, requests, io

@st.cache_data(ttl=300)
def load_data():
    app = msal.ConfidentialClientApplication(
        st.secrets["graph_client_id"],
        authority=f"https://login.microsoftonline.com/{st.secrets['graph_tenant_id']}",
        client_credential=st.secrets["graph_client_secret"],
    )
    token = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
    
    # Obtener el contenido del archivo
    headers = {"Authorization": f"Bearer {token['access_token']}"}
    drive_url = (
        f"https://graph.microsoft.com/v1.0/sites/{st.secrets['site_id']}"
        f"/drive/root:/Maestro_Pagos_NOMII_07-03-2026.xlsx:/content"
    )
    resp = requests.get(drive_url, headers=headers)
    
    df = pd.read_excel(io.BytesIO(resp.content), sheet_name="SALIDAS", engine="openpyxl")
    df["Date"] = pd.to_datetime(df["Date"])
    df["Abs_Amount"] = df["Amount in EUR"].abs()
    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.month
    df["Month_Name"] = df["Date"].dt.strftime("%b %Y")
    df["Year_Month"] = df["Date"].dt.to_period("M").astype(str)
    return df
```

---

## 🌐 Deploy en Streamlit Cloud

1. Sube el repo a GitHub (sin el Excel si usas SharePoint)
2. Ve a [share.streamlit.io](https://share.streamlit.io)
3. Conecta tu repo → Configura secrets en la UI
4. ¡Listo! Dashboard online y actualizado automáticamente
