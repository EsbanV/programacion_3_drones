class Client:
    def __init__(self, client_id, name, type_, total_orders=0, node=None):
        self.client_id = client_id
        self.name = name
        self.type = type_
        self.total_orders = total_orders
        self.node = node

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