import numpy as np

class Supplier:
    def __init__(self, name, reliability, cost_multiplier, delivery_time_range):
        self.name = name
        self.reliability = reliability
        self.cost_multiplier = cost_multiplier
        self.delivery_time_range = delivery_time_range

    def get_delivery_time(self):
        """Returns delivery time based on reliability"""
        if np.random.rand() < self.reliability:
            return np.random.randint(self.delivery_time_range[0], self.delivery_time_range[1] + 1)
        else:
            return np.random.randint(self.delivery_time_range[0] + 2, self.delivery_time_range[1] + 5)

    def get_cost(self, order_quantity):
        """Returns cost based on order size and cost multiplier"""
        return 20 * self.cost_multiplier * (0.9 if order_quantity >= 100 else 1)
