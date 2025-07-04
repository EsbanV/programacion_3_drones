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

        fmap = folium.Map(location=center, zoom_start=13, tiles="cartodbpositron")

        # Colores y iconos por rol (usar colores válidos para folium.Icon)
        role_colors = {
            "storage": "orange",    # folium.Icon color: 'orange'
            "recharge": "blue",     # folium.Icon color: 'blue'
            "client": "green"       # folium.Icon color: 'green'
        }
        role_icons = {
            "storage": "archive",    # fa-archive
            "recharge": "bolt",      # fa-bolt
            "client": "user"         # fa-user
        }

        # Nodos diferenciados por color e icono
        for n in G.nodes:
            lat, lon = pos[n]
            role = node_roles.get(n, "client")
            # Asegura que el rol sea string y minúscula
            role_str = str(role).lower()
            color = role_colors.get(role_str, "gray")
            icon = role_icons.get(role_str, "info-sign")
            folium.Marker(
                location=[lat, lon],
                popup=f"{n} ({role})",
                icon=folium.Icon(color=color, icon=icon, prefix="fa")
            ).add_to(fmap)

        # Aristas
        for u, v, data in G.edges(data=True):
            latlngs = [pos[u], pos[v]]
            folium.PolyLine(
                locations=latlngs,
                color="gray",
                weight=2,
                opacity=0.5,
                tooltip=f"Weight: {data.get('weight', '')}"
            ).add_to(fmap)

        # Ruta resaltada
        if route_path and len(route_path) > 1:
            route_latlngs = []
            for n in route_path:
                n_str = str(n)
                if n in pos:
                    route_latlngs.append(pos[n])
                elif n_str in pos:
                    route_latlngs.append(pos[n_str])
                else:
                    found = False
                    for k in pos:
                        if str(k) == n_str:
                            route_latlngs.append(pos[k])
                            found = True
                            break
                    if not found:
                        continue  # omite si no encuentra
            if len(route_latlngs) > 1:
                folium.PolyLine(
                    locations=route_latlngs,
                    color="red",
                    weight=5,
                    opacity=0.9,
                    tooltip="Route"
                ).add_to(fmap)

        return fmap

    @staticmethod
    def _generate_latlon_positions(G):
        # Distribuye nodos en un área ficticia de Santiago, Chile
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
        nodes = list(G.nodes)
        random.seed(42)
        pos = {}
        for i, n in enumerate(nodes):
            lat = base_lat + random.uniform(-delta, delta)
            lon = base_lon + random.uniform(-delta, delta)
            pos[n] = (lat, lon)
        return pos
