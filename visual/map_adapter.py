import folium
import networkx as nx
import random

class MapAdapter:
    @staticmethod
    def network_to_folium(G, node_roles, route_path=None):
        # 1. Generar o recuperar posiciones para todos los nodos
        if 'pos' not in G.graph:
            G.graph['pos'] = MapAdapter._generate_latlon_positions(G)
        pos = G.graph['pos']

        # 2. Calcular centro del mapa
        lats = [pos[n][0] for n in G.nodes if n in pos]
        lons = [pos[n][1] for n in G.nodes if n in pos]
        center = [sum(lats)/len(lats), sum(lons)/len(lons)] if lats and lons else [-33.45, -70.65]

        fmap = folium.Map(location=center, zoom_start=13, tiles="OpenStreetMap")

        # 3. Dibujar TODAS las aristas primero (para que queden bajo los nodos)
        # En el bucle de aristas, reemplaza con:
        for u, v, data in G.edges(data=True):
            if u in pos and v in pos:
                weight = data.get('weight', 1)
                folium.PolyLine(
                    locations=[pos[u], pos[v]],
                    color="gray",
                    weight=2 + weight/5,
                    opacity=0.6,
                    tooltip=f"Edge: {u} ↔ {v} (Weight: {weight})",
                    popup=f"Weight: {weight}"  # Aparece al hacer click
                ).add_to(fmap)

        # 4. Dibujar los nodos con sus iconos
        for n in G.nodes:
            if n not in pos:  # Si el nodo no tiene posición, saltarlo
                continue
                
            lat, lon = pos[n]
            role = "client"
            
            # Buscar el rol comparando strings
            for key in node_roles:
                if str(key) == str(n):
                    role = node_roles[key]
                    break

            # Configuración de iconos según rol
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

        # 5. Dibujar ruta resaltada (si existe)
        if route_path and len(route_path) > 1:
            route_coords = []
            for node in route_path:
                node_str = str(node)
                # Buscar la posición correspondiente al nodo
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