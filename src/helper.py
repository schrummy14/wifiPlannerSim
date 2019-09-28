import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt
from shapely.geometry import LineString

def mat2dB(mat): # From https://eyesaas.com/wifi-signal-loss/
    dBmatList = {
        'drywall'           :   0.01,
        'glass'             :   0.07,
        'wooden'            :   3.27,
        'brick'             :  15.28,
        'concrete (102 mm)' :  26.00
    }
    return dBmatList[mat]

def mat2color(mat):
    colorMatList = {
        'drywall'           :  'y',
        'glass'             :  'b',
        'wooden'            :  'g',
        'brick'             :  'b',
        'concrete (102 mm)' :  'k'
    }
    return colorMatList[mat]

def genWallsFromFile(WallFileName):
    walls = []
    walls.append([ 0.0,  0.0, 10.0,  0.0, 'concrete (102 mm)'])
    walls.append([10.0,  0.0, 10.0, 10.0, 'concrete (102 mm)'])
    walls.append([10.0, 10.0,  0.0, 10.0, 'concrete (102 mm)'])
    walls.append([ 0.0, 10.0,  0.0,  0.0, 'concrete (102 mm)'])
    walls.append([ 0.0,  8.0,  5.0,  8.0, 'wooden'])
    walls.append([ 5.0,  8.0,  5.0,  6.0, 'wooden'])
    walls.append([ 5.0,  6.0,  3.0,  6.0, 'glass'])
    walls.append([ 3.0,  6.0,  3.0,  4.0, 'wooden'])
    walls.append([ 3.0,  4.0,  0.0,  4.0, 'drywall'])
    walls.append([ 9.0,  3.0,  7.0,  3.0, 'drywall'])
    walls.append([ 7.0,  3.0,  7.0,  8.0, 'drywall'])
    walls.append([ 7.0,  8.0, 10.0,  8.0, 'drywall'])
    return walls

def getAPsFromFile(ApFileName):
    APs = []
    APs.append([ 5.00,  5.00, 5.0])
    APs.append([ 0.00,  0.00, 5.0])
    APs.append([10.00,  0.00, 5.0])
    APs.append([10.00, 10.00, 5.0])
    APs.append([ 0.00, 10.00, 5.0])
    return APs

def plot(data,walls):

    myPlot = plt.contourf(
        data[:,:,0], data[:,:,1], data[:,:,2],
        levels = 101)
    for wall in walls:
        plt.plot(
            [wall[0],wall[2]], [wall[1],wall[3]], 
            c = mat2color(wall[4]),
            linewidth = 5)
    plt.colorbar(myPlot)
    plt.clim(-10, 0)
    plt.show()

def runSim(Aps, Walls, numCells = 50, dx = 0.0, dy = 0.0):
    # Get max room dimensions (Assums square and min == 0)
    maxX = 0
    maxY = 0
    for wall in Walls:
        mX = max(wall[0:4:2])
        mY = max(wall[1:4:2])
        if mX > maxX:
            maxX = mX
        if mY > maxY:
            maxY = mY
    if dx == 0.0 or dy == 0.0:
        dx = maxX/numCells
        dy = maxY/numCells
        numCellsX = numCells
        numCellsY = numCells
    else:
        numCellsX = np.ceil(maxX/dx)
        numCellsY = np.ceil(maxY/dy)

    dx = maxX/numCellsX
    dy = maxY/numCellsY
    data = np.zeros([(numCellsY+1),(numCellsX+1),3]) - 100.0

    for ky in tqdm(range(numCellsY+1)):
        for kx in range(numCellsX+1):
            data[ky,kx,0] = kx*dx
            data[ky,kx,1] = ky*dy
            point = data[ky,kx,0:2]
            for Ap in Aps:
                rsq, vec = getMagSq(Ap, point)
                inTheWay = []
                reducePower = 0.0
                for wall in Walls:
                    d = dist2wall(Ap,point,wall,vec)
                    if d > 0:
                        reducePower += mat2dB(wall[4])

                newVal = max([-reducePower + -2*np.log(max([1.0,np.sqrt(rsq)])),data[ky,kx,2]])
                data[ky,kx,2] = newVal
    return data

def dist2wall(Ap,point,wall,vec):
    l1 = LineString([(Ap[0],Ap[1]), (point[0],point[1])])
    l2 = LineString([(wall[0],wall[1]),(wall[2],wall[3])])
    x = l1.intersection(l2)
    if x.is_empty:
        return 0
    l3 = LineString([(Ap[0],Ap[1]), x.coords[0]])
    if l1.length == l3.length:
        return 0
    return l3.length

def getMagSq(Ap, data):
    x = data[0]
    y = data[1]
    Ax = Ap[0]
    Ay = Ap[1]

    Axmx = Ax-x
    Aymy = Ay-y

    rsq = (Axmx)*(Axmx) + (Aymy)*(Aymy)
    if rsq == 0.0:
        return rsq, [0,0]
    vec = np.array([Axmx, Aymy])/np.sqrt(rsq)

    return rsq, vec
