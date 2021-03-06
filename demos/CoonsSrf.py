# Demonstration of a Coons surface

from Nurbs import Srf, Crv

pnts = [[0., 3., 4.5, 6.5, 8., 10.],
        [0., 0., 0., 0., 0., 0.],
        [2., 2., 7., 4., 7., 9.]]   
crv1 = Crv.Crv(pnts, [0., 0., 0., 1./3., 0.5, 2./3., 1., 1., 1.])
    
pnts= [[0., 3., 5., 8., 10.],
       [10., 10., 10., 10., 10.],
       [3., 5., 8., 6., 10.]]
crv2 = Crv.Crv(pnts, [0., 0., 0., 1./3., 2./3., 1., 1., 1.])
    
pnts= [[0.,0., 0., 0.],
       [0., 3., 8., 10.],
       [2., 0., 5., 3.]]
crv3 = Crv.Crv(pnts, [0., 0., 0., 0.5, 1., 1., 1.])
    
pnts= [[10., 10., 10., 10., 10.],
       [0., 3., 5., 8., 10.],
       [9., 7., 7., 10., 10.]]
crv4 = Crv.Crv(pnts, [0., 0., 0., 0.25, 0.75, 1., 1., 1.])
    
srf = Srf.Coons(crv1, crv2, crv3, crv4)
srf.plot()
