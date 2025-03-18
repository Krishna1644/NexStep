import numpy as np
import simpy
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

class OptimizedMLSupplyChain:
    def __init__(self, env, store, suppliers, demand_data, lookback=5):
        self.env = env
        self.store = store
        self.suppliers = suppliers
        self.demand_data = demand_data
        self.lookback = lookback
        self.training_data = []
        self.ml_model = RandomForestRegressor(n_estimators=10)
        self.pending_orders = []
        self.last_order_day = -10
        self.env.process(self.run())

    def run(self):
        for day in range(len(self.demand_data)):
            print(f"Day {day}: Inventory = {self.store.inventory}", end=" ")

            demand = self.demand_data[day]
            fulfilled = self.store.fulfill_demand(demand)
            print(f"| Demand: {demand}, Fulfilled: {fulfilled}", end=" ")

            self.receive_pending_orders()

            if len(self.store.demand_history) >= self.lookback:
                avg_demand = sum(self.store.demand_history[-self.lookback:]) / self.lookback
                reorder_threshold = avg_demand * 4  

                if self.store.inventory < reorder_threshold and (day - self.last_order_day) > 7:
                    best_supplier = np.random.choice(self.suppliers).name
                    supplier = next(s for s in self.suppliers if s.name == best_supplier)
                    order_quantity = max(int(avg_demand * 5), 100)  
                    delivery_time = supplier.get_delivery_time()
                    self.pending_orders.append((self.env.now + delivery_time, order_quantity, supplier.name))

                    print(f"| Order Placed: {order_quantity} units from {supplier.name} (Delivery in {delivery_time} days)", end=" ")
                    self.last_order_day = day  

            print()
            yield self.env.timeout(1)

    def receive_pending_orders(self):
        new_pending_orders = []
        for arrival_day, quantity, supplier_name in self.pending_orders:
            if self.env.now >= arrival_day:
                self.store.receive_order(quantity, supplier_name)
                print(f"Day {self.env.now}: Order of {quantity} units received from {supplier_name}. New Inventory = {self.store.inventory}", end=" ")
            else:
                new_pending_orders.append((arrival_day, quantity, supplier_name))

        self.pending_orders = new_pending_orders
