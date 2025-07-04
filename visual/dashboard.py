import sys
import os
import random
import datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from sim.init_simulation import InitSimulation
from sim.simulation import Simulation
from visual.network_adapter import NetworkAdapter
from visual.avl_visualizer import AVL_visualizer
from tda.avl import AVL
from tda.hash_map import Map
from domain.client import Client
from domain.order import Order

import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import plotly.graph_objects as go
import folium
from visual.report_generator import ReportGenerator
from visual.map.map_adapter import MapAdapter
from streamlit_folium import st_folium
from sim.kruskal import kruskal_mst  # Asegúrate de tenerlo implementado como antes
from api.main import sync_state_from_streamlit 

st.set_page_config(layout="wide")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Run Simulation",
    "Explore Network",
    "Clients & Orders",
    "Route Analytics",
    "General Statistics"
])

# ------------------ TAB 1: Configuración y generación de simulación ------------------
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
    n_orders = st.slider("Number of Orders", min_value=1, max_value=300, value=10)
    autonomy = 50

    n_clients = int(n_nodes * 0.6)
    st.caption(f"Derived Client Nodes: {n_clients} (60% of {n_nodes})")

    if st.button("🟩 Start Simulation"):
        graph, vertices = InitSimulation.generate_connected_graph(n_nodes, m_edges)
        role_distribution = [("storage", 0.2), ("recharge", 0.2), ("client", 0.6)]
        roles = []
        for role, perc in role_distribution:
            roles += [role] * int(n_nodes * perc)
        while len(roles) < n_nodes:
            roles.append("client")
        random.shuffle(roles)
        node_roles = {v: roles[i] for i, v in enumerate(vertices)}

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

        orders = []
        for i in range(n_orders):
            src = random.choice(storage_nodes)
            tgt = random.choice(client_nodes)
            client_obj = next((c for c in clients if c.node == tgt), None)
            client_id = client_obj.client_id if client_obj else None
            now = datetime.datetime.now().isoformat()

            # Calcula la ruta y el costo aquí:
            route_result = Simulation.bfs_shortest_path(graph, src, tgt, autonomy, recharge_nodes)
            if route_result and hasattr(route_result, "cost"):
                route_cost = route_result.cost
            else:
                route_cost = None

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
                route_cost=route_cost
            ))
            if client_obj:
                client_obj.total_orders += 1

        st.session_state['n_nodes'] = n_nodes
        st.session_state['m_edges'] = m_edges
        st.session_state['n_orders'] = n_orders
        st.session_state['autonomy'] = autonomy
        st.session_state['graph'] = graph
        st.session_state['vertices'] = vertices
        st.session_state['node_roles'] = node_roles
        st.session_state['recharge_nodes'] = recharge_nodes
        st.session_state['storage_nodes'] = storage_nodes
        st.session_state['node_visits'] = Map()  
        st.session_state['clients'] = clients
        st.session_state['orders'] = orders
        st.session_state['routes_avl'] = AVL()
        st.session_state['simulation_ready'] = True
        st.session_state['last_route_path'] = None
        sync_state_from_streamlit()

# ------------------ TAB 2: Visualización del grafo y cálculo de rutas ------------------
with tab2:
    st.markdown("<h2>🌍 Network Visualization</h2>", unsafe_allow_html=True)
    st.markdown("#### Drone Delivery Network")

    if 'mst_visible' not in st.session_state:
        st.session_state['mst_visible'] = False

    if st.session_state.get('simulation_ready'):
        col_grafo, col_ruta = st.columns([3, 1], gap="large")

        with col_grafo:
            # --- NUEVO: Mapa interactivo con folium ---
            G = NetworkAdapter.graph_to_networkx(
                st.session_state['graph'], st.session_state['node_roles']
            )
            mst_edges = st.session_state.get('mst_edges', None)

            fmap = MapAdapter.network_to_folium(
                G,
                st.session_state['node_roles'],
                route_path=st.session_state.get('last_route_path', None),
                mst_edges=st.session_state.get('mst_edges', None),
                graph=st.session_state['graph']   # <--- TU grafo de clases propias
            )
            st_folium(fmap, width=700, height=500)
            # --- Fin NUEVO ---

        with col_ruta:
            st.markdown("### 📌 Calculate Route")
            # Obtén los roles de nodos (Vertex -> str "storage"/"client"/etc)
            node_roles = st.session_state['node_roles']

            # Filtra solo nodos de almacenamiento para origen
            storage_nodes = [v for v, role in node_roles.items() if role == "storage"]

            # Filtra solo nodos de cliente para destino
            client_nodes = [v for v, role in node_roles.items() if role == "client"]

            start = st.selectbox(
                "Origin Node (Solo almacén)",
                storage_nodes,
                format_func=lambda v: f"{v} (Almacenamiento)"
            )
            end = st.selectbox(
                "Destination Node (Solo cliente)",
                client_nodes,
                format_func=lambda v: f"{v} (Cliente)"
            )

            matching_order = None
            for order in st.session_state.get('orders', []):
                if (
                    getattr(order, "origin", None) == str(start) and
                    getattr(order, "destination", None) == str(end) and
                    getattr(order, "status", None) == "pending"
                ):
                    matching_order = order
                    break

            if st.button("🧭 Calculate Route"):
                path, cost = Simulation.get_shortest_path(
                    st.session_state['graph'],
                    start,
                    end,
                    st.session_state['autonomy'],
                    st.session_state['recharge_nodes']
                )
                if path and len(path) > 1:
                    st.session_state['last_route_path'] = path
                    st.success(f"Route found: {[str(v) for v in path]} (Cost: {cost})")
                    # Aquí actualizas los rankings y la AVL, etc.
                    route_key = " → ".join(str(v) for v in path)
                    st.session_state['routes_avl'].insert(route_key)
                    visits = st.session_state['node_visits']
                    for v in path:
                        v_str = str(v)
                        if v_str in visits:
                            visits[v_str] += 1
                        else:
                            visits[v_str] = 1
                else:
                    st.error("No route found (autonomy or recharge limit reached).")
                st.rerun()

                if route:
                    st.session_state['last_route_path'] = route.path
                    st.success(f"Route found: {route.path} (Cost: {route.cost})")
                    route_key = " → ".join(str(v) for v in route.path)
                    st.session_state['routes_avl'].insert(route_key)
                    # Usar Map aquí para las visitas:
                    visits = st.session_state['node_visits']
                    for v in route.path:
                        v_str = str(v)
                        if v_str in visits:
                            visits[v_str] += 1
                        else:
                            visits[v_str] = 1
                st.rerun()

            st.markdown("### 🌲 Árbol de Expansión Mínima (MST)")

            if st.session_state.get('simulation_ready'):
                # ... (tu visualización de grafo actual)
                
                if st.button("🌲 Mostrar/Ocultar MST"):
                    if st.session_state['mst_visible']:
                        # Oculta el MST
                        st.session_state['mst_visible'] = False
                        st.session_state['mst_edges'] = None
                    else:
                        # Calcula y muestra el MST
                        mst_edges = kruskal_mst(st.session_state['graph'])
                        # Si usas strings para nodos en NetworkX:
                        st.session_state['mst_edges'] = [(str(e.endpoints()[0]), str(e.endpoints()[1])) for e in mst_edges]
                        st.session_state['mst_visible'] = True
                    st.rerun()

            if matching_order:
                st.info(f"Pending order found for this route: {getattr(matching_order, 'order_id', '')} "
                        f"(Priority: {getattr(matching_order, 'priority', '')})")
                if st.button("✅ Complete Delivery"):
                    matching_order.status = "completed"
                    matching_order.delivered_at = datetime.datetime.now().isoformat()
                    st.success(f"Order {getattr(matching_order, 'order_id', '')} marked as completed at {matching_order.delivered_at}")
                    st.rerun()
    else:
        st.info("No nodes registered yet.")

# ------------------ TAB 3: Visualización de clientes y órdenes ------------------
with tab3:
    st.write("### Clients")
    if 'clients' in st.session_state:
        clients_list = [c.to_dict() for c in st.session_state['clients']]
        st.json(clients_list, expanded=False)
    else:
        st.info("No clients registered yet.")

    st.write("### Orders")
    if 'orders' in st.session_state:
        orders_list = [o.to_dict() for o in st.session_state['orders']]
        st.json(orders_list, expanded=False)

    else:
        st.info("No orders registered yet.")

# ------------------ TAB 4: Route Analytics y AVL ------------------
with tab4:
    st.markdown("## 🔁 Route Analytics")
    avl_obj = st.session_state.get('routes_avl')

    # --- Top rutas más frecuentes ---
    st.markdown("### 🏅 Most Frequent Routes")
    if avl_obj and avl_obj.root:
        routes = avl_obj.in_order()
        if routes:
            routes = sorted(routes, key=lambda x: -x[1])
            st.markdown(
                "<div style='margin-bottom: 1em;'>"
                + "".join(
                    f"<div style='margin-bottom: 6px;'>"
                    f"<b>{idx}.</b> <span style='color:deepskyblue'>{path}</span>"
                    f" <span style='color:orange'>(freq: {freq})</span>"
                    f"</div>"
                    for idx, (path, freq) in enumerate(routes[:10], 1)
                )
                + "</div>",
                unsafe_allow_html=True,
            )
        else:
            st.info("No routes registered yet.")
    else:
        st.info("No routes registered yet.")

    # --- Visualización AVL ---
    st.markdown("### 🌳 AVL Tree Visualization")
    if avl_obj and avl_obj.root:
        G = NetworkAdapter.avl_to_nx_graph(avl_obj.root, avl_obj.freqs)
        pos = AVL_visualizer.hierarchy_pos(G)
        fig, ax = plt.subplots(figsize=(10, 4))
        nx.draw(
            G, pos, with_labels=True, arrows=True,
            node_size=1800, node_color="#a7d2ec",
            font_size=10, font_weight="bold", ax=ax
        )
        st.pyplot(fig)

        st.markdown("### 📄 Generar Informe PDF")

    # Recopila los datos necesarios del sistema:
    # 1. Estadísticas generales
    stats = {
        "Nodos": st.session_state.get("n_nodes", 0),
        "Aristas": st.session_state.get("m_edges", 0),
        "Órdenes totales": len(st.session_state.get("orders", [])),
        "Rutas registradas": len(st.session_state.get("routes_avl", AVL()).in_order()),
        "Clientes": len(st.session_state.get("clients", [])),
    }

    # 2. Pedidos y clientes
    orders = st.session_state.get("orders", [])
    clients = st.session_state.get("clients", [])

    # 3. Rutas frecuentes (formato: lista de (ruta, frecuencia))
    avl_obj = st.session_state.get('routes_avl')
    routes = []
    if avl_obj and avl_obj.root:
        routes = sorted(avl_obj.in_order(), key=lambda x: -x[1])

    # 4. Nodos más usados (diccionario {str(node): visitas})
    node_visits_map = st.session_state.get("node_visits", {})
    if hasattr(node_visits_map, "items"):  # Es tu HashMap propio
        node_visit_stats = {str(k): node_visits_map[k] for k in node_visits_map}
    else:  # Es dict plano
        node_visit_stats = node_visits_map

    node_roles = st.session_state.get("node_roles", {})
    role_counts = {"storage": 0, "recharge": 0, "client": 0}
    for role in node_roles.values():
        if role in role_counts:
            role_counts[role] += 1

    # --- Botón para generar PDF ---
    if st.button("📄 Generar Informe PDF"):
        # Asegura que las claves de node_roles sean string
        node_roles_str = {str(k): v for k, v in node_roles.items()}

        generator = ReportGenerator(
            stats,
            orders,
            clients,
            routes,
            node_visit_stats,
            role_counts,
            node_roles_str           # <-- Agrega esto para los rankings por tipo de nodo
        )
        filename = generator.generate_pdf("reporte.pdf")
        with open(filename, "rb") as f:
            st.download_button(
                label="Descargar reporte PDF",
                data=f,
                file_name="reporte.pdf",
                mime="application/pdf"
            )
    else:
        st.info("AVL Tree not available yet.")



# ------------------ TAB 5: Estadísticas generales ------------------
with tab5:
    st.markdown("## 📊 General Statistics")
    st.markdown("### 🏆 Top Visited Nodes by Role")

    node_visits = st.session_state.get('node_visits', None)
    node_roles = st.session_state.get('node_roles', None)

    if not node_visits or not node_roles or len(node_roles) == 0:
        st.info("No node data available. Run the simulation and generate at least one route.")
    else:
        roles = {"client": [], "recharge": [], "storage": []}
        visits_by_role = {"client": [], "recharge": [], "storage": []}

        for v, role in node_roles.items():
            v_str = str(v)
            if role in roles:
                roles[role].append(v_str)
                visits_by_role[role].append(node_visits.get(v_str, 0))

        no_clients = len(roles["client"]) == 0
        no_recharge = len(roles["recharge"]) == 0
        no_storage = len(roles["storage"]) == 0

        col1, col2, col3 = st.columns(3, gap="large")

        with col1:
            st.markdown("##### 👤 Most Visited Clients")
            if no_clients or all(v == 0 for v in visits_by_role["client"]):
                st.info("No client node visits recorded.")
            else:
                fig1 = go.Figure([go.Bar(
                    x=roles["client"],
                    y=visits_by_role["client"],
                    marker_color="lightskyblue"
                )])
                fig1.update_layout(xaxis_title="Client Node", yaxis_title="Visits", showlegend=False)
                st.plotly_chart(fig1, use_container_width=True, key="clients_bar")

        with col2:
            st.markdown("##### 🟩 Most Visited Recharge Stations")
            if no_recharge or all(v == 0 for v in visits_by_role["recharge"]):
                st.info("No recharge station visits recorded.")
            else:
                fig2 = go.Figure([go.Bar(
                    x=roles["recharge"],
                    y=visits_by_role["recharge"],
                    marker_color="mediumseagreen"
                )])
                fig2.update_layout(xaxis_title="Recharge Node", yaxis_title="Visits", showlegend=False)
                st.plotly_chart(fig2, use_container_width=True, key="recharge_bar")

        with col3:
            st.markdown("##### 📦 Most Visited Storage Nodes")
            if no_storage or all(v == 0 for v in visits_by_role["storage"]):
                st.info("No storage node visits recorded.")
            else:
                fig3 = go.Figure([go.Bar(
                    x=roles["storage"],
                    y=visits_by_role["storage"],
                    marker_color="orange"
                )])
                fig3.update_layout(xaxis_title="Storage Node", yaxis_title="Visits", showlegend=False)
                st.plotly_chart(fig3, use_container_width=True, key="storage_bar")

        # --- Pie chart de proporciones ---
        st.markdown("### 🥧 Node Role Proportion")
        n_storage = len(roles["storage"])
        n_recharge = len(roles["recharge"])
        n_client = len(roles["client"])

        if n_storage == 0 and n_recharge == 0 and n_client == 0:
            st.info("No nodes to display in pie chart.")
        else:
            fig_pie = go.Figure(
                go.Pie(
                    labels=["Storage Nodes", "Recharge Nodes", "Client Nodes"],
                    values=[n_storage, n_recharge, n_client],
                    marker_colors=["orange", "mediumseagreen", "lightskyblue"],
                    hole=0.3,
                    textinfo="label+percent"
                )
            )
            fig_pie.update_layout(showlegend=True)
            # Usa una sola vez el key="roles_pie" y elimina duplicados
            st.plotly_chart(fig_pie, use_container_width=True, key="roles_pie")
