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

     # Sliders para parametros
    st.subheader("Number of Nodes")
    n_nodes = st.slider("", min_value=10, max_value=150, value=15, key="nodes_slider")
    
    st.subheader("Number of Edges") 
    n_edges = st.slider("", min_value=10, max_value=300, value=20, key="edges_slider")
    
    st.subheader("Number of Orders")
    n_orders = st.slider("", min_value=1, max_value=500, value=1, key="orders_slider")
    
    # Calculos de nodos por rol
    storage_nodes = int(n_nodes * 0.20)  
    recharge_nodes = int(n_nodes * 0.20)   
    client_nodes = n_nodes - storage_nodes - recharge_nodes  
    
    # Campo informativo
    st.subheader("Derived Client Nodes:")
    st.text(f"{client_nodes} ({int((client_nodes/n_nodes)*100)}% of {n_nodes})")
    
    # Información adicional de nodos
    st.info(f"""
    **Distribución de nodos:**
    - 📦 Nodos de almacenamiento: {storage_nodes} ({int((storage_nodes/n_nodes)*100)}%)
    - 🔋 Nodos de recarga: {recharge_nodes} ({int((recharge_nodes/n_nodes)*100)}%)  
    - 👤 Nodos de clientes: {client_nodes} ({int((client_nodes/n_nodes)*100)}%)
    """)
    
    # Validaciones
    valid_simulation = True
    validation_messages = []
    
    # Validar que hay suficientes aristas para conectividad
    min_edges_for_connectivity = n_nodes - 1
    if n_edges < min_edges_for_connectivity:
        valid_simulation = False
        validation_messages.append(f"⚠️ Se necesitan al menos {min_edges_for_connectivity} aristas para garantizar conectividad")
    
    # Validar que hay nodos de cada tipo
    if storage_nodes < 1:
        valid_simulation = False
        validation_messages.append("⚠️ Se necesita al menos 1 nodo de almacenamiento")
        
    if recharge_nodes < 1:
        valid_simulation = False
        validation_messages.append("⚠️ Se necesita al menos 1 nodo de recarga")
        
    if client_nodes < 1:
        valid_simulation = False
        validation_messages.append("⚠️ Se necesita al menos 1 nodo cliente")
    
    # Mostrar mensajes de validación
    if validation_messages:
        for msg in validation_messages:
            st.warning(msg)
    
    # Botón de inicio de simulación
    st.button("🏁 Start Simulation", disabled=not valid_simulation)

with tab2:
    st.header("👁 Visualizar red:")

with tab3:
    st.header("🌐 Clientes y ordenes:")

with tab4:
    st.header("🚍 Rutas de frecuencia e historial:")

with tab5:
    st.header("✅ Estadísticas generales:")