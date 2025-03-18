import simpy
from data_generator import DataGenerator
from Store import Store
from supplier import Supplier
from fixed_order_supply_chain import FixedOrderSupplyChain
from optimized_ml_supply_chain import OptimizedMLSupplyChain

# --------------------------
# Data Generation Parameters
# --------------------------
SEASONALITY_FACTOR = 5  # Amplitude of seasonal demand variations (higher value = stronger fluctuations)
TREND_FACTOR = 0.05  # Rate of long-term demand increase (+) or decrease (-) per day
VOLATILITY = 5  # Standard deviation of random daily demand fluctuations (higher value = more randomness)
SHOCK_PROBABILITY = 0.15  # Probability (0-1) of an unexpected demand spike or drop on a given day
SEED = 1  # Fixed random seed for reproducibility; set to None for different results each run

"""
Parameters:
- SEASONALITY_FACTOR: Defines the amplitude of cyclical fluctuations in demand, simulating seasonal trends.
  Measured in demand units, where higher values cause stronger up-and-down variations.

- TREND_FACTOR: Represents the long-term change in demand per day. A positive value means growing demand,
  while a negative value indicates declining demand. Measured in demand units per day.

- VOLATILITY: Controls the randomness in daily demand, acting as the standard deviation of demand noise.
  Measured in demand units, where higher values lead to more unpredictable demand shifts.

- SHOCK_PROBABILITY: The likelihood (0 to 1) that a significant market event occurs, causing a demand spike
  or drop. Higher values increase the chance of extreme variations.

- SEED: A fixed number that ensures the same random values are generated across runs for reproducibility.
  If set to None, demand will vary with each execution.
"""

# --------------------------
# Simulation Parameters
# --------------------------
SIMULATION_DAYS = 100
SELLING_PRICE_PER_UNIT = 50  # Revenue per unit sold
HOLDING_COST_PER_UNIT = 0.5  # Cost per unit stored per day
STOCKOUT_PENALTY_PER_UNIT = 10  # Penalty for unfulfilled demand

# --------------------------
# Simulation Runner
# --------------------------

def run_simulation(supply_chain_class, test_name, demand_data):
    env = simpy.Environment()
    store = Store()
    total_supplier_cost = 0
    total_holding_cost = 0
    total_stockout_cost = 0
    total_revenue = 0

    # Define suppliers
    suppliers = [
        Supplier("Cheap", reliability=0.6, cost_multiplier=0.8, delivery_time_range=(7, 10), per_unit_price=15, shipping_cost=100),
        Supplier("Normal", reliability=0.85, cost_multiplier=1.0, delivery_time_range=(4, 7), per_unit_price=20, shipping_cost=80),
        Supplier("Premium", reliability=0.95, cost_multiplier=1.3, delivery_time_range=(2, 5), per_unit_price=25, shipping_cost=50),
        Supplier("Expedited", reliability=1.0, cost_multiplier=2.0, delivery_time_range=(1, 2), per_unit_price=40, shipping_cost=200) 
    ]
  

    if "Fixed" in test_name:
            fixed_supplier = next(s for s in suppliers if s.name == "Normal")
            supply_chain = supply_chain_class(env, store, fixed_supplier, demand_data) 
    else:
        supply_chain = supply_chain_class(env, store, suppliers, demand_data)  


    for day in range(len(demand_data)):
        env.run(until=day + 1)
        
        daily_holding_cost = store.inventory * HOLDING_COST_PER_UNIT
        daily_stockout_cost = store.stockouts * STOCKOUT_PENALTY_PER_UNIT
        daily_revenue = sum(store.demand_history) * SELLING_PRICE_PER_UNIT
        
        total_holding_cost += daily_holding_cost
        total_stockout_cost += daily_stockout_cost
        total_revenue += daily_revenue

    total_costs = total_supplier_cost + total_holding_cost + total_stockout_cost
    profit = total_revenue - total_costs
    roi = (profit / total_costs) * 100 if total_costs > 0 else 0

    print(f"\n=== Test Case: {test_name} ===")
    print(f"Final Inventory: {store.inventory}")
    print(f"Stockouts: {store.stockouts}")
    print(f"Orders Placed: {len(store.order_history)}")
    print(f"Supplier Selection: {store.supplier_history}")
    print(f"Total Revenue: ${total_revenue:.2f}")
    print(f"Total Costs: ${total_costs:.2f}")
    print(f"Profit: ${profit:.2f}")
    print(f"ROI: {roi:.2f}%")

if __name__ == "__main__":
    # Generate shared demand data with improved seasonality, trend, and shocks
    data_generator = DataGenerator(sim_days=SIMULATION_DAYS, seasonality_factor=SEASONALITY_FACTOR, trend_factor=TREND_FACTOR, volatility=VOLATILITY, shock_prob=SHOCK_PROBABILITY, seed=SEED)
    shared_demand_data = data_generator.generate_demand_data()

    print("\n=== Fixed Order Model ===")
    run_simulation(FixedOrderSupplyChain, "Fixed_Model", shared_demand_data)

    #For Future. DO NO UNCOMMENT
"""
    print("\n=== Optimized ML Model ===")
    run_simulation(OptimizedMLSupplyChain, "Optimized_Model_ML", shared_demand_data)
"""
