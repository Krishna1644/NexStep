import simpy
from data_generator import DataGenerator
from Store import Store
from supplier import Supplier
from fixed_order_supply_chain import FixedOrderSupplyChain
from optimized_ml_supply_chain import OptimizedMLSupplyChain

# --------------------------
# Simulation Runner
# --------------------------

def run_simulation(supply_chain_class, test_name, demand_data):
    env = simpy.Environment()
    store = Store()

    # Define suppliers
    suppliers = [
        Supplier("Cheap", reliability=0.6, cost_multiplier=0.8, delivery_time_range=(7, 10)),
        Supplier("Normal", reliability=0.85, cost_multiplier=1.0, delivery_time_range=(4, 7)),
        Supplier("Premium", reliability=0.95, cost_multiplier=1.3, delivery_time_range=(2, 5))
    ]

    # Choose appropriate suppliers (for Fixed Order Model, always use "Normal")
    if "Fixed" in test_name:
        supply_chain = supply_chain_class(env, store, "Normal", demand_data)
    else:
        supply_chain = supply_chain_class(env, store, suppliers, demand_data)

    for time in range(len(demand_data)):
        env.run(until=time + 1)

    print(f"\n=== Test Case: {test_name} ===")
    print(f"Final Inventory: {store.inventory}")
    print(f"Stockouts: {store.stockouts}")
    print(f"Orders Placed: {len(store.order_history)}")
    print(f"Supplier Selection: {store.supplier_history}")


if __name__ == "__main__":
    # Generate shared demand data for both models
    data_generator = DataGenerator(sim_days=100)
    shared_demand_data = data_generator.generate_demand_data()

    print("\n=== Fixed Order Model ===")
    run_simulation(FixedOrderSupplyChain, "Fixed_Model", shared_demand_data)

    """
    print("\n=== Optimized ML Model ===")
    run_simulation(OptimizedMLSupplyChain, "Optimized_Model_ML", shared_demand_data)
    """