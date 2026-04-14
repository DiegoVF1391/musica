import sys
import os

# Esto añade la carpeta raíz al camino de búsqueda de Python
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from core.notion_api import get_notion_data

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