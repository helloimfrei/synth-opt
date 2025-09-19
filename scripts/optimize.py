import sys
sys.path.append('src')

import os
from synthopt.device import DeviceOptimizer
serum = DeviceOptimizer("Serum")


while True: 
    params = serum.ask() 
    print(params) 
    serum.set_params(params) 
    print(serum.get_params()) 
    serum.push_params() 
    score = input("How did you like the sound? (0-100): ") 
    serum.tell(score)