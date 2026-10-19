"""4. Explicitly specified two-arc parallel-parking model.

The original question does not specify enough obstacle/initial-pose parameters
for a unique minimum. This script derives a conditional closed form and checks
all four clearance groups against exact polygon clipping on an angle grid.
Steering changes sign once; the velocity remains negative throughout.
"""
import math
import numpy as np
import sympy as sp
from scipy.optimize import minimize_scalar
from shapely.geometry import Polygon, box


def symbolic():
    R,q,F,r,p,alpha,yf=sp.symbols('R q F r p alpha yf', positive=True)
    xi,eta=sp.symbols('xi eta', real=True)
    cc,ss=sp.cos(p),sp.sin(p)
    # Final axle (0,yf), second circle center (0,yf+R).
    xx=xi*cc+(R-eta)*ss
    yy=yf+R+xi*ss+(eta-R)*cc
    rho2=xi**2+(eta-R)**2
    sf=sp.sqrt(F**2+(R+q)**2-(R-q)**2)
    checks={
        'corner rotation invariant': (xx**2+(yy-yf-R)**2,rho2),
        'front outside radius': (rho2.subs({xi:F,eta:-q}),F**2+(R+q)**2),
        'front inside radius': (rho2.subs({xi:F,eta:q}),F**2+(R-q)**2),
        'rear outside radius': (rho2.subs({xi:-r,eta:-q}),r**2+(R+q)**2),
        'rear inside radius': (rho2.subs({xi:-r,eta:q}),r**2+(R-q)**2),
        'front tangency abscissa squared': (sf**2,F**2+4*R*q),
        'conditional slot formula': (r+sf,r+sp.sqrt(F**2+4*R*q)),
        'lateral shift': (2*R-2*R*sp.cos(alpha),2*R*(1-sp.cos(alpha))),
        'two arc longitudinal squared': ((2*R*sp.sin(alpha))**2,
                   4*R*(2*R*(1-sp.cos(alpha)))-(2*R*(1-sp.cos(alpha)))**2),
        'tail curb amplitude': ((r*ss+(R+q)*cc)**2+
                   (r*cc-(R+q)*ss)**2,r**2+(R+q)**2),
    }
    # First circle and second circle meet with equal axle position and heading.
    d=2*R*(1-sp.cos(alpha))
    first_x=2*R*sp.sin(alpha)+xi*cc-(R+eta)*ss
    first_y=yf+d-R+xi*ss+(R+eta)*cc
    checks['tangent x continuity']=(first_x.subs(p,alpha),xx.subs(p,alpha))
    checks['tangent y continuity']=(first_y.subs(p,alpha),yy.subs(p,alpha))
    checks['first arc relative height']=(first_y-(yf+d-R),
                                        (first_x-2*R*sp.sin(alpha))*sp.tan(p)+(R+eta)/sp.cos(p))
    z=R+q-d
    c1x=2*R*sp.sin(alpha)
    checks['first arc cap contact squared']=((c1x-(c1x-sp.sqrt((R-q)**2-z**2)))**2+z**2,
                                             (R-q)**2)
    checks['traffic height amplitude']=((F*ss+(R+q)*cc)**2+
                                (F*cc-(R+q)*ss)**2,F**2+(R+q)**2)
    for label,(lhs,rhs) in checks.items():
        assert sp.simplify(lhs-rhs)==0,label
    print('SymPy:',len(checks),'simplify(lhs-rhs)==0 assertions PASS')


def numerical():
    R=2.7/math.tan(.6)
    F,r,w=3.6,1.1,1.85
    q=w/2
    # These are declared extra assumptions, not parameters supplied by the user.
    d,c=2.5,.2
    yf=q+c
    alpha=math.acos(1-d/(2*R))
    corner=np.array([[-r,-q],[F,-q],[F,q],[-r,q]])
    sf=math.sqrt(F*F+2*R*w)
    candidate=r+sf
    outer=math.hypot(F,R+q)
    beta=math.atan2(R+q,F)-math.asin((R-q)/outer)
    # Insert the analytical front tangency and curb-tail extrema into the grid.
    angles=np.unique(np.r_[np.linspace(0,alpha,12001),beta,
                           math.atan(r/(R+q)),math.atan(F/(R+q))])
    angles=angles[(angles>=0)&(angles<=alpha)]
    band=box(-1000,c,1000,c+w)
    fmax,bmin,ymin,ymax=-np.inf,np.inf,np.inf,-np.inf
    e_circle=0.
    for phase in [1,2]:
        for p in angles:
            cs,sn=math.cos(p),math.sin(p)
            if phase==1:
                C=np.array([2*R*math.sin(alpha),yf+d-R])
                V=np.column_stack([C[0]+corner[:,0]*cs-(R+corner[:,1])*sn,
                                   C[1]+corner[:,0]*sn+(R+corner[:,1])*cs])
                exact_rho2=corner[:,0]**2+(R+corner[:,1])**2
            else:
                C=np.array([0.,yf+R])
                V=np.column_stack([corner[:,0]*cs+(R-corner[:,1])*sn,
                                   C[1]+corner[:,0]*sn+(corner[:,1]-R)*cs])
                exact_rho2=corner[:,0]**2+(corner[:,1]-R)**2
            e_circle=max(e_circle,np.max(np.abs(np.sum((V-C)**2,axis=1)-exact_rho2)))
            ymin=min(ymin,V[:,1].min()); ymax=max(ymax,V[:,1].max())
            cap=Polygon(V).intersection(band)
            if not cap.is_empty:
                bmin=min(bmin,cap.bounds[0]); fmax=max(fmax,cap.bounds[2])
    # Exact conditional solution: front car begins at sf; rear car ends at -r.
    # The numerical example verifies that arc 1 does not strengthen these.
    e_front=abs(fmax-sf); e_rear=abs(bmin+r)
    assert e_circle<1e-11
    assert e_front<1e-9 and e_rear<1e-9
    c_required=math.hypot(r,R+q)-(R+q)
    assert ymin>=-1e-10 and c>=c_required
    # Analytic first-arc gate: d>w, 0<z<R-q, and no stronger front bound.
    z=R+q-d
    first_front_bound=2*R*math.sin(alpha)-math.sqrt((R-q)**2-z*z)
    assert d>w and 0<z<R-q
    assert first_front_bound<sf
    assert alpha<math.atan((R-q)/r)
    H_analytic=yf+d-R+math.hypot(F,R+q)
    e_height=abs(H_analytic-ymax)
    assert e_height<1e-10
    # A road boundary H>=ymax completes the fourth clearance group.
    H=ymax+.2
    assert ymax<=H-.2+1e-12
    # Independent 1D optimization of the active front-corner/road-edge contact.
    crossing=lambda p: F*math.sin(p)-(R+q)*math.cos(p)+(R-q)
    from scipy.optimize import brentq
    pn=brentq(crossing,0,alpha,xtol=1e-14)
    xn=F*math.cos(pn)+(R+q)*math.sin(pn)
    e_scipy=abs(xn-sf)
    assert e_scipy<1e-10
    print('Declared model: same-width parked cars, curb y=0, final clearance c=0.2 m;')
    print('two reverse arcs, R=R_min, lateral shift d=2.5 m, unbounded car lengths.')
    print('Four corner radii [front-right, front-left, rear-right, rear-left] [m]:')
    print([math.hypot(F,R+q),math.hypot(F,R-q),math.hypot(r,R+q),math.hypot(r,R-q)])
    print('alpha [degree]:',math.degrees(alpha))
    print('Front obstacle x boundary [m]:',format(sf,'.12f'))
    print('Rear obstacle x boundary [m]:',format(-r,'.12f'))
    print('Conditional minimum slot length [m]:',format(candidate,'.12f'))
    print('Minimum final curb clearance for this full tail swing [m]:',format(c_required,'.12f'))
    print('Swept y range [m]:',ymin,ymax)
    print('First arc front cap analytic upper bound [m]:',first_front_bound)
    print('Traffic-side height analytic error [m]:',format(e_height,'.3e'))
    print('Shapely front/rear boundary max errors [m]:',format(e_front,'.3e'),format(e_rear,'.3e'))
    print('NumPy circle invariant max error [m^2]:',format(e_circle,'.3e'))
    print('SciPy contact root max error [m]:',format(e_scipy,'.3e'))
    print('All numerical assertions PASS. This is a conditional ideal-arc result,')
    print('not a unique minimum for the underspecified original scenario.')


if __name__=='__main__':
    symbolic(); numerical()
