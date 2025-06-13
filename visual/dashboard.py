import tkinter as tk
from tkinter import ttk
from visual.statistics import GeneralStatisticsTab

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from sim.init_simulation import generate_connected_graph
from sim.simulation import bfs_shortest_path
from visual.network_adapter import graph_to_networkx, get_spring_params, avl_to_nx_graph
from visual.avl_visualizer import render_avl_tree, collect_routes, hierarchy_pos
from tda.avl import insert, Node
from domain.client import Client
from domain.order import Order

import networkx as nx
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Run Simulation",
    "Explore Network",
    "Clients & Orders",
    "Route Analytics",
    "General Statistics"
])

# --- TAB 1: Sliders y botón ---
with tab1:
    st.markdown(
        """
        <h1 style="display: flex; align-items: center; gap: 10px;">
            <span>🚁</span> Drone Logistics Simulator - Correos Chile
        </h1>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("**Node Role Proportions:**")
    st.markdown("""
    <ul>
        <li> <span style='color: orange;'>🟧 Storage Nodes: 20%</span> </li>
        <li> <span style='color: #43b581;'>🟩 Recharge Nodes: 20%</span> </li>
        <li> <span style='color: #CCCCCC;'>🟩 Client Nodes: 60%</span> </li>
    </ul>
    """, unsafe_allow_html=True)

    st.markdown("## ⚙️ Initialize Simulation")
    n_nodes = st.slider("Number of Nodes", min_value=10, max_value=150, value=15)
    m_edges = st.slider("Number of Edges", min_value=10, max_value=300, value=20)
    n_orders = st.slider("Number of Orders", min_value=1, max_value=500, value=10)
    autonomy = 50  # Puedes hacerlo slider también si quieres

    n_clients = int(n_nodes * 0.6)
    st.caption(f"Derived Client Nodes: {n_clients} (60% of {n_nodes})")

    if st.button("🟩 Start Simulation"):
        graph, vertices = generate_connected_graph(n_nodes, m_edges)
        # Assign roles
        role_distribution = [("storage", 0.2), ("recharge", 0.2), ("client", 0.6)]
        roles = []
        for role, perc in role_distribution:
            roles += [role] * int(n_nodes * perc)
        while len(roles) < n_nodes:
            roles.append("client")
        random.shuffle(roles)
        node_roles = {v: roles[i] for i, v in enumerate(vertices)}

        # Prepare clients (nuevos atributos completos)
        client_nodes = [v for v, r in node_roles.items() if r == "client"]
        recharge_nodes = [v for v, r in node_roles.items() if r == "recharge"]
        storage_nodes = [v for v, r in node_roles.items() if r == "storage"]

        clients = [
            Client(
                client_id=f"C{str(i).zfill(3)}",
                name=f"Client{i}",
                type_="premium" if i % 2 == 0 else "normal",
                total_orders=0,
                node=v
            )
            for i, v in enumerate(client_nodes)
        ]

        # Prepare orders
        orders = []
        for i in range(n_orders):
            src = random.choice(storage_nodes)
            tgt = random.choice(client_nodes)
            client_obj = next((c for c in clients if c.node == tgt), None)
            client_id = client_obj.client_id if client_obj else None
            now = datetime.datetime.now().isoformat()
            orders.append(Order(
                order_id=f"O{str(i).zfill(3)}",
                client=client_obj.name if client_obj else None,
                client_id=client_id,
                origin=str(src),
                destination=str(tgt),
                status="pending",
                priority=random.randint(0, 1),
                created_at=now,
                delivered_at=None,
                route_cost=None
            ))
            if client_obj:
                client_obj.total_orders += 1

        # Guarda todo en session_state
        if 'route_frequencies' not in st.session_state:
            st.session_state['route_frequencies'] = {}

        st.session_state['n_nodes'] = n_nodes
        st.session_state['m_edges'] = m_edges
        st.session_state['n_orders'] = n_orders
        st.session_state['autonomy'] = autonomy
        st.session_state['graph'] = graph
        st.session_state['vertices'] = vertices
        st.session_state['node_roles'] = node_roles
        st.session_state['recharge_nodes'] = recharge_nodes
        st.session_state['storage_nodes'] = storage_nodes
        st.session_state['clients'] = clients
        st.session_state['orders'] = orders
        st.session_state['avl_root'] = None
        st.session_state['simulation_ready'] = True
        st.session_state['last_route_path'] = None

with tab2:
    st.markdown("<h2>🌍 Network Visualization</h2>", unsafe_allow_html=True)
    st.markdown("#### Drone Delivery Network")

    if st.session_state.get('simulation_ready'):
        # CREA LAS COLUMNAS: Izquierda para el grafo, derecha para la UI de ruta
        col_grafo, col_ruta = st.columns([3, 1], gap="large")

        # --- COLUMNA IZQUIERDA: Grafo ---
        with col_grafo:
            G = graph_to_networkx(st.session_state['graph'], st.session_state['node_roles'])
            n_nodes = st.session_state['n_nodes']
            spring_params = get_spring_params(n_nodes)
            pos = nx.spring_layout(
                G,
                k=spring_params["k"],
                iterations=spring_params["iterations"],
                scale=spring_params["scale"],
                seed=42
            )
            role_colors = {"storage": "orange", "recharge": "blue", "client": "green"}
            color_map = [role_colors[G.nodes[n]['role']] for n in G.nodes]
            fig, ax = plt.subplots(figsize=(8, 7))
            nx.draw(G, pos, ax=ax, node_color=color_map, with_labels=True)
            labels = nx.get_edge_attributes(G, "weight")
            nx.draw_networkx_edge_labels(G, pos, edge_labels=labels, ax=ax, font_size=9)
            # --- Dibuja la ruta si existe ---
            route_path = st.session_state.get('last_route_path')
            if route_path and len(route_path) > 1:
                path_edges = list(zip(route_path, route_path[1:]))
                path_edges_str = [(str(u), str(v)) for u, v in path_edges]
                nx.draw_networkx_edges(
                    G,
                    pos,
                    edgelist=path_edges_str,
                    ax=ax,
                    edge_color="red",
                    width=3
                )
            st.pyplot(fig)

        # --- COLUMNA DERECHA: Panel de cálculo de ruta ---
        with col_ruta:
            st.markdown("### 📌 Calculate Route")
            options = list(st.session_state['graph'].vertices())
            node_roles = st.session_state['node_roles']
            start = st.selectbox("Origin Node", options, format_func=lambda v: f"{v} ({node_roles.get(v, '-')})", key="route_start")
            end = st.selectbox("Destination Node", options, format_func=lambda v: f"{v} ({node_roles.get(v, '-')})", key="route_end")
            if st.button("🧭 Calculate Route"):
                route = bfs_shortest_path(
                    st.session_state['graph'],
                    start,
                    end,
                    st.session_state['autonomy'],
                    st.session_state['recharge_nodes']
                )
                if route:
                    st.session_state['last_route_path'] = route.path
                    st.success(f"Route found: {route.path} (Cost: {route.cost})")

                    # ---------- Guarda ruta en AVL y actualiza frecuencias ----------
                    route_key = " → ".join(str(v) for v in route.path)
                    # Inicializa el dict de frecuencias si no existe
                    if 'route_frequencies' not in st.session_state:
                        st.session_state['route_frequencies'] = {}
                    st.session_state['avl_root'] = insert(st.session_state.get('avl_root'), route_key)
                    freqs = st.session_state['route_frequencies']
                    freqs[route_key] = freqs.get(route_key, 0) + 1

                else:
                    st.session_state['last_route_path'] = None
                    st.error("No route found within drone autonomy and recharge constraints.")

with tab3:
    st.write("### Clients")
    if 'clients' in st.session_state:
        clients_list = [c.to_dict() for c in st.session_state['clients']]
        st.json(clients_list, expanded=False)

    st.write("### Orders")
    if 'orders' in st.session_state:
        orders_list = [o.to_dict() for o in st.session_state['orders']]
        st.json(orders_list, expanded=False)

with tab4:
    st.markdown("### Most Frequent Routes")

    avl_root = st.session_state.get('avl_root')
    freqs = st.session_state.get('route_frequencies', {})
    if avl_root:
        routes = collect_routes(avl_root, freqs, [])

        # Ordena por frecuencia descendente y muestra solo los top N (ejemplo: 10)
        routes = sorted(routes, key=lambda x: -x[1])
        for idx, (path, freq) in enumerate(routes[:10], 1):
            st.markdown(
                f"**{idx}.** Route hash: <span style='color:deepskyblue'>{path}</span> | "
                f"<span style='color:orange'>Frequency: {freq}</span>",
                unsafe_allow_html=True
            )
    else:
        st.info("No routes registered yet.")

    st.markdown("### 🟩 AVL Tree Visualization")
    avl_root = st.session_state.get('avl_root')
    freqs = st.session_state.get('route_frequencies', {})
    if avl_root:
        # Crea grafo
        G = avl_to_nx_graph(avl_root, freqs)
        # Usa layout jerárquico
        pos = hierarchy_pos(G)
        fig, ax = plt.subplots(figsize=(10, 4))
        nx.draw(G, pos, with_labels=True, arrows=True,
                node_size=1800, node_color="#a7d2ec", font_size=10, font_weight="bold", ax=ax)
        st.pyplot(fig)
    else:
        st.info("AVL Tree not available yet.")


with tab5:
    st.write("### General Statistics")
    st.info("Here you can show bar charts and pie charts with visit counts and role proportions.")
