import csv
import numpy as np
import simpy

REORDER_POINT = 50  # Inventory level at which an order is triggered
ORDER_QUANTITY = 100  # Number of units ordered each time
SELLING_PRICE_PER_UNIT = 50
HOLDING_COST_PER_UNIT = 0.5
STOCKOUT_PENALTY_PER_UNIT = 10

class FixedOrderSupplyChain:
    """
    Implements a fixed-order supply chain model with accurate financial tracking
    and real-time CSV export for easier graphing and analysis.
    """
    def __init__(self, env, store, supplier, demand_data, csv_filename="fixed_order_simulation.csv"):
        self.env = env
        self.store = store
        self.supplier = supplier
        self.demand_data = demand_data
        self.reorder_threshold = REORDER_POINT
        self.reorder_quantity = ORDER_QUANTITY
        self.pending_orders = []
        
        self.total_supplier_cost = 0
        self.total_holding_costs = 0
        self.total_stockout_costs = 0
        self.total_revenue = 0
        self.total_costs = 0
        
        self.csv_filename = csv_filename
        
        # Initialize CSV logging
        self.init_csv()
        
        self.env.process(self.run())

    def init_csv(self):
        """Initialize CSV file with headers."""
        with open(self.csv_filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                "Day", "Inventory", "Demand", "Fulfilled", "Stockouts", "Order Quantity", 
                "Supplier", "Holding Cost", "Stockout Cost", "Supplier Cost", "Revenue", "Profit", "ROI"
            ])

    def run(self):
        for day in range(len(self.demand_data)):
            print(f"Day {day}: Inventory = {self.store.inventory}", end=" ")
            
            demand = self.demand_data[day]
            fulfilled = self.store.fulfill_demand(demand)
            print(f"| Demand: {demand}, Fulfilled: {fulfilled}", end=" ")
            
            daily_holding_cost = self.store.inventory * HOLDING_COST_PER_UNIT
            daily_stockout_cost = (demand - fulfilled) * STOCKOUT_PENALTY_PER_UNIT if fulfilled < demand else 0
            
            self.total_holding_costs += daily_holding_cost
            self.total_stockout_costs += daily_stockout_cost
            
            revenue = fulfilled * SELLING_PRICE_PER_UNIT
            self.total_revenue += revenue
            
            self.receive_pending_orders()
            
            order_quantity = 0
            supplier_name = "None"
            order_cost = 0 
            
            if self.store.inventory < self.reorder_threshold and len(self.pending_orders) == 0:
                delivery_time = np.random.randint(4, 7)
                order_quantity = self.reorder_quantity
                order_cost = self.supplier.get_cost(order_quantity)
                self.total_supplier_cost += order_cost
                self.pending_orders.append((self.env.now + delivery_time, order_quantity, self.supplier.name))
                supplier_name = self.supplier.name
                print(f"| Order Placed: {order_quantity} units from {supplier_name} (Delivery in {delivery_time} days)", end=" ")
            
            today_costs = order_cost + daily_holding_cost + daily_stockout_cost
            self.total_costs += today_costs
            profit = revenue - today_costs
            roi = (profit / today_costs) * 100 if today_costs > 0 else 0
            
            # Log data to CSV
            self.log_to_csv(day, self.store.inventory, demand, fulfilled, demand - fulfilled, order_quantity, 
                            supplier_name, daily_holding_cost, daily_stockout_cost, revenue, profit, roi)
            
            print()
            yield self.env.timeout(1)
        
        self.compute_final_roi()

    def receive_pending_orders(self):
        new_pending_orders = []
        for arrival_day, quantity, supplier_name in self.pending_orders:
            if self.env.now >= arrival_day:
                self.store.receive_order(quantity, supplier_name)
                print(f"Day {self.env.now}: Order of {quantity} units received from {supplier_name}. New Inventory = {self.store.inventory}", end=" ")
            else:
                new_pending_orders.append((arrival_day, quantity, supplier_name))
        self.pending_orders = new_pending_orders

    def log_to_csv(self, day, inventory, demand, fulfilled, stockouts, order_quantity, supplier_name, 
                   holding_cost, stockout_cost, revenue, profit, roi):
        """Logs the day's data to a CSV file for graphing later."""
        with open(self.csv_filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([day, inventory, demand, fulfilled, stockouts, order_quantity, supplier_name,
                             f"{holding_cost:.2f}", f"{stockout_cost:.2f}", f"{revenue:.2f}", 
                             f"{profit:.2f}", f"{roi:.2f}"])

    def compute_final_roi(self):
        """Calculates and prints final ROI metrics."""
        profit = self.total_revenue - self.total_costs
        roi = (profit / self.total_costs) * 100 if self.total_costs > 0 else 0
        
        print("\n=== Fixed Order Model Financial Summary ===")
        print(f"Total Revenue: ${self.total_revenue:.2f}")
        print(f"Total Supplier Cost: ${self.total_supplier_cost:.2f}")
        print(f"Total Holding Cost: ${self.total_holding_costs:.2f}")
        print(f"Total Stockout Cost: ${self.total_stockout_costs:.2f}")
        print(f"Total Costs: ${self.total_costs:.2f}")
        print(f"ROI: {roi:.2f}%")
        
        print("\n=== FINAL SIMULATION RESULTS ===")
        print(f"Total Revenue: ${self.total_revenue:.2f}")
        print(f"Total Costs: ${self.total_costs:.2f}")
        print(f"Profit: ${profit:.2f}")
        print(f"Final ROI: {roi:.2f}%")
