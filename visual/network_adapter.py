import networkx as nx

def graph_to_networkx(graph, node_roles=None):
    G = nx.Graph()
    for v in graph.vertices():
        G.add_node(str(v), role=node_roles.get(v, 'client') if node_roles else 'client')
    for e in graph.edges():
        u, v = e.endpoints()
        G.add_edge(str(u), str(v), weight=e.element())
    return G

def get_spring_params(n_nodes):

    if n_nodes <= 10:
        return {"k": 2.5, "iterations": 300, "scale": 2.5}
    elif n_nodes <= 20:
        return {"k": 2.0, "iterations": 300, "scale": 3.0}
    elif n_nodes <= 40:
        return {"k": 1.2, "iterations": 400, "scale": 4.0}
    elif n_nodes <= 80:
        return {"k": 0.8, "iterations": 500, "scale": 5.0}
    else:
        return {"k": 0.4, "iterations": 600, "scale": 8.0}

def avl_to_nx_graph(root, freqs, G=None, parent=None):
    if G is None:
        G = nx.DiGraph()
    if root:
        label = f"{root.key}\nFreq: {freqs.get(root.key, 0)}"
        G.add_node(label)
        if parent:
            G.add_edge(parent, label)
        avl_to_nx_graph(root.left, freqs, G, label)
        avl_to_nx_graph(root.right, freqs, G, label)
    return G
