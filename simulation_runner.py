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
SEASONALITY_FACTOR = 5
TREND_FACTOR = 0.05
VOLATILITY = 5
SHOCK_PROBABILITY = 0.15
SEED = 1

# --------------------------
# Simulation Parameters
# --------------------------
SIMULATION_DAYS = 100
CSV_FILENAME = "simulation_results.csv"

def run_simulation(supply_chain_class, test_name, demand_data, csv_filename):
    """Runs the supply chain simulation and logs results to a CSV file."""
    env = simpy.Environment()
    store = Store()
    suppliers = [
        Supplier("Cheap", reliability=0.6, cost_multiplier=0.8, delivery_time_range=(7, 10), per_unit_price=15, shipping_cost=100),
        Supplier("Normal", reliability=0.85, cost_multiplier=1.0, delivery_time_range=(4, 7), per_unit_price=20, shipping_cost=80),
        Supplier("Premium", reliability=0.95, cost_multiplier=1.3, delivery_time_range=(2, 5), per_unit_price=25, shipping_cost=50),
        Supplier("Expedited", reliability=1.0, cost_multiplier=2.0, delivery_time_range=(1, 2), per_unit_price=40, shipping_cost=200)
    ]
    
    if "Fixed" in test_name:
        fixed_supplier = next(s for s in suppliers if s.name == "Normal")
        supply_chain = supply_chain_class(env, store, fixed_supplier, demand_data, csv_filename)
    else:
        supply_chain = supply_chain_class(env, store, suppliers, demand_data, csv_filename)
    
    # Run the simulation
    env.run(until=SIMULATION_DAYS)
    
    print(f"\n=== Test Case: {test_name} ===")
    print(f"Final Inventory: {store.inventory}")
    print(f"Stockouts: {store.stockouts}")
    print(f"Orders Placed: {len(store.order_history)}")
    print(f"Supplier Selection: {store.supplier_history}")
    
    df = pd.read_csv(csv_filename)
    df.to_csv(csv_filename, index=False)
    print(f"Simulation results saved to {csv_filename}")
    
    total_revenue = supply_chain.total_revenue
    total_costs = supply_chain.total_supplier_cost + supply_chain.total_holding_costs + supply_chain.total_stockout_costs
    profit = total_revenue - total_costs
    roi = (profit / total_costs) * 100 if total_costs > 0 else 0
    
    print("\n=== FINAL SIMULATION RESULTS ===")
    print(f"Total Revenue: ${total_revenue:.2f}")
    print(f"Total Costs: ${total_costs:.2f}")
    print(f"Profit: ${profit:.2f}")
    print(f"Final ROI: {roi:.2f}%")

if __name__ == "__main__":
    data_generator = DataGenerator(sim_days=SIMULATION_DAYS, seasonality_factor=SEASONALITY_FACTOR,
                                   trend_factor=TREND_FACTOR, volatility=VOLATILITY, 
                                   shock_prob=SHOCK_PROBABILITY, seed=SEED)
    shared_demand_data = data_generator.generate_demand_data()

        
    print("\n=== Running Fixed Order Model ===")
    run_simulation(FixedOrderSupplyChain, "Fixed_Model", shared_demand_data, CSV_FILENAME)
    """
    # Do Not Uncomment
    print("\n=== Running Optimized ML Model ===")
    run_simulation(OptimizedMLSupplyChain, "Optimized_Model_ML", shared_demand_data, "optimized_ml_results.csv")"""
    