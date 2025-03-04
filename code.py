import simpy
import numpy as np
import pandas as pd

# Simulation Parameters
SIMULATION_DAYS = 100
INITIAL_INVENTORY = 50
REORDER_POINT = 20
ORDER_QUANTITY = 50

LEAD_TIME = 5  
DELIVERY_TIME = 5
DISRUPTION_PROBABILITY = 0.05
DISRUPTION_EXTRA_DELAY = (2, 5)

HOLDING_COST_PER_UNIT = 1
STOCKOUT_COST_PER_UNIT = 5
ORDERING_COST = 20

DEMAND_MEAN = 10
DEMAND_STD = 3

class SupplyChain:
    def __init__(self, env):
        self.env = env
        self.inventory = INITIAL_INVENTORY
        self.pending_orders = []

        self.total_holding_cost = 0
        self.total_stockout_cost = 0
        self.total_ordering_cost = 0
        self.daily_data = []

        # Start simulation processes
        self.env.process(self.customer_demand())
        self.env.process(self.inventory_management())

    def customer_demand(self):
        """Simulates daily customer demand affecting inventory."""
        while True:
            customer_demand = max(0, int(np.random.normal(DEMAND_MEAN, DEMAND_STD)))

            if self.inventory >= customer_demand:
                self.inventory -= customer_demand
                lost_sales = 0
            else:
                lost_sales = customer_demand - self.inventory
                self.inventory = 0  # Stockout occurs

            # Track costs
            holding_cost = self.inventory * HOLDING_COST_PER_UNIT
            stockout_cost = lost_sales * STOCKOUT_COST_PER_UNIT
            self.total_holding_cost += holding_cost
            self.total_stockout_cost += stockout_cost

            self.daily_data.append([
                self.env.now, customer_demand, self.inventory, lost_sales,
                holding_cost, stockout_cost, self.total_ordering_cost
            ])

            yield self.env.timeout(1)  # Wait for the next day

    def inventory_management(self):
        """Monitors inventory and places orders when stock is low."""
        while True:
            if self.inventory < REORDER_POINT:
                delay = LEAD_TIME + DELIVERY_TIME
                
                # Possible disruption
                if np.random.rand() < DISRUPTION_PROBABILITY:
                    delay += np.random.randint(DISRUPTION_EXTRA_DELAY[0], DISRUPTION_EXTRA_DELAY[1] + 1)

                self.pending_orders.append((self.env.now, ORDER_QUANTITY, self.env.now + delay))
                self.total_ordering_cost += ORDERING_COST
                print(f'Day {self.env.now}: Order placed, arriving in {delay} days')

                # Process the order arrival event
                self.env.process(self.receive_order(delay, ORDER_QUANTITY))

            yield self.env.timeout(1)  # Check inventory daily

    def receive_order(self, delay, quantity):
        """Handles order arrivals after lead time."""
        yield self.env.timeout(delay)
        self.inventory += quantity
        print(f'Day {self.env.now}: Order received, new inventory = {self.inventory}')

# Run the simulation
env = simpy.Environment()
supply_chain = SupplyChain(env)
env.run(until=SIMULATION_DAYS)

# Convert data to DataFrame
columns = ["Day", "Customer Demand", "Inventory Level", "Lost Sales", "Holding Cost", "Stockout Cost", "Total Ordering Cost"]
df = pd.DataFrame(supply_chain.daily_data, columns=columns)

# Save the results
df.to_csv("supply_chain_simpy_simulation.csv", index=False)
print("Simulation complete. Data saved to 'supply_chain_simpy_simulation.csv'.")
