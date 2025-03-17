import simpy
import numpy as np
import pandas as pd

# Runs Simpy to simulate the supply chain
class SupplyChain:
    def __init__(self, env):
        
        self.env = env

        self.env.process(self.place_order(5))


    def place_order(self,quantity):
        while(True):
             
            print("Order Placed = " + str(quantity))
            yield self.env.timeout(1)

    
# represets a store
class Store():
    def __init__(self):
            self.inventory = 1
    



if __name__ == "__main__":
    Wegmens = Store()
    print(Wegmens.inventory)

    #Runs the simulation
    env = simpy.Environment()
    supply_chain = SupplyChain(env)
    env.run(until=5)