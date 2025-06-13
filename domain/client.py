class Client:
    def __init__(self, client_id, name, type_, total_orders=0, node=None):
        self.client_id = client_id    # Ejemplo: "C017"
        self.name = name              # Ejemplo: "Client17"
        self.type = type_             # Ejemplo: "premium" o "normal"
        self.total_orders = total_orders  # Ejemplo: 1
        self.node = node              # Mantiene compatibilidad con el nodo original (opcional)

    def __repr__(self):
        return (f"Client(client_id={self.client_id}, name={self.name}, "
                f"type={self.type}, total_orders={self.total_orders}, node={self.node})")

    def to_dict(self):
        """Devuelve un dict compatible para st.json"""
        return {
            "client_id": self.client_id,
            "name": self.name,
            "type": self.type,
            "total_orders": self.total_orders
        }