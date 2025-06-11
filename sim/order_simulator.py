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
        # Buscar ruta usando el route_manager
        path, cost, recharge_stops = self.route_manager.find_route(origin, destination)
        
        # Si encontro ruta valida
        if path and cost != float('inf'):
            status = "Entregado"
            # Registrar ruta en tracker
            self.tracker.record_route(path)
        else:
            status = "Fallido"
            path = []
            cost = 0
            recharge_stops = []
        
        return path, cost, recharge_stops, status

    def process_orders(self, order_list):
        """
        Recibe una lista de órdenes (tuplas origen-destino) y procesa cada una.
        """
        for i, order in enumerate(order_list, 1):
            origin, destination = order
            path, cost, recharge_stops, status = self.generate_order(origin, destination)
            self.print_order_result(i, origin, destination, path, cost, recharge_stops, status)

    def print_order_result(self, order_id, origin, destination, route, cost, recharge_stops, status):
        """
        Imprime la salida esperada con el formato especificado en la tarea.
        """
        # Convertir ruta a string
        if route:
            route_str = " → ".join([str(node) for node in route])
        else:
            route_str = "No disponible"
        
        # Convertir paradas de recarga a string
        if recharge_stops:
            recharge_str = f"[{', '.join(recharge_stops)}]"
        else:
            recharge_str = "[]"
        
        # Imprimir formato requerido
        print(f"Orden #{order_id}: {origin} → {destination}")
        print(f"Ruta: {route_str}")
        print(f"Costo: {cost} | Paradas de recarga {recharge_str} | Estado: {status}")
