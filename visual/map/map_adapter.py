import folium
import networkx as nx
import random

class MapAdapter:
    @staticmethod
    def network_to_folium(G, node_roles, route_path=None, mst_edges=None, graph=None):
        """
        Parámetros:
        - G: grafo NetworkX (para layout y aristas)
        - node_roles: dict (nodo -> str rol)
        - route_path: lista de nodos (camino activo)
        - mst_edges: lista de pares (u, v) del MST
        - graph: objeto Graph propio, para consultar pesos de aristas reales (requerido para tooltips)
        """
        # 1. Generar o recuperar posiciones para todos los nodos
        if 'pos' not in G.graph:
            G.graph['pos'] = MapAdapter._generate_latlon_positions(G)
        pos = G.graph['pos']

        # 2. Calcular centro del mapa
        lats = [pos[n][0] for n in G.nodes if n in pos]
        lons = [pos[n][1] for n in G.nodes if n in pos]
        center = [sum(lats)/len(lats), sum(lons)/len(lons)] if lats and lons else [-33.45, -70.65]

        fmap = folium.Map(location=center, zoom_start=13, tiles="OpenStreetMap")

        # 3. Dibujar TODAS las aristas (gris)
        for u, v, data in G.edges(data=True):
            if u in pos and v in pos:
                weight = data.get('weight', 1)
                folium.PolyLine(
                    locations=[pos[u], pos[v]],
                    color="gray",
                    weight=2 + weight/5,
                    opacity=0.6,
                    tooltip=f"Edge: {u} ↔ {v} (Weight: {weight})",
                    popup=f"Weight: {weight}"
                ).add_to(fmap)

        # 4. Dibujar las aristas del MST (azul punteada) con peso
        if mst_edges and graph is not None:
            for u, v in mst_edges:
                u_obj = MapAdapter._vertex_from_str(graph, u)
                v_obj = MapAdapter._vertex_from_str(graph, v)
                edge = graph.get_edge(u_obj, v_obj) if u_obj and v_obj else None
                weight = edge.element() if edge else "?"
                if u in pos and v in pos:
                    folium.PolyLine(
                        locations=[pos[u], pos[v]],
                        color="deepskyblue",
                        weight=6,
                        opacity=0.8,
                        dash_array="10",
                        tooltip=f"MST Edge: {u} ↔ {v} (Weight: {weight})"
                    ).add_to(fmap)

        # 5. Dibujar los nodos
        for n in G.nodes:
            if n not in pos:
                continue
            lat, lon = pos[n]
            role = "client"
            for key in node_roles:
                if str(key) == str(n):
                    role = node_roles[key]
                    break
            icon_config = {
                "storage": {"color": "orange", "icon": "warehouse", "prefix": "fa"},
                "recharge": {"color": "green", "icon": "bolt", "prefix": "fa"},
                "client": {"color": "blue", "icon": "user", "prefix": "fa"}
            }.get(role, {"color": "blue", "icon": "user", "prefix": "fa"})
            folium.Marker(
                location=[lat, lon],
                popup=f"<b>Node {n}</b><br>Type: {role}",
                tooltip=f"{n} ({role})",
                icon=folium.Icon(**icon_config, icon_color="white")
            ).add_to(fmap)

        # 6. Dibujar ruta resaltada (roja) tramo a tramo con pesos
        if route_path and len(route_path) > 1 and graph is not None:
            for i in range(len(route_path) - 1):
                u = route_path[i]
                v = route_path[i + 1]
                u_pos, v_pos = None, None
                for pos_key in pos:
                    if str(pos_key) == str(u):
                        u_pos = pos[pos_key]
                    if str(pos_key) == str(v):
                        v_pos = pos[pos_key]
                if u_pos and v_pos:
                    edge = graph.get_edge(u, v)
                    weight = edge.element() if edge else "?"
                    folium.PolyLine(
                        locations=[u_pos, v_pos],
                        color="red",
                        weight=4,
                        opacity=0.8,
                        tooltip=f"Route: {u} ↔ {v} (Weight: {weight})"
                    ).add_to(fmap)

        return fmap

    @staticmethod
    def _generate_latlon_positions(G):
        # Genera posiciones en el área de Santiago, Chile
        base_lat, base_lon = -33.45, -70.65
        delta = 0.05
        nodes = list(G.nodes)
        random.seed(42)
        pos = {}
        for i, n in enumerate(nodes):
            lat = base_lat + random.uniform(-delta, delta)
            lon = base_lon + random.uniform(-delta, delta)
            pos[n] = (lat, lon)
        return pos
    
    @staticmethod
    def _vertex_from_str(graph, s):
        for v in graph.vertices():
            if str(v) == str(s):
                return v
        return None

