import numpy as np
import simpy
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

MISSED_REVENUE_THRESHOLD = 5000  
PENALTY_MULTIPLIER = 150  
ORDER_SCALING_FACTOR = 1.2  
SAFETY_STOCK_MULTIPLIER = 6  
EMERGENCY_ORDER_THRESHOLD = 0.2  
EMERGENCY_ORDER_SIZE = 50  

class OptimizedMLSupplyChain:
    """
    Machine-learning-driven supply chain optimization model that selects the 
    best supplier dynamically based on cost, reliability, and delivery time.
    Uses emergency orders for critical stockouts and adjusts order sizes based on demand patterns.
    """

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
        self.missed_revenue = 0  
        self.env.process(self.run())

        self.emergency_supplier = next(s for s in self.suppliers if s.name == "Expedited")

    def run(self):
        for day in range(len(self.demand_data)):
            print(f"Day {day}: Inventory = {self.store.inventory}", end=" ")

            demand = self.demand_data[day]
            fulfilled = self.store.fulfill_demand(demand)
            missed = demand - fulfilled
            print(f"| Demand: {demand}, Fulfilled: {fulfilled}", end=" ")

            self.missed_revenue += missed * 50  

            self.receive_pending_orders()

            if len(self.store.demand_history) >= self.lookback:
                avg_demand = sum(self.store.demand_history[-self.lookback:]) / self.lookback
                depletion_rate = (self.store.demand_history[-1] - self.store.demand_history[0]) / self.lookback
                reorder_threshold = avg_demand * SAFETY_STOCK_MULTIPLIER + depletion_rate * 3  

                if self.store.inventory < (reorder_threshold * EMERGENCY_ORDER_THRESHOLD) and len(self.pending_orders) == 0:
                    emergency_order_cost = self.emergency_supplier.get_cost(EMERGENCY_ORDER_SIZE) + self.emergency_supplier.shipping_cost
                    self.pending_orders.append((self.env.now + self.emergency_supplier.get_delivery_time(), EMERGENCY_ORDER_SIZE, self.emergency_supplier))
                    print(f"| Emergency Order Placed: {EMERGENCY_ORDER_SIZE} units from {self.emergency_supplier.name} (Delivery in 1-2 days)", end=" ")

                if self.store.inventory < reorder_threshold and (day - self.last_order_day) > 7 and len(self.pending_orders) == 0:
                    
                    if len(self.training_data) > 10:
                        df = pd.DataFrame(self.training_data, columns=['AvgDemand', 'Reliability', 'CostMultiplier', 'DeliveryTime', 'Delay'])
                        X = df[['AvgDemand', 'Reliability', 'CostMultiplier', 'DeliveryTime']]
                        y = df['Delay']
                        self.ml_model.fit(X, y)

                        supplier_scores = {}
                        for supplier in self.suppliers:
                            if supplier.name == "Expedited":
                                continue  
                            X_pred = pd.DataFrame([[avg_demand, supplier.reliability, supplier.cost_multiplier, np.mean(supplier.delivery_time_range)]], 
                                                  columns=['AvgDemand', 'Reliability', 'CostMultiplier', 'DeliveryTime'])
                            predicted_delay = self.ml_model.predict(X_pred)[0]
                            total_cost = (supplier.get_cost(100) + supplier.shipping_cost + (predicted_delay ** 2) * PENALTY_MULTIPLIER)
                            supplier_scores[supplier.name] = total_cost

                        best_supplier_name = min(supplier_scores, key=supplier_scores.get)
                        supplier = next(s for s in self.suppliers if s.name == best_supplier_name)
                    else:
                        supplier = min((s for s in self.suppliers if s.name != "Expedited"), key=lambda s: min(s.delivery_time_range))

                    order_quantity = max(int(avg_demand * 5), 100)
                    if self.missed_revenue > MISSED_REVENUE_THRESHOLD:
                        order_quantity = int(order_quantity * ORDER_SCALING_FACTOR)

                    delivery_time = supplier.get_delivery_time()
                    order_cost = supplier.get_cost(order_quantity) + supplier.shipping_cost
                    self.pending_orders.append((self.env.now + delivery_time, order_quantity, supplier))

                    print(f"| Order Placed: {order_quantity} units from {supplier.name} (Delivery in {delivery_time} days)", end=" ")
                    self.last_order_day = day  

                    self.training_data.append([avg_demand, supplier.reliability, supplier.cost_multiplier, np.mean(supplier.delivery_time_range), delivery_time])

            print()
            yield self.env.timeout(1)

    def receive_pending_orders(self):
        new_pending_orders = []
        for arrival_day, quantity, supplier in self.pending_orders:
            if self.env.now >= arrival_day:
                self.store.receive_order(quantity, supplier.name)
                print(f"| Order of {quantity} units received from {supplier.name}. New Inventory = {self.store.inventory}", end=" ")
            else:
                new_pending_orders.append((arrival_day, quantity, supplier))

        self.pending_orders = new_pending_orders
