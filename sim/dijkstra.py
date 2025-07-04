# sim/dijkstra.py

import heapq
from itertools import count

def dijkstra_shortest_path(graph, start, goal):
    dist = {v: float('inf') for v in graph.vertices()}
    prev = {v: None for v in graph.vertices()}
    dist[start] = 0
    queue = [(0, start)]

    while queue:
        curr_dist, u = heapq.heappop(queue)
        if u == goal:
            break
        for v in graph.neighbors(u):
            edge = graph.get_edge(u, v)
            weight = edge.element()
            alt = curr_dist + weight
            if alt < dist[v]:
                dist[v] = alt
                prev[v] = u
                heapq.heappush(queue, (alt, v))

    path = []
    u = goal
    if prev[u] or u == start:
        while u is not None:
            path.insert(0, u)
            u = prev[u]
        return path, dist[goal]
    else:
        return None, float('inf')

def dijkstra_with_recharge(graph, start, goal, autonomy, recharge_nodes):
    recharge_nodes = set(recharge_nodes)
    heap = []
    unique = count()  # NUEVO: contador global para el heap

    # NOTA: todos los heappush y heappop usan la tupla: (cost, contador, ...)
    heapq.heappush(heap, (0, next(unique), start, autonomy, frozenset(), [start]))
    visited = dict()

    while heap:
        cost, _, u, battery, recs, path = heapq.heappop(heap)
        key = (u, battery, recs)
        if key in visited and visited[key] <= cost:
            continue
        visited[key] = cost

        if u == goal:
            return path, cost

        for v in graph.neighbors(u):
            edge = graph.get_edge(u, v)
            w = edge.element()
            if w > autonomy:
                continue
            if v in recharge_nodes and v not in recs:
                next_battery = autonomy
                next_recs = frozenset(set(recs) | {v})
            else:
                next_battery = battery
                next_recs = recs
            next_battery -= w
            if next_battery < 0:
                continue
            # Aquí está la clave: next(unique) como segundo valor
            heapq.heappush(heap, (cost + w, next(unique), v, next_battery, next_recs, path + [v]))

    return None, float('inf')
