class Order:
    def __init__(self, order_id, client, client_id, origin, destination, status="pending", priority=0, created_at=None, delivered_at=None, route_cost=None):
        self.order_id = order_id
        self.client = client
        self.client_id = client_id
        self.origin = origin
        self.destination = destination
        self.status = status
        self.priority = priority
        self.created_at = created_at
        self.delivered_at = delivered_at
        self.route_cost = route_cost

    def __repr__(self):
        return (f"Order(order_id={self.order_id}, client={self.client}, "
                f"client_id={self.client_id}, origin={self.origin}, "
                f"destination={self.destination}, status={self.status}, "
                f"priority={self.priority}, created_at={self.created_at}, "
                f"delivered_at={self.delivered_at}, route_cost={self.route_cost})")

    def to_dict(self):
        """Devuelve un dict compatible para st.json"""
        return {
            "order_id": self.order_id,
            "client": str(self.client),
            "client_id": self.client_id,
            "origin": self.origin,
            "destination": self.destination,
            "status": self.status,
            "priority": self.priority,
            "created_at": self.created_at,
            "delivered_at": self.delivered_at,
            "route_cost": self.route_cost
        }
