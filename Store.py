# ----------------------------
# Store Configuration Parameters
# ----------------------------
INITIAL_INVENTORY = 100  # Starting inventory level at the beginning of the simulation (units)
MAX_STORAGE_CAPACITY = 200  # Maximum inventory storage capacity (units)
HOLDING_COST_PER_UNIT = 0.5  # Cost of storing one unit of inventory per day ($ per unit per day)
STOCKOUT_PENALTY_PER_UNIT = 10  # Penalty cost incurred for each unit of unfulfilled demand ($ per unit)
SELLING_PRICE_PER_UNIT = 50  # Revenue generated for each unit sold ($ per unit)

class Store:
    def __init__(self):
        self.inventory = INITIAL_INVENTORY
        self.order_history = []
        self.demand_history = []
        self.supplier_history = []
        self.stockouts = 0
        self.total_holding_costs = 0
        self.total_stockout_costs = 0
        self.total_revenue = 0

    def receive_order(self, quantity, supplier_name):
        """Increase inventory when an order arrives"""
        self.inventory = min(self.inventory + quantity, MAX_STORAGE_CAPACITY)
        self.order_history.append(quantity)
        self.supplier_history.append(supplier_name)

    def fulfill_demand(self, demand):
        """Fulfill demand while tracking stockouts and revenue"""
        fulfilled = min(self.inventory, demand)
        self.inventory -= fulfilled
        self.demand_history.append(demand)
        if fulfilled < demand:
            self.stockouts += (demand - fulfilled)

        self.calculate_revenue(fulfilled)
        self.calculate_stockout_costs(demand, fulfilled)

        return fulfilled
    

    #Calculate daily holding costs based on current inventory
    def calculate_holding_costs(self):
        
        daily_cost = self.inventory * HOLDING_COST_PER_UNIT
        self.total_holding_costs += daily_cost
        return daily_cost
    
    #Calculate stockout penalty for unfulfilled demand
    def calculate_stockout_costs(self, demand, fulfilled):
        
        unfulfilled_demand = demand - fulfilled
        cost = unfulfilled_demand * STOCKOUT_PENALTY_PER_UNIT
        self.total_stockout_costs += cost
        return cost
    #Calculate revenue from fulfilled demand
    def calculate_revenue(self, fulfilled_units):
        
        revenue = fulfilled_units * SELLING_PRICE_PER_UNIT
        self.total_revenue += revenue
        return revenue
