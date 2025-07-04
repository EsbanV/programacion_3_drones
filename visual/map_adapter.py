import folium
import networkx as nx
import random
from model.edge import Edge

class MapAdapter:
    @staticmethod
    def network_to_folium(G, node_roles, route_path=None, mst_edges=None):
        # 1. Generar o recuperar posiciones
        if 'pos' not in G.graph:
            G.graph['pos'] = MapAdapter._generate_latlon_positions(G)
        pos = G.graph['pos']

        # 2. Centro del mapa
        lats = [pos[n][0] for n in G.nodes if n in pos]
        lons = [pos[n][1] for n in G.nodes if n in pos]
        center = [sum(lats)/len(lats), sum(lons)/len(lons)] if lats and lons else [-33.45, -70.65]

        fmap = folium.Map(location=center, zoom_start=13, tiles="OpenStreetMap")

        # 3. Dibujar MST si existe
        mst_set = set()
        if mst_edges:
            for u, v in mst_edges:
                u_str = str(u)
                v_str = str(v)
                if u_str in pos and v_str in pos:
                    folium.PolyLine(
                        locations=[pos[u_str], pos[v_str]],
                        color="#046108",   # verde oscuro
                        weight=4,          # un poco más gruesa
                        opacity=0.9,
                        dash_array="10,10", # líneas cortadas (dash)
                        tooltip=f"MST Edge: {u_str} ↔ {v_str}"
                    ).add_to(fmap)
                    mst_set.add(tuple(sorted((u_str, v_str))))


        # 4. Dibujar aristas normales (excluyendo las del MST)
        if not mst_edges or len(mst_edges) == 0:
            for u, v, data in G.edges(data=True):
                u_str = str(u)
                v_str = str(v)
                if u_str in pos and v_str in pos:
                    weight = data.get('weight', 1)
                    folium.PolyLine(
                        locations=[pos[u_str], pos[v_str]],
                        color="gray",
                        weight=2 + weight / 5,
                        opacity=0.6,
                        tooltip=f"Edge: {u_str} ↔ {v_str} (Weight: {weight})",
                        popup=f"Weight: {weight}"
                    ).add_to(fmap)


        # 5. Dibujar nodos con íconos
        for n in G.nodes:
            n_str = str(n)
            if n_str not in pos:
                continue
            lat, lon = pos[n_str]
            role = "client"
            for key in node_roles:
                if str(key) == n_str:
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

        # 6. Dibujar ruta si existe
        if route_path and len(route_path) > 1:
            route_coords = []
            for node in route_path:
                node_str = str(node)
                for pos_key in pos:
                    if str(pos_key) == node_str:
                        route_coords.append(pos[pos_key])
                        break

            if len(route_coords) > 1:
                folium.PolyLine(
                    locations=route_coords,
                    color="red",
                    weight=4,
                    opacity=0.8,
                    tooltip="Active Route"
                ).add_to(fmap)

        return fmap

    @staticmethod
    def _generate_latlon_positions(G):
        base_lat, base_lon = -33.45, -70.65
        delta = 0.05
        random.seed(42)
        pos = {}
        for n in G.nodes:
            lat = base_lat + random.uniform(-delta, delta)
            lon = base_lon + random.uniform(-delta, delta)
            pos[str(n)] = (lat, lon)
        return pos
