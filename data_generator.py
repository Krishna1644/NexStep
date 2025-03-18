import numpy as np

class DataGenerator:
    """
    Generates realistic demand data for a supply chain simulation.
    
    Parameetrs:
        sim_days (int): Number of days to simulate.
        seasonality_factor (float): Strength of seasonal demand fluctuations.
        trend_factor (float): Linear increase (+) or decrease (-) in demand over time.
        volatility (float): Standard deviation of random noise in demand.
        shock_prob (float): Probability of a sudden demand spike or drop.
        seed (int, optional): Random seed for reproducibility.
    """

    def __init__(self, sim_days=100, seasonality_factor=5, trend_factor=0, volatility=3, shock_prob=0.1, seed=None):
        self.sim_days = sim_days
        self.seasonality_factor = seasonality_factor
        self.trend_factor = trend_factor
        self.volatility = volatility
        self.shock_prob = shock_prob
        if seed is not None:
            np.random.seed(seed)

    
    #Calculates daily demand with seasonality, noise, trend, and occasional shocks.
    def seasonal_demand(self, day):
        base_demand = 10 + self.seasonality_factor * np.sin(2 * np.pi * day / np.random.randint(25, 35))
        noise = np.random.normal(0, self.volatility)
        trend = self.trend_factor * day
        shock = np.random.choice([-1, 1]) * np.random.randint(10, 30) if np.random.rand() < self.shock_prob else 0
        return max(0, int(base_demand + noise + trend + shock))

    
    #Generates a list of daily demand values based on configured parameters.
    def generate_demand_data(self):
        return [self.seasonal_demand(day) for day in range(self.sim_days)]
