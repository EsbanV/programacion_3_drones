import random
from model.graph import Graph

class InitSimulation:

    @staticmethod
    def generate_connected_graph(n_nodes, m_edges):
        graph = Graph(directed=False)
        vertices = [graph.insert_vertex(i) for i in range(n_nodes)]

        for i in range(1, n_nodes):
            u = vertices[i]
            v = vertices[random.randint(0, i - 1)]
            weight = random.randint(1, 10)
            graph.insert_edge(u, v, weight)

        added = set()
        while len(list(graph.edges())) < m_edges:
            u, v = random.sample(vertices, 2)
            if (u, v) not in added and (v, u) not in added and not graph.get_edge(u, v):
                weight = random.randint(1, 10)
                graph.insert_edge(u, v, weight)
                added.add((u, v))

        return graph, vertices
