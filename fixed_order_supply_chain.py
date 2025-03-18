import numpy as np
import simpy

REORDER_POINT = 50
ORDER_QUANTITY = 100

class FixedOrderSupplyChain:
    def __init__(self, env, store, supplier, demand_data):
        self.env = env
        self.store = store
        self.supplier = supplier
        self.demand_data = demand_data
        self.reorder_threshold = REORDER_POINT
        self.reorder_quantity = ORDER_QUANTITY
        self.pending_orders = []
        self.env.process(self.run())

    def run(self):
        for day in range(len(self.demand_data)):
            print(f"Day {day}: Inventory = {self.store.inventory}", end=" ")

            # Fulfill daily demand
            demand = self.demand_data[day]
            fulfilled = self.store.fulfill_demand(demand)
            print(f"| Demand: {demand}, Fulfilled: {fulfilled}", end=" ")

            order_placed = False
            self.receive_pending_orders()

            if self.store.inventory < self.reorder_threshold and len(self.pending_orders) == 0:
                delivery_time = np.random.randint(4, 7)
                self.pending_orders.append((self.env.now + delivery_time, self.reorder_quantity, self.supplier))
                print(f"| Order Placed: {self.reorder_quantity} units from {self.supplier} (Delivery in {delivery_time} days)", end=" ")
                order_placed = True

            print()
            yield self.env.timeout(1)

    def receive_pending_orders(self):
        """Receive orders that are due today"""
        new_pending_orders = []
        for arrival_day, quantity, supplier_name in self.pending_orders:
            if self.env.now >= arrival_day:
                self.store.receive_order(quantity, supplier_name)
                print(f"Day {self.env.now}: Order of {quantity} units received from {supplier_name}. New Inventory = {self.store.inventory}", end=" ")
            else:
                new_pending_orders.append((arrival_day, quantity, supplier_name))

        self.pending_orders = new_pending_orders
