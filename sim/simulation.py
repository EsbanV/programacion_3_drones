from collections import deque
from domain.route import Route
from sim.kruskal import kruskal_mst
from sim.dijkstra import dijkstra_with_recharge

class Simulation:
    @staticmethod
    def get_shortest_path(graph, start, end, autonomy, recharge_nodes):
        return dijkstra_with_recharge(graph, start, end, autonomy, recharge_nodes)

    @staticmethod
    def bfs_shortest_path(graph, start, goal, autonomy_limit, recharge_nodes):
        queue = deque()
        queue.append((start, [start], 0))
        visited = set()

        while queue:
            current, path, cost = queue.popleft()
            if current == goal and cost <= autonomy_limit:
                return Route(path, cost)

            visited.add(current)

            for neighbor in graph.neighbors(current):
                edge = graph.get_edge(current, neighbor)
                edge_weight = edge.element()
                new_cost = cost + edge_weight

                if new_cost > autonomy_limit and current not in recharge_nodes:
                    continue

                if neighbor not in visited:
                    next_path = path + [neighbor]
                    if neighbor in recharge_nodes:
                        queue.append((neighbor, next_path, edge_weight))
                    else:
                        queue.append((neighbor, next_path, new_cost))
        return None
    
    @staticmethod
    def get_mst(graph):
        return kruskal_mst(graph)
