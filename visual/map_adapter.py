import folium
import networkx as nx
import random

class MapAdapter:
    @staticmethod
    def network_to_folium(G, node_roles, route_path=None):
        # Asigna posiciones geográficas ficticias si no existen
        if 'pos' in G.graph:
            pos = G.graph['pos']
        else:
            pos = MapAdapter._generate_latlon_positions(G)
            G.graph['pos'] = pos

        lats = [lat for lat, lon in pos.values()]
        lons = [lon for lat, lon in pos.values()]
        center = [sum(lats)/len(lats), sum(lons)/len(lons)]

        fmap = folium.Map(location=center, zoom_start=13, tiles="OpenStreetMap")

        # Colores e iconos según la imagen mostrada
        role_config = {
            "storage": {
                "color": "orange",      # Naranja para Storage
                "icon": "archive"       # Icono de archivo/almacén
            },
            "recharge": {
                "color": "green",       # Verde para Recharge
                "icon": "bolt"          # Icono de rayo/energía
            },
            "client": {
                "color": "blue",        # Azul para Client
                "icon": "user"          # Icono de usuario
            }
        }

        # Agregar nodos al mapa
        for n in G.nodes:
            lat, lon = pos[n]
            role = node_roles.get(n, "client")
            role_str = str(role).lower()
            
            # Obtener configuración del rol
            config = role_config.get(role_str, role_config["client"])
            
            folium.Marker(
                location=[lat, lon],
                popup=f"<b>{n}</b><br>Role: {role.capitalize()}",
                tooltip=f"{n} ({role})",
                icon=folium.Icon(
                    color=config["color"],
                    icon=config["icon"]
                )
            ).add_to(fmap)

        # Agregar aristas (conexiones entre nodos)
        for u, v, data in G.edges(data=True):
            lat1, lon1 = pos[u]
            lat2, lon2 = pos[v]
            
            folium.PolyLine(
                locations=[(lat1, lon1), (lat2, lon2)],
                color="blue",
                weight=2,
                opacity=0.6,
                tooltip=f"Edge: {u} ↔ {v}"
            ).add_to(fmap)

        # Agregar ruta resaltada si existe
        if route_path and len(route_path) > 1:
            route_coords = []
            for node in route_path:
                # Buscar el nodo en pos, manejando diferentes tipos de keys
                found_pos = None
                for pos_key in pos:
                    if str(pos_key) == str(node):
                        found_pos = pos[pos_key]
                        break
                
                if found_pos:
                    route_coords.append(found_pos)
            
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