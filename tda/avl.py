class Node:
    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None
        self.height = 0

class AVL:
    def __init__(self):
        self.root = None
        self.freqs = {}

    def insert(self, key):
        self.root = self._insert(self.root, key)
        self.freqs[key] = self.freqs.get(key, 0) + 1

    def _insert(self, node, key):
        if node is None:
            return Node(key)
        if key < node.key:
            node.left = self._insert(node.left, key)
        elif key > node.key:
            node.right = self._insert(node.right, key)
        else:
            return node
        node.height = 1 + max(self._height(node.left), self._height(node.right))
        return self._rebalance(node)

    def _height(self, n):
        return n.height if n else 0

    def _get_balance(self, n):
        return self._height(n.left) - self._height(n.right) if n else 0

    def _rebalance(self, node):
        balance = self._get_balance(node)
        if balance > 1:
            if self._get_balance(node.left) < 0:
                node.left = self._left_rotate(node.left)
            return self._right_rotate(node)
        if balance < -1:
            if self._get_balance(node.right) > 0:
                node.right = self._right_rotate(node.right)
            return self._left_rotate(node)
        return node

    def _left_rotate(self, x):
        y = x.right
        T2 = y.left
        y.left = x
        x.right = T2
        x.height = 1 + max(self._height(x.left), self._height(x.right))
        y.height = 1 + max(self._height(y.left), self._height(y.right))
        return y

    def _right_rotate(self, y):
        x = y.left
        T2 = x.right
        x.right = y
        y.left = T2
        y.height = 1 + max(self._height(y.left), self._height(y.right))
        x.height = 1 + max(self._height(x.left), self._height(x.right))
        return x

    def in_order(self):
        result = []
        def _in_order(n):
            if n:
                _in_order(n.left)
                result.append((n.key, self.freqs.get(n.key, 0)))
                _in_order(n.right)
        _in_order(self.root)
        return result

    def get_freq(self, key):
        return self.freqs.get(key, 0)
