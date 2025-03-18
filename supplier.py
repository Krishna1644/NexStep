import numpy as np

class Supplier:
    """
    Represents a supplier in the supply chain, defining their reliability, delivery time,
    cost structure, and pricing model. The supplier determines delivery time based on 
    reliability and calculates the total cost of an order, including per-unit price, 
    cost multiplier, bulk discounts, and shipping costs.
    """

    def __init__(self, name, reliability, cost_multiplier, delivery_time_range, per_unit_price, shipping_cost):
        self.name = name
        self.reliability = reliability
        self.cost_multiplier = cost_multiplier
        self.delivery_time_range = delivery_time_range
        self.per_unit_price = per_unit_price  
        self.shipping_cost = shipping_cost  


    #Determines delivery time based on supplier reliability.
    def get_delivery_time(self):
        
        if np.random.rand() < self.reliability:
            return np.random.randint(self.delivery_time_range[0], self.delivery_time_range[1] + 1)
        else:
            return np.random.randint(self.delivery_time_range[0] + 2, self.delivery_time_range[1] + 5)
        
        
        
    #Calculates total cost, including bulk discounts and shipping fees.
    def get_cost(self, order_quantity):
        
        base_cost = order_quantity * self.per_unit_price * self.cost_multiplier
        discount = 0.9 if order_quantity >= 100 else 1  
        total_cost = (base_cost * discount) + self.shipping_cost
        return total_cost
