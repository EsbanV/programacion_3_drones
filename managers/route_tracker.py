class RouteTracker:
    def __init__(self, avl_tree, hash_map):
        """
        avl_tree: estructura AVL para frecuencias de rutas
        hash_map: diccionario o implementación custom para visitas por nodo
        """
        self.avl = avl_tree
        self.hash_map = hash_map

    def record_route(self, route):
        """
        Registra una ruta (list de Vertex).
        Incrementa la frecuencia en AVL y cuenta visitas en hash_map.
        """
        pass

    def route_to_string(self, route):
        """Convierte una ruta (list de Vertex) al formato 'A→B→C'."""
        pass

    def get_route_frequencies(self):
        """Devuelve rutas ordenadas por frecuencia (desde el AVL)."""
        pass

    def get_node_visit_stats(self):
        """Devuelve visitas por nodo (desde el hash_map)."""
        pass

    def print_statistics_report(self):
        """Genera e imprime un reporte de estadísticas ordenadas."""
        pass
