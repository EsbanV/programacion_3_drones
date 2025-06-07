class RouteOptimizer:
    def __init__(self, tracker, graph):
        """
        tracker: instancia de RouteTracker (acceso a historial)
        graph: instancia de Graph
        """
        self.tracker = tracker
        self.graph = graph

    def suggest_route(self, origin, destination):
        """
        Sugiere una ruta optimizada entre dos nodos considerando historial,
        eficiencia energética y rutas conocidas.
        Retorna: (ruta [list de Vertex], explicación de la decisión [str])
        """
        pass

    def analyze_common_segments(self, origin, destination):
        """
        Identifica y retorna segmentos comunes entre origen y destino según historial.
        """
        pass

    def document_heuristic(self):
        """
        Devuelve una descripción de la heurística aplicada.
        """
        pass
