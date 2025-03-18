INITIAL_INVENTORY = 100
MAX_STORAGE_CAPACITY = 200

class Store:
    def __init__(self):
        self.inventory = INITIAL_INVENTORY
        self.order_history = []
        self.demand_history = []
        self.supplier_history = []
        self.stockouts = 0

    def receive_order(self, quantity, supplier_name):
        """Increase inventory when an order arrives"""
        self.inventory = min(self.inventory + quantity, MAX_STORAGE_CAPACITY)
        self.order_history.append(quantity)
        self.supplier_history.append(supplier_name)

    def fulfill_demand(self, demand):
        """Fulfill demand while tracking stockouts"""
        fulfilled = min(self.inventory, demand)
        self.inventory -= fulfilled
        self.demand_history.append(demand)
        if fulfilled < demand:
            self.stockouts += 1
        return fulfilled
