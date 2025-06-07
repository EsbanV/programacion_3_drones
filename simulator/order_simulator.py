class OrderSimulator:
    def __init__(self, route_manager, tracker, optimizer):
        """
        route_manager: instancia de RouteManager
        tracker: instancia de RouteTracker
        optimizer: instancia de RouteOptimizer
        """
        self.route_manager = route_manager
        self.tracker = tracker
        self.optimizer = optimizer

    def generate_order(self, origin, destination):
        """
        Genera y procesa una orden entre origen y destino.
        Llama a los managers necesarios, registra la ruta y estadísticas.
        """
        pass

    def process_orders(self, order_list):
        """
        Recibe una lista de órdenes (tuplas origen-destino) y procesa cada una.
        """
        pass

    def print_order_result(self, order_id, origin, destination, route, cost, recharge_stops, status):
        """
        Imprime la salida esperada con el formato especificado en la tarea.
        """
        pass
