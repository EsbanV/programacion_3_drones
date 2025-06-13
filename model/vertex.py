class Vertex:
    __slots__ = '_element'

    def __init__(self, element):
        self._element = element

    def element(self):
        return self._element

    def __hash__(self):
        return hash(self._element)

    def __eq__(self, other):
        return isinstance(other, Vertex) and self._element == other._element

    def __str__(self):
        return str(self._element)

    def __repr__(self):
        return f"Vertex({self._element})"
