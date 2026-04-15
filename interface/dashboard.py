import sys
import os

# Esto añade la carpeta raíz al camino de búsqueda de Python
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from core.notion_api import get_notion_data
from core.processor import apply_prioritization_engine

st.set_page_config(page_title="Musics Dashboard", layout="wide")
st.title("🎵 Inventario (Data Analysis)")

# Cargar datos
df = get_notion_data()

# KPIs Rápidos
col1, col2, col3 = st.columns(3)
col1.metric("Total Canciones", len(df))
col2.metric("Promedio Rating", round(df["Rating_Num"].mean(), 2))
col3.metric("En Producción", len(df[df["Status"] == "Producción"]))

# Gráfico de barras por Género (Ciencia de Datos básica)
st.subheader("Distribución por Género")
# Explotamos la lista de géneros para contar individualmente
generos_df = df.explode("Genero")
st.bar_chart(generos_df["Genero"].value_counts())

st.subheader("Inventario Completo")
st.dataframe(df)

st.divider()
# En la sección del EP del dashboard
st.header("🎯 Foco Estratégico: Proyecto 'Depre'")
st.write("Estas son las canciones con las que vas a debutar profesionalmente. Olvida el resto hasta terminar estas.")

# Aplicar el motor
depre_elite = apply_prioritization_engine(df)

if not depre_elite.empty:
    # Mostrar las Top 15
    top_15 = depre_elite.head(15)
    
    for index, row in top_15.iterrows():
        with st.container():
            col_a, col_b, col_c = st.columns([3, 1, 1])
            with col_a:
                st.subheader(f"{index+1}. {row['Nombre']}")
                st.caption(f"Status: {row['Status']} | Rating: {'⭐' * int(row['Rating_Num'])}")
            with col_b:
                st.metric("Priority Score", round(row['Final_Priority'], 1))
            with col_c:
                if row['Path']:
                    st.button("📂 Abrir Carpeta", key=f"btn_{index}", on_click=lambda p=row['Path']: os.startfile(p) if os.path.exists(p) else None)

    st.success(f"Tienes {len(depre_elite)} canciones candidatas para este proyecto. Concéntrate en las 5 de arriba.")
else:
    st.warning("No se encontraron canciones con el mood 'Depre' y Rating >= 3. ¿Quizás falta etiquetarlas en Notion?")