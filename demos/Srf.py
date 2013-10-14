# Demonstration of a surface

import numpy as np
from Nurbs import Srf, Crv

cntrl = np.zeros((4,4,4), np.float)
for u in range(4):
    for v in range(4):
        cntrl[0][u][v] = 2.*(u - 1.5)
        cntrl[1][u][v] = 2.*(v - 1.5)
        if (u == 1 or u == 2) and (v == 1 or v == 2):
            cntrl[2][u][v] = 2.
        else:
            cntrl[2][u][v] = -2.
        cntrl[3][u][v] = 1.
            
knots = [0.,0.,0.,0.,1.,1.,1.,1.]

srf = Srf.Srf(cntrl, knots, knots)
srf.plot()
