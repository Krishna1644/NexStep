import simpy
import numpy as np
import pandas as pd
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

# --------------------------
# Simulation Parameters
# --------------------------
SIMULATION_DAYS = 100
SELLING_PRICE_PER_UNIT = 50  # Revenue per unit sold
HOLDING_COST_PER_UNIT = 0.5  # Cost per unit stored per day
STOCKOUT_PENALTY_PER_UNIT = 10  # Penalty for unfulfilled demand

# Prepare CSV logging
csv_data = []

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
        supplier_name = store.supplier_history[-1] if store.supplier_history else "None"
        order_quantity = store.order_history[-1] if store.order_history else 0

        total_holding_cost += daily_holding_cost
        total_stockout_cost += daily_stockout_cost
        total_revenue += daily_revenue

        total_costs = total_supplier_cost + total_holding_cost + total_stockout_cost
        profit = total_revenue - total_costs
        roi = (profit / total_costs) * 100 if total_costs > 0 else 0

        csv_data.append([
            day, store.inventory, demand_data[day], store.demand_history[-1] if store.demand_history else 0,
            store.stockouts, supplier_name, order_quantity, f"{daily_holding_cost:.2f}",
            f"{daily_stockout_cost:.2f}", f"{total_supplier_cost:.2f}", f"{daily_revenue:.2f}",
            f"{profit:.2f}", f"{roi:.2f}"
        ])

    # Append labeled Data Generation parameters to CSV
    csv_data.append(["# Data Generation Specifications"])
    csv_data.append(["SEASONALITY_FACTOR", SEASONALITY_FACTOR])
    csv_data.append(["TREND_FACTOR", TREND_FACTOR])
    csv_data.append(["VOLATILITY", VOLATILITY])
    csv_data.append(["SHOCK_PROBABILITY", SHOCK_PROBABILITY])
    csv_data.append(["SEED", SEED])

    # Convert and save CSV
    df = pd.DataFrame(csv_data)
    df.to_csv("simulation_results.csv", index=False, header=[
        "Day", "Inventory", "Demand", "Fulfilled", "Stockouts", "Supplier",
        "Order Quantity", "Holding Cost", "Stockout Cost", "Supplier Cost",
        "Revenue", "Profit", "ROI"
    ])

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
    data_generator = DataGenerator(sim_days=SIMULATION_DAYS, seasonality_factor=SEASONALITY_FACTOR,
                                   trend_factor=TREND_FACTOR, volatility=VOLATILITY, 
                                   shock_prob=SHOCK_PROBABILITY, seed=SEED)
    shared_demand_data = data_generator.generate_demand_data()

    print("\n=== Fixed Order Model ===")
    run_simulation(FixedOrderSupplyChain, "Fixed_Model", shared_demand_data)

    # DO NOT UNCOMMENT
    """
    print("\n=== Optimized ML Model ===")
    run_simulation(OptimizedMLSupplyChain, "Optimized_Model_ML", shared_demand_data)
    """
