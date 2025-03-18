import numpy as np
import simpy

REORDER_POINT = 50  # Inventory level at which an order is triggered
ORDER_QUANTITY = 100  # Number of units ordered each time

class FixedOrderSupplyChain:
    """
    Implements a fixed-order supply chain model where inventory is replenished
    when it falls below a set threshold. Tracks costs, revenue, and computes ROI.
    
    Attributes:
        env (simpy.Environment): Simulation environment.
        store (Store): Store instance tracking inventory and costs.
        supplier (Supplier): Supplier providing inventory replenishment.
        demand_data (list): Daily demand values for the simulation period.
    """
    def __init__(self, env, store, supplier, demand_data):
        self.env = env
        self.store = store
        self.supplier = supplier
        self.demand_data = demand_data
        self.reorder_threshold = REORDER_POINT
        self.reorder_quantity = ORDER_QUANTITY
        self.pending_orders = []
        self.total_supplier_cost = 0
        self.env.process(self.run())

    def run(self):
        for day in range(len(self.demand_data)):
            print(f"Day {day}: Inventory = {self.store.inventory}", end=" ")

            demand = self.demand_data[day]
            fulfilled = self.store.fulfill_demand(demand)
            print(f"| Demand: {demand}, Fulfilled: {fulfilled}", end=" ")

            daily_holding_cost = self.store.calculate_holding_costs()
            daily_stockout_cost = self.store.calculate_stockout_costs(demand, fulfilled)

            self.receive_pending_orders()

            if self.store.inventory < self.reorder_threshold and len(self.pending_orders) == 0:
                delivery_time = np.random.randint(4, 7)
                order_cost = self.supplier.get_cost(self.reorder_quantity) 
                self.total_supplier_cost += order_cost
                self.pending_orders.append((self.env.now + delivery_time, self.reorder_quantity, self.supplier.name))
                print(f"| Order Placed: {self.reorder_quantity} units from {self.supplier.name} (Delivery in {delivery_time} days)", end=" ")

            print()
            yield self.env.timeout(1)

        self.compute_final_roi()
    
    #Receive orders that are due today
    def receive_pending_orders(self):
        new_pending_orders = []
        for arrival_day, quantity, supplier_name in self.pending_orders:
            if self.env.now >= arrival_day:
                self.store.receive_order(quantity, supplier_name)
                print(f"Day {self.env.now}: Order of {quantity} units received from {supplier_name}. New Inventory = {self.store.inventory}", end=" ")
            else:
                new_pending_orders.append((arrival_day, quantity, supplier_name))

        self.pending_orders = new_pending_orders

    #Calculate and print final ROI metrics
    def compute_final_roi(self):
        
        total_costs = self.total_supplier_cost + self.store.total_holding_costs + self.store.total_stockout_costs
        total_revenue = self.store.total_revenue
        profit = total_revenue - total_costs
        roi = (profit / total_costs) * 100 if total_costs > 0 else 0

        print("\n=== Fixed Order Model Financial Summary ===")
        print(f"Total Revenue: ${total_revenue:.2f}")
        print(f"Total Supplier Cost: ${self.total_supplier_cost:.2f}")
        print(f"Total Holding Cost: ${self.store.total_holding_costs:.2f}")
        print(f"Total Stockout Cost: ${self.store.total_stockout_costs:.2f}")
        print(f"Total Costs: ${total_costs:.2f}")
        print(f"Profit: ${profit:.2f}")
        print(f"ROI: {roi:.2f}%")
