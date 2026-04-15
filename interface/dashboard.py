import sys
import os
import pandas as pd
import streamlit as st

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="Nahuacho Dashboard - Música y Datos",
    page_icon="🎹",
    layout="wide"
)

# Añadir carpeta raíz al path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.notion_api import get_notion_data
from core.processor import apply_prioritization_engine
from core.history_tracker import save_snapshot

# 2. CACHÉ Y CARGA DE DATOS
@st.cache_data(ttl=600)
def load_data_cached():
    df = get_notion_data()
    save_snapshot(df)
    return df

df = load_data_cached()

# 3. ESTILO VISUAL (CSS)
st.markdown("""
    <style>
    /* Estilo para las métricas */
    [data-testid="stMetricValue"] { font-size: 28px; color: #00FFAA; }
    [data-testid="stMetric"] { 
        background-color: #161b22; 
        padding: 15px; 
        border-radius: 10px; 
        border: 1px solid #30363d; 
    }
    /* Estilo para los botones de abrir carpeta */
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        background-color: #238636;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# 4. ENCABEZADO PRO
st.title("DASHBOARD")
st.markdown("*Desde los Estudios Santa María de la Nahuacho House*")
st.markdown("---")

# KPIs con nuevo diseño
k1, k2, k3, k4 = st.columns(4)
k1.metric("Catálogo Total", len(df), delta=f"{len(df)} temas")
k2.metric("Rating Promedio", f"{round(df['Rating_Num'].mean(), 1)} ⭐")
k3.metric("En proceso", len(df[df["Status"].isin(["Producción", "Grabación", "Mezcla"])]))
k4.metric("Status API", "Conectado", delta="Online")

# 5. PESTAÑAS
tab1, tab2, tab3, tab4 = st.tabs(["🔥 PRIORIDADES", "📦 INVENTARIO", "📊 ANALÍTICA", "📚 HISTORIAL"])

with tab1:
    st.header("🎯 Selección Élite: EP 'Depre'")
    st.info("Algoritmo de Prioridad: Enfocado en cerrar ciclos y lanzar material.")
    
    # Motor de prioridad
    depre_elite = apply_prioritization_engine(df, target_album="Depre")
    
    if not depre_elite.empty:
        top_10 = depre_elite.head(10)
        
        for index, row in top_10.iterrows():
            with st.container():
                # Columnas con tu estructura original
                col_a, col_b, col_c = st.columns([3, 1, 1])
                
                with col_a:
                    # Usamos HTML para darle el color neón al título
                    st.markdown(f"### <span style='color:#00FFAA;'>{row['Nombre']}</span>", unsafe_allow_html=True)
                    st.markdown(f"**Status:** `{row['Status']}` | **Calidad:** {'⭐' * int(row['Rating_Num'])}")
                    st.caption(f"Proyecto: {row['ProjectName']}")
                
                with col_b:
                    # El Metric resalta el score de prioridad
                    st.metric("Priority Score", round(row['Final_Priority'], 1))
                
                with col_c:
                    st.write("") # Espaciador para alinear el botón
                    st.write("") 
                    if row['Path']:
                        # Botón con la lógica de apertura de carpeta
                        st.button("📂 Abrir Carpeta", key=f"btn_{index}", 
                                  on_click=lambda p=row['Path']: os.startfile(p) if os.path.exists(p) else st.error("Ruta no válida"))
                
                st.divider()
    else:
        st.warning("No hay canciones con Rating >= 3 etiquetadas en el álbum 'Depre'.")

with tab2:
    st.header("📦 El Baúl de las 800 Ideas")
    busqueda = st.text_input("🔍 Filtro rápido (Nombre, Proyecto o Álbum):", placeholder="Escribe para buscar...")
    
    # Aplicando el fix del Warning: width="stretch"
    if busqueda:
        res = df[df['Nombre'].str.contains(busqueda, case=False, na=False)]
        st.dataframe(res, width="stretch") # FIX DEL WARNING
    else:
        st.dataframe(df.head(100), width="stretch") # FIX DEL WARNING
        st.caption("Mostrando los últimos 100 movimientos.")

with tab3:
    st.header("📊 Ciencia de Datos aplicada al Arte")
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Fuerza por Género")
        gen_counts = df.explode("Genero")["Genero"].value_counts()
        st.bar_chart(gen_counts)
    with col_b:
        st.subheader("Estado de las Ideas")
        st.bar_chart(df["Status"].value_counts())
with tab4:
    st.header("📈 Seguimiento de Progreso")
    
    if os.path.exists("data/progreso_history.csv"):
        history_df = pd.read_csv("data/progreso_history.csv")
        
        # 1. Resumen de actividad
        dias_registrados = history_df["Fecha_Snapshot"].nunique()
        st.info(f"Sistema de monitoreo activo. Datos acumulados de {dias_registrados} día(s).")
        
        col_h1, col_h2 = st.columns(2)
        
        with col_h1:
            st.subheader("Evolución de Status")
            # Mostramos cuántas canciones hay en cada estado a lo largo del tiempo
            progreso_temporal = history_df.groupby(["Fecha_Snapshot", "Status"]).size().unstack(fill_value=0)
            st.line_chart(progreso_temporal)
            
        with col_h2:
            st.subheader("Crecimiento del Catálogo")
            # Conteo total de canciones por fecha
            conteo_total = history_df.groupby("Fecha_Snapshot").size()
            st.area_chart(conteo_total)

        # 2. Detector de estancamiento (Lógica simple)
        st.subheader("⚠️ Alerta de Estancamiento")
        # Si una canción aparece en el mismo status en la fecha más vieja y la más nueva
        fechas = sorted(history_df["Fecha_Snapshot"].unique())
        if len(fechas) > 1:
            inicio = history_df[history_df["Fecha_Snapshot"] == fechas[0]]
            actual = history_df[history_df["Fecha_Snapshot"] == fechas[-1]]
            
            # Unimos para comparar
            comparativa = pd.merge(inicio, actual, on="Nombre", suffixes=('_old', '_new'))
            estancadas = comparativa[comparativa["Status_old"] == comparativa["Status_new"]]
            
            if not estancadas.empty:
                st.warning(f"Tienes {len(estancadas)} canciones que no han cambiado de estado desde que iniciaste el tracking.")
                st.dataframe(estancadas[["Nombre", "Status_new"]].head(10), width="stretch")
        else:
            st.write("Se necesitan al menos 2 días de datos para comparar el progreso.")
            
    else:
        st.warning("Aún no hay un archivo de historial. El sistema creará uno automáticamente al cargar el Dashboard.")
        
# Footer
st.markdown("---")
if st.button("🔄 Sincronizar con Notion"):
    st.cache_data.clear()
    st.rerun()