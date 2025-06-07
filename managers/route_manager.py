class RouteManager:
    def __init__(self, graph, battery_limit, recharge_stations):
        """
        graph: instancia de Graph
        battery_limit: int (capacidad máxima de la batería)
        recharge_stations: set/list de Vertex (nodos con estación de recarga)
        """
        self._graph = graph
        self.battery_limit = battery_limit
        self.recharge_stations = set(recharge_stations)
    
    def find_route(self, origin, destination):
        """
        Calcula la ruta óptima considerando batería y recargas.
        Retorna: (ruta [list de Vertex], costo total, paradas de recarga [list de Vertex])
        """
        pass

    def update_battery_limit(self, new_limit):
        """Permite actualizar la capacidad máxima de batería."""
        pass
