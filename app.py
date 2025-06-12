import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import random
import string

def generate_node_labels(n):
    labels = []
    i = 0
    while len(labels) < n:
        label = ''
        x = i
        while True:
            x, rem = divmod(x, 26)
            label = chr(65 + rem) + label
            if x == 0:
                break
            x -= 1
        labels.append(label)
        i += 1
    return labels

def generate_random_tree(n, seed=None):
    random.seed(seed)
    G = nx.Graph()
    G.add_nodes_from(range(n))
    nodes = list(G.nodes())
    connected = [nodes.pop(0)]
    while nodes:
        node = nodes.pop(0)
        target = random.choice(connected)
        G.add_edge(node, target)
        connected.append(node)
    return G

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
    st.header("👁 Visualizar red:")
    if 'graph_data' not in st.session_state or st.session_state['last_n'] != n_nodes or st.session_state['last_e'] != n_edges:
        G = generate_random_tree(n_nodes, seed=42)
        
        extra_edges_needed = n_edges - (n_nodes - 1)

        possible_edges = list(nx.non_edges(G))
        random.shuffle(possible_edges)
        for i in range(min(extra_edges_needed, len(possible_edges))):
            u, v = possible_edges[i]
            G.add_edge(u, v)

        labels = generate_node_labels(n_nodes)
        mapping = {node: labels[i] for i, node in enumerate(G.nodes())}
        G = nx.relabel_nodes(G, mapping)

        positions = nx.spring_layout(G, seed=42)
        nx.set_node_attributes(G, positions, 'pos')

        for (u, v) in G.edges():
            G.edges[u, v]['weight'] = random.randint(1, 20)

        nodes_list = list(G.nodes())
        random.seed(42)
        random.shuffle(nodes_list)
        n_storage = int(0.2 * n_nodes)
        n_recharge = int(0.2 * n_nodes)
        n_client = n_nodes - n_storage - n_recharge

        roles = {}
        for i, node in enumerate(nodes_list):
            if i < n_storage:
                roles[node] = 'storage'
            elif i < n_storage + n_recharge:
                roles[node] = 'recharge'
            else:
                roles[node] = 'client'
        nx.set_node_attributes(G, roles, 'role')

        st.session_state['graph_data'] = G
        st.session_state['last_n'] = n_nodes
        st.session_state['last_e'] = n_edges

    G = st.session_state['graph_data']
    positions = nx.get_node_attributes(G, 'pos')
    roles = nx.get_node_attributes(G, 'role')

    col1, col2 = st.columns([3, 1])

    with col2:
        st.header("Ruta más corta")
        origin = st.selectbox("Nodo origen", list(G.nodes()))
        destination = st.selectbox("Nodo destino", list(G.nodes()))
        calcular = st.button("Calcular ruta")

    path_nodes = []
    path_edges = []
    path_cost = 0

    if calcular:
        try:
            path_nodes = nx.shortest_path(G, source=origin, target=destination, weight='weight')
            path_edges = list(zip(path_nodes[:-1], path_nodes[1:]))
            path_cost = nx.shortest_path_length(G, source=origin, target=destination, weight='weight')
            st.success(f"Ruta: {' -> '.join(path_nodes)}, costo: {path_cost}")
        except nx.NetworkXNoPath:
            st.error("No existe una ruta entre los nodos seleccionados.")

    with col1:
        plt.figure(figsize=(10, 8))

        color_map = {
            'client': 'green',
            'storage': 'red',
            'recharge': 'blue'
        }
        node_colors = [color_map[roles.get(node, 'client')] for node in G.nodes()]
        edge_colors = ['red' if (u, v) in path_edges or (v, u) in path_edges else 'black' for u, v in G.edges()]
        labels = nx.get_edge_attributes(G, 'weight')

        nx.draw_networkx_nodes(G, pos=positions, node_color=node_colors, node_size=800)
        nx.draw_networkx_edges(G, pos=positions, edge_color=edge_colors, width=2)
        nx.draw_networkx_labels(G, pos=positions, font_size=10, font_weight='bold')
        nx.draw_networkx_edge_labels(G, pos=positions, edge_labels=labels, font_size=8)
        plt.axis('off')
        st.pyplot(plt)
with tab3:
    st.header("🌐 Clientes y ordenes:")

with tab4:
    st.header("🚍 Rutas de frecuencia e historial:")

with tab5:
    st.header("✅ Estadísticas generales:")