import sys
import os
import random
import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from sim.init_simulation import generate_connected_graph
from sim.simulation import bfs_shortest_path
from visual.network_adapter import graph_to_networkx, get_spring_params, avl_to_nx_graph
from visual.avl_visualizer import hierarchy_pos
from tda.avl import AVL
from tda.hash_map import Map
from domain.client import Client
from domain.order import Order

import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import plotly.graph_objects as go

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
        graph, vertices = generate_connected_graph(n_nodes, m_edges)
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
            route_result = bfs_shortest_path(graph, src, tgt, autonomy, recharge_nodes)
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

# ------------------ TAB 2: Visualización del grafo y cálculo de rutas ------------------
with tab2:
    st.markdown("<h2>🌍 Network Visualization</h2>", unsafe_allow_html=True)
    st.markdown("#### Drone Delivery Network")

    if st.session_state.get('simulation_ready'):
        col_grafo, col_ruta = st.columns([3, 1], gap="large")

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

            legend_elements = [
                mpatches.Patch(color="orange", label="Storage"),
                mpatches.Patch(color="blue", label="Recharge"),
                mpatches.Patch(color="green", label="Client")
            ]
            ax.legend(handles=legend_elements, loc="best", title="Node Roles")
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

        with col_ruta:
            st.markdown("### 📌 Calculate Route")
            options = list(st.session_state['graph'].vertices())
            node_roles = st.session_state['node_roles']
            start = st.selectbox(
                "Origin Node", options,
                format_func=lambda v: f"{v} ({node_roles.get(v, '-')})",
                key="route_start"
            )
            end = st.selectbox(
                "Destination Node", options,
                format_func=lambda v: f"{v} ({node_roles.get(v, '-')})",
                key="route_end"
            )

            # Encuentra orden pendiente (si existe) para ese origen/destino
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

            if matching_order:
                st.info(f"Pending order found for this route: {getattr(matching_order, 'order_id', '')} "
                        f"(Priority: {getattr(matching_order, 'priority', '')})")
                if st.button("✅ Complete Delivery"):
                    matching_order.status = "completed"
                    matching_order.delivered_at = datetime.datetime.now().isoformat()
                    st.success(f"Order {getattr(matching_order, 'order_id', '')} marked as completed at {matching_order.delivered_at}")
                    st.rerun()

# ------------------ TAB 3: Visualización de clientes y órdenes ------------------
with tab3:
    st.write("### Clients")
    if 'clients' in st.session_state:
        clients_list = [c.to_dict() for c in st.session_state['clients']]
        st.json(clients_list, expanded=False)

    st.write("### Orders")
    if 'orders' in st.session_state:
        orders_list = [o.to_dict() for o in st.session_state['orders']]
        st.json(orders_list, expanded=False)

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
        G = avl_to_nx_graph(avl_obj.root, avl_obj.freqs)
        pos = hierarchy_pos(G)
        fig, ax = plt.subplots(figsize=(10, 4))
        nx.draw(
            G, pos, with_labels=True, arrows=True,
            node_size=1800, node_color="#a7d2ec",
            font_size=10, font_weight="bold", ax=ax
        )
        st.pyplot(fig)
    else:
        st.info("AVL Tree not available yet.")

# ------------------ TAB 5: Estadísticas generales ------------------
with tab5:
    st.markdown("## 📊 General Statistics")
    st.markdown("### 🏆 Top Visited Nodes by Role")

    node_visits = st.session_state.get('node_visits', Map())
    node_roles = st.session_state.get('node_roles', {})


    roles = {"client": [], "recharge": [], "storage": []}
    visits_by_role = {"client": [], "recharge": [], "storage": []}

    for v, role in node_roles.items():
        v_str = str(v)
        if role in roles:
            roles[role].append(v_str)
            visits_by_role[role].append(node_visits.get(v_str, 0))

    col1, col2, col3 = st.columns(3, gap="large")

    with col1:
        st.markdown("##### 👤 Most Visited Clients")
        fig1 = go.Figure([go.Bar(
            x=roles["client"],
            y=visits_by_role["client"],
            marker_color="lightskyblue"
        )])
        fig1.update_layout(xaxis_title="Client Node", yaxis_title="Visits", showlegend=False)
        st.plotly_chart(fig1, use_container_width=True, key="clients_bar")

    with col2:
        st.markdown("##### 🟩 Most Visited Recharge Stations")
        fig2 = go.Figure([go.Bar(
            x=roles["recharge"],
            y=visits_by_role["recharge"],
            marker_color="mediumseagreen"
        )])
        fig2.update_layout(xaxis_title="Recharge Node", yaxis_title="Visits", showlegend=False)
        st.plotly_chart(fig2, use_container_width=True, key="recharge_bar")

    with col3:
        st.markdown("##### 📦 Most Visited Storage Nodes")
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
    st.plotly_chart(fig_pie, use_container_width=True, key="roles_pie")
