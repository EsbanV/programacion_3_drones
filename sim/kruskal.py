# sim/kruskal.py

def kruskal_mst(graph):
    parent = {}
    rank = {}

    def find(u):
        while parent[u] != u:
            parent[u] = parent[parent[u]]
            u = parent[u]
        return u

    def union(u, v):
        ru, rv = find(u), find(v)
        if ru == rv:
            return False
        if rank[ru] < rank[rv]:
            parent[ru] = rv
        else:
            parent[rv] = ru
            if rank[ru] == rank[rv]:
                rank[ru] += 1
        return True

    for v in graph.vertices():
        parent[v] = v
        rank[v] = 0

    mst = []
    edges = sorted(graph.edges(), key=lambda e: e.element())
    for e in edges:
        u, v = e.endpoints()
        if union(u, v):
            mst.append(e)
    return mst

# Asumiendo que graph.vertices() da los Vertex originales
def get_vertex_from_str(graph, s):
    for vertex in graph.vertices():
        if str(vertex) == str(s):
            return vertex
    return None
