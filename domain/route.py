class Route:
    def __init__(self, path, cost):
        self.path = path
        self.cost = cost

    def __repr__(self):
        return f"Route(path={[str(v) for v in self.path]}, cost={self.cost})"
