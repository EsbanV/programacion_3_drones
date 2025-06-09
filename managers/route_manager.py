from collections import deque

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
        queue = deque()
        visited = set()
        queue.append((origin, [origin], self.battery_limit, 0, []))

        while queue:
            current, path, battery, cost, recharges = queue.popleft()
            if current == destination:
                return path, cost, recharges

            visited.add((current, battery))

            for neighbor, weight in self._graph.get_neighbors(current):
                if battery >= weight:
                    next_battery = battery - weight
                    next_recharges = list(recharges)
                elif current in self.recharge_stations:
                    next_battery = self.battery_limit - weight
                    next_recharges = recharges + [current]
                else:
                    continue

                if (neighbor, next_battery) not in visited:
                    queue.append((
                        neighbor,
                        path + [neighbor],
                        next_battery,
                        cost + weight,
                        next_recharges
                    ))

        return [], float('inf'), []

    def update_battery_limit(self, new_limit):
        self.battery_limit = new_limit
