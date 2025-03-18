import numpy as np

class DataGenerator:
    def __init__(self, sim_days=100, seasonality_factor=5):
        self.sim_days = sim_days
        self.seasonality_factor = seasonality_factor

    def seasonal_demand(self, day):
        """Generate seasonal demand with noise"""
        base_demand = 10 + self.seasonality_factor * np.sin(2 * np.pi * day / 30)
        noise = np.random.normal(0, 3)
        return max(0, int(base_demand + noise))

    def generate_demand_data(self):
        """Creates a list of daily demand values"""
        return [self.seasonal_demand(day) for day in range(self.sim_days)]
