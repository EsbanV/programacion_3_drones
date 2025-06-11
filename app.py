import streamlit as st

st.set_page_config(page_title="Proyecto: SLAD", page_icon="🛸", layout="wide")
st.title("Proyecto: Sistema logístico autónomo con drones")
st.subheader("Proporciones de los roles de los nodos")
st.text("·  📦 Nodos de almacenamiento: 20%\n·  🔋 Nodos de recarga: 20%\n·  👤 Nodos de clientes: 60%")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "♿ Iniciar simulación", 
    "🔍 Explorar red", 
    "🌐 Clientes y ordenes", 
    "🚍 Análisis de ruta", 
    "✅ Estadísticas"
])

with tab1:
    st.header("⚙ Configuración de la simulación:")

with tab2:
    st.header("👁 Visualizar red:")

with tab3:
    st.header("🌐 Clientes y ordenes:")

with tab4:
    st.header("🚍 Rutas de frecuencia e historial:")

with tab5:
    st.header("✅ Estadísticas generales:")