import sys
from helper import *

def main():
    if len(sys.argv) > 1:
        k = 1
        while k < len(sys.argv):
            if sys.argv[k] == 'ApsFile':
                ApsFile = sys.argv[k+1]
            elif sys.argv[k] == 'WallsFile':
                WallsFile = sys.argv[k+1]
            else:
                print("Program must be called with both a ApsFile and a WallsFile")
                exit()
            k+=2
    else:
        WallsFile = 'testWallsFile.txt'
        ApsFile = 'testApsFile.txt'

    walls = genWallsFromFile(WallsFile)
    APs = getAPsFromFile(ApsFile)
    plot(runSim(APs,walls),walls)

if __name__ == '__main__':
    main()