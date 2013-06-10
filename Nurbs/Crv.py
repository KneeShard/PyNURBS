import math
from _Bas import bspkntins, bspdegelev, bspbezdecom, bspeval # Lowlevel Nurbs functions
from Util import  scale, translate, rotz

dependencies = '''This module requires:
	Numeric Python (NumPy)
'''

try:
    import numpy as np
except ImportError, value:
	print dependencies
	raise

NURBSError = 'NURBSError'

class Crv:
    '''Construct a NURB curve and check the format.
    
 The NURB curve is represented by a 4 dimensional b-spline.

 INPUT:

    cntrl  - Control points, homogeneous coordinates (wx,wy,wz,w)
            [dim,nu] matrix
            dim is the dimension valid options are:
            2 .... (x,y)        2D cartesian coordinates
            3 .... (x,y,z)      3D cartesian coordinates   
            4 .... (wx,wy,wz,w) 4D homogeneous coordinates

    uknots - Knot sequence along the parametric u direction.

 NOTES:

    Its assumed that the input knot sequences span the
    interval [0.0,1.0] and are clamped to the control
    points at the end by a knot multiplicity equal to
    the spline order.'''

    def __init__(self, cntrl, uknots):
        self._bezier = None
        # Force the u knot sequence to be a vector in ascending order
        # and normalise between [0.0,1.0]
        uknots = np.sort(np.asarray(uknots, np.float))
        nku = uknots.shape[0]
        uknots = (uknots - uknots[0])/(uknots[-1] - uknots[0])
        print "knot sequence: " + str(uknots)
        if uknots[0] == uknots[-1]:
            raise NURBSError, 'Illegal uknots sequence'
        self.uknots = uknots
        cntrl = np.asarray(cntrl, np.float)
        (dim, nu) = cntrl.shape
        if dim < 2 or dim > 4:
            raise NURBSError, 'Illegal control point format'
        elif dim < 4:
            self.cntrl = np.zeros((4, nu), np.float)
            self.cntrl[0:dim,:] = cntrl
            self.cntrl[-1,:] = np.ones((nu,))
        else:
            self.cntrl = cntrl
        # Spline degree
        self.degree = nku - nu - 1
        if self.degree < 0:
            raise NURBSError, 'NURBS order must be a positive integer'

    def trans(self, mat):
        "Apply the 4D transform matrix to the NURB control points."
        self.cntrl = np.dot(mat, self.cntrl)

    def reverse(self):
        "Reverse evaluation direction"
        self.cntrl = self.cntrl[:,::-1]
        self.uknots = 1 - self.uknots[::-1]
        
    def kntins(self, uknots):
        """Insert new knots into the curve
	NOTE: No knot multiplicity will be increased beyond the order of the spline"""
        if len(uknots):
            uknots = np.sort(np.asarray(uknots, np.float))
            if np.any(uknots < 0.) or np.any(uknots > 1.):
                raise NURBSError, 'NURBS curve parameter out of range [0,1]'
            self.cntrl, self.uknots = bspkntins(self.degree, self.cntrl, self.uknots, uknots)

    def degelev(self, degree):
        "Degree elevate the curve"
        if degree < 0:
            raise NURBSError, 'degree must be a positive number'
        if degree > 0:
            cntrl, uknots, nh = bspdegelev(self.degree, self.cntrl, self.uknots, degree)
            self.cntrl = cntrl[:,:nh + 1]
            self.uknots = uknots[:nh + self.degree + degree + 2]
            self.degree += degree

    def bezier(self, update = None):
        "Decompose curve to bezier segments and return overlaping control points"
        if update or not self._bezier:
            self._bezier = bspbezdecom(self.degree, self.cntrl, self.uknots)
        return self._bezier

    def bounds(self):
        "Return the boundingbox for the curve"
        ww = np.resize(self.cntrl[-1,:], (3, self.cntrl.shape[1]))
        cntrl = np.sort(self.cntrl[0:3,:]/ww)
        return np.asarray([cntrl[0,0], cntrl[1,0], cntrl[2,0],
                                cntrl[0,-1], cntrl[1,-1], cntrl[2,-1]], np.float)
                                
    def pnt3D(self, ut):
        "Evaluate parametric point[s] and return 3D cartesian coordinate[s]"
        val = self.pnt4D(ut)
        return val[0:3,:]/np.resize(val[-1,:], (3, val.shape[1]))

    def pnt4D(self, ut):
        "Evaluate parametric point[s] and return 4D homogeneous coordinates"
        ut = np.asarray(ut, np.float)
		
        if np.any(ut < 0.) or np.any(ut > 1.):
            raise NURBSError, 'NURBS curve parameter out of range [0,1]'
        return bspeval(self.degree, self.cntrl, self.uknots, ut)
                
    def plot(self, n = 25):
        """A simple plotting function for debugging purpose
	n = number of subdivisions.
	Depends on the matplotlib plotting library."""
        try:
			from mpl_toolkits.mplot3d import axes3d
			import matplotlib as mpl
			import matplotlib.pyplot as plt
        except ImportError, value:
            print 'matplotlib plotting library not available'
            return

        pnts = self.pnt3D(np.arange(n + 1, dtype = np.float64)/n)
        knots = self.pnt3D(self.uknots)

		# TODO clean (most of this isn't necessary with matplotlib)
        maxminx = np.sort(self.cntrl[0,:]/self.cntrl[3,:])
        minx = maxminx[0]
        maxx = maxminx[-1]
        if minx == maxx:
            minx -= 1.
            maxx += 1.
        maxminy = np.sort(self.cntrl[1,:]/self.cntrl[3,:])
        miny = maxminy[0]
        maxy = maxminy[-1]
        if miny == maxy:
            miny -= 1.
            maxy += 1.
        maxminz = np.sort(self.cntrl[2,:]/self.cntrl[3,:])
        minz = maxminz[0]
        maxz = maxminz[-1]
        if minz == maxz:
            minz -= 1.
            maxz += 1.
			
        fig = plt.figure()
            
        
        ax = fig.add_subplot(111, projection='3d')
        # TODO
        plt.title("b-spline Curve. n={}, p={}".format(1,-1 ))
        plt.xlabel('x')
        plt.ylabel('y')
        # FIXME plt.zlabel('z')
		# actual nurbs
        plt.plot(pnts[0,:], pnts[1,:], pnts[2,:], label='parametric bspline')

		# control points/polygon
        plt.plot(self.cntrl[0,:]/self.cntrl[3,:], self.cntrl[1,:]/self.cntrl[3,:],
                      self.cntrl[2,:]/self.cntrl[3,:], 'ro-', label='control pts', linewidth=.5)

        plt.plot(knots[0,:], knots[1,:], knots[2,:], 'y+', markersize = 10, markeredgewidth=1.8, label="knots")
        plt.legend(fontsize='x-small',bbox_to_anchor=(0.91, 1), loc=2, borderaxespad=-1.)
        plt.savefig("bspline-curve-R3.png")
        # plt.show() # stops here
        plt.close()

        # dislin.metafl('cons')
        # dislin.disini()
        # dislin.hwfont()
        # dislin.pagera()
        # dislin.name('X-axis', 'X')
        # dislin.name('Y-axis', 'Y')
        # dislin.name('Z-axis', 'Z')
        # dislin.graf3d(minx, maxx, 0 , abs((maxx-minx)/4.),
        #               miny, maxy, 0 , abs((maxy-miny)/4.),
        #               minz, maxz, 0 , abs((maxz-minz)/4.))
        # dislin.color('yellow')
			# se: changes to plot
        # dislin.curv3d(pnts[0,:], pnts[1,:], pnts[2,:], n+1)
        # dislin.color('red')
        # dislin.dashm()
        # dislin.curv3d(self.cntrl[0,:]/self.cntrl[3,:], self.cntrl[1,:]/self.cntrl[3,:],
        #               self.cntrl[2,:]/self.cntrl[3,:], self.cntrl.shape[1])
        # dislin.color('white')
        # dislin.incmrk(-1)
        # dislin.marker(8)
        # dislin.curv3d(knots[0,:], knots[1,:], knots[2,:], knots.shape[1])
        # dislin.disfin()

    def __call__(self, *args):
        return self.pnt3D(args[0])

    def __repr__(self):
        return 'Nurbs curve:\ndegree: %s\ncntrl: %s\nuknots: %s\n' % (`self.degree`,`self.cntrl`,`self.uknots`)

class Line(Crv):
    """A straight line segment
	Example: c = Line([0,0],[1,1])"""
    def __init__(self, p1 = (0,0,0), p2 = (1,0,0)):
        Crv.__init__(self, np.transpose([p1,p2]), [0,0,1,1])
                       
class Polyline(Crv):
    """A polyline
	Example: c = Polyline([[0,0],[5,2],[10,8]])"""
    def __init__(self, pnts):
        pnts = np.transpose(np.asarray(pnts, np.float))
        npnts = pnts.shape[1]
        if npnts < 3:
            raise NURBSError, 'Point sequence error'
        cntrl = np.zeros((pnts.shape[0], 2 * npnts - 2), np.float)
        cntrl[:,0] = pnts[:,0]
        cntrl[:,-1] = pnts[:,-1]
        cntrl[:,1:-2:2] = pnts[:,1:-1]
        cntrl[:,2:-1:2] = pnts[:,1:-1]
        uknots = np.zeros(npnts * 2, np.float)
        uknots[0::2] = np.arange(npnts)
        uknots[1::2] = np.arange(npnts)
        Crv.__init__(self, cntrl, uknots)

class UnitCircle(Crv):
    "NURBS representation of a unit circle in the xy plan"
    def __init__(self):
        r22 = np.sqrt(2.)/2.
        uknots = [0., 0., 0., 0.25, 0.25, 0.5, 0.5, 0.75, 0.75, 1., 1.,1.]
        cntrl = [[0., r22, 1., r22, 0., -r22, -1., -r22, 0.],
                 [-1., -r22, 0., r22, 1., r22, 0., -r22, -1.],
                 [0., 0., 0., 0., 0., 0., 0., 0., 0.],
                 [1., r22, 1., r22, 1., r22, 1., r22, 1.]]
        Crv.__init__(self, cntrl, uknots)

class Circle(UnitCircle):
    """NURBS representation of a circle in the xy plan
	with given radius (default = .5) and optional center."""
    def __init__(self, radius = .5, center = None):
        UnitCircle.__init__(self)
        if radius != 1.:
            self.trans(scale([radius, radius]))
        if center:
            self.trans(translate(center))

class Arc(Crv):
    """NURBS representation of a arc in the xy plan
	with given radius (default = 1.) and optional center,
	start angle (default = 0) and end angle. (default = 2*pi)""" 
    def __init__(self, radius = 1.,center = None, sang = 0., eang = 2*math.pi):
        sweep = eang - sang # sweep angle of arc
        if sweep < 0.:
            sweep = 2.*math.pi + sweep
        if abs(sweep) <= math.pi/2.:
            narcs = 1   # number of arc segments
            knots = [0., 0., 0., 1., 1., 1.]
        elif abs(sweep) <= math.pi:
            narcs = 2
            knots = [0., 0., 0., 0.5, 0.5, 1., 1., 1.]
        elif abs(sweep) <= 3.*math.pi/2.:
            narcs = 3
            knots = [0., 0., 0., 1./3., 1./3., 2./3., 2./3., 1., 1., 1.]
        else:
            narcs = 4
            knots = [0., 0., 0., 0.25, 0.25, 0.5, 0.5, 0.75, 0.75, 1., 1., 1.]

        dsweep = sweep/(2.*narcs);     # arc segment sweep angle/2
        
        # determine middle control point and weight
        wm = math.cos(dsweep)
        x  = radius*math.cos(dsweep)
        y  = radius*math.sin(dsweep)
        xm = x+y*math.tan(dsweep)

        # arc segment control points
        ctrlpt = np.array([[x, wm*xm, x], [-y, 0., y], [0., 0., 0.], [1., wm, 1.]], np.float)
        # build up complete arc from rotated segments
        coefs = np.zeros((4, 2*narcs+1), np.float)   # nurb control points of arc
        # rotate to start angle
        coefs[:,0:3] = np.dot(rotz(sang + dsweep), ctrlpt)
        xx = rotz(2*dsweep)
        for ms in range(2, 2*narcs,2):
            coefs[:,ms:ms+3] = np.dot(xx, coefs[:,ms-2:ms+1])
        if center:
            xx = translate(center)
            coefs = np.dot(xx, coefs)
        Crv.__init__(self, coefs, knots)

if __name__ == '__main__':
    #c = Polyline([[0,0],[5,2],[10,8]])
    #c = Crv([[0,30,60,90],[0,0,30,30]],[0,0,0,0,1,1,1,1])
    #c = Line([0,0],[1,1])
    c = UnitCircle()
    #c = Arc(1.,None,0,math.pi/2.)

    '''cntrl = [[-50., -75., 25., 0., -25., 75., 50.],
             [25., 50., 50., 0., -50., -50., 25.]]
    knots = [0., 0., 0., .2, .4, .6, .8, 1., 1., 1.]
    c = Crv(cntrl, knots)'''
    c.plot()
