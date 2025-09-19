import live
import sys
import os
sys.path.append('src')
from synthopt.device import *
import time

serum = DeviceOptimizer('Serum')
while True:
    serum.refresh_params()
    os.system("clear")  
    for param,value in serum.get_params().items(): 
        print(param,':',value[-1])
    time.sleep(0.3)