from helper import *

walls = genWallsFromFile(None)
APs = getAPsFromFile(None)

plot(runSim(APs,walls),walls)