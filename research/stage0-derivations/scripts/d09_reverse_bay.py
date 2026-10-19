"""9. Mouth-clipped static envelope and a strict single reverse arc.

Run with Python 3; dependencies: sympy, numpy, scipy, shapely.
The static envelope optimizes a different pose translation at each angle. It is
a necessary geometric bound, not a nonholonomic trajectory certificate.
"""
import math
import numpy as np
import sympy as sp
from scipy.optimize import brentq, minimize_scalar
from shapely.geometry import Polygon, box


def symbolic():
    p = sp.symbols('p', real=True)
    ell, width, gap, h = sp.symbols('ell width gap h', positive=True)
    R, q, b, xi, eta, F, rr = sp.symbols('R q b xi eta F rr', positive=True)
    s, c = sp.sin(p), sp.cos(p)
    H = ell*s + width*c
    h_tri = gap*s*c
    h_mid = (gap-width*s)*sp.tan(p)
    checks = {
        'triangle cap width': (h_tri*(sp.tan(p)+1/sp.tan(p)), gap),
        'trapezoid cap width': (width*s+h_mid/sp.tan(p), gap),
        'triangle protrusion': (H-h_tri, ell*s+width*c-gap*s*c),
        'trapezoid protrusion': (H-h_mid, ell*s+width/c-gap*sp.tan(p)),
        'stationarity equation': (sp.diff(H-h_mid,p)*c**2,
                                  ell*c**3+width*s-gap),
        'height amplitude': (H**2+(ell*c-width*s)**2, ell**2+width**2),
        'depth cap branch': (H-h, H+(-h)),
    }
    xx = R+xi*c-(R+eta)*s
    yy = -b+xi*s+(R+eta)*c
    checks.update({
        'arc constant radius': ((xx-R)**2+(yy+b)**2,xi**2+(R+eta)**2),
        'arc derivative x': (sp.diff(xx,p),-(yy+b)),
        'arc derivative y': (sp.diff(yy,p),xx-R),
        'right wall threshold': ((R-q)**2-b**2-(R-gap/2)**2,
                                R*(gap-2*q)-b**2+q**2-gap**2/4),
        'left wall threshold': ((R+gap/2)**2-(rr**2+(R+q)**2),
                               R*(gap-2*q)+gap**2/4-q**2-rr**2),
        'arc plus straight initial-lane condition': ((R-q)**2-
                              ((gap-2*q)*R+q**2-gap**2/4),(R-gap/2)**2),
        'arc plus straight derivative sign reduction':
            (4*((gap-2*q)*R+q**2-gap**2/4)*(R+q)**2
                -(gap-2*q)**2*(F**2+(R+q)**2),
             (gap-2*q)*(2*(2*R-gap)*(R+q)**2-(gap-2*q)*F**2)),
        'straight orientation x': (xx.subs(p,sp.pi/2),-eta),
        'straight orientation y': (yy.subs(p,sp.pi/2),-b+xi),
    })
    wall_depth=sp.sqrt((gap-2*q)*R+q**2-gap**2/4)
    radius_front=sp.sqrt(F**2+(R+q)**2)
    checks['arc plus straight aisle derivative']=(
        sp.diff(radius_front-wall_depth,R),
        (R+q)/radius_front-(gap-2*q)/(2*wall_depth))
    checks['arc plus straight positive first-term derivative']=(
        sp.diff((R+q)/radius_front,R),F**2/radius_front**3)
    for label,(lhs,rhs) in checks.items():
        assert sp.simplify(lhs-rhs) == 0, label
    print('SymPy:',len(checks),'simplify(lhs-rhs)==0 assertions PASS')


L,F,r,w = 2.7,3.6,1.1,1.85
ell,q = F+r,w/2


def cap_width(h,p):
    """Width of the closed-set clip to y<=0, with lowest body y=-h.

    h<0 means the whole body is above the mouth, hence an empty clip. At
    h=0 a horizontal/vertical rectangle touches along its full lower edge;
    other angles touch at one vertex. Endpoint angles are treated exactly,
    without snapping small nonzero angles to an endpoint.
    """
    if h < 0: return 0.0
    if p == 0: return ell
    if p == math.pi/2: return w
    s,c=math.sin(p),math.cos(p)
    return min(w*s,h*math.tan(p))+min(ell*c,h/math.tan(p))


def cap_depth(p,g):
    """Supremal insertion depth; endpoint value need not be attained.

    At p=0 and g<ell, no h>=0 passes the closed-set cap-width test: even the
    touching lower edge has width ell. The returned 0 is the supremum of
    feasible h<0 (approach from a fully clear body above the mouth), so the
    static aisle formula gives an infimum there rather than an attained pose.
    """
    s,c=math.sin(p),math.cos(p)
    H=ell*s+w*c
    if ell*c+w*s <= g: return H
    if p < 1e-14: return 0.0
    # General exact cases; numerical tests use w < g < ell.
    h0=g*s*c
    if h0 <= min(w*c,ell*s)+1e-14: return h0
    if w*c <= ell*s: return (g-w*s)*s/c
    return (g-ell*c)*c/s


def static_A(p,g,D=5.3,c_end=.3):
    H=ell*math.sin(p)+w*math.cos(p)
    return max(0.,H-min(cap_depth(p,g),D-c_end))


def clipped_polygon_width(p,h):
    s,c=math.sin(p),math.cos(p)
    # Lowest corner at (0,-h); adjacent edges ell*u and w*v.
    verts=np.array([[0,0],[ell*c,ell*s],
                    [ell*c-w*s,ell*s+w*c],[-w*s,w*c]])
    verts[:,1]-=h
    P=Polygon(verts).intersection(box(-100,-100,100,0))
    return 0.0 if P.is_empty else P.bounds[2]-P.bounds[0]


def numerical():
    g=2.5
    # Exact endpoint angles need their own tests. Positive insertion depths
    # avoid Shapely's pi/2 trig rounding at a zero-area contact edge.
    e_endpoint=0.
    for p in [0.,math.pi/2]:
        H=ell*math.sin(p)+w*math.cos(p)
        for h in [.0001,.1,H/2,H,H+.5]:
            e_endpoint=max(e_endpoint,abs(clipped_polygon_width(p,h)-cap_width(h,p)))
    assert e_endpoint<1e-12
    assert cap_width(0.,0.)==ell
    assert cap_width(0.,math.pi/2)==w
    e_empty=0.
    for p in [0.,.37,math.pi/2]:
        for h in [-.001,-.1,-1.]:
            e_empty=max(e_empty,abs(clipped_polygon_width(p,h)-cap_width(h,p)))
            assert cap_width(h,p)==0.
    assert e_empty==0.
    # Independent polygon clipping versus analytic cap width, at all cap depths.
    e_width=0.
    for p in np.linspace(.002,math.pi/2-.002,73):
        H=ell*math.sin(p)+w*math.cos(p)
        for h in np.linspace(.001,H,41):
            e_width=max(e_width,abs(clipped_polygon_width(p,h)-cap_width(h,p)))
    assert e_width < 1e-10
    e_depth=0.
    for p in np.linspace(.002,math.pi/2-.002,301):
        B=ell*math.cos(p)+w*math.sin(p)
        if B>g:
            H=ell*math.sin(p)+w*math.cos(p)
            numeric=brentq(lambda h: clipped_polygon_width(p,h)-g,
                           1e-12,H,xtol=2e-13)
            e_depth=max(e_depth,abs(numeric-cap_depth(p,g)))
    assert e_depth<1e-10
    res=minimize_scalar(lambda p:-static_A(p,g),bounds=(.001,math.pi/2-.001),
                        method='bounded',options={'xatol':1e-14})
    p_star=brentq(lambda p:ell*math.cos(p)**3+w*math.sin(p)-g,
                  math.asin(w/g),1.15,xtol=1e-14)
    A=static_A(p_star,g)
    e_opt=abs(A+res.fun)
    assert e_opt<1e-10
    # D>=ell+c_end: this case's global envelope maximum is unchanged.
    ps=np.linspace(0,math.pi/2,10001)
    global_max=[]
    for D in [ell+.3,5.3,6.,10.]:
        global_max.append(max(static_A(p,g,D) for p in ps))
    e_depth_independence=max(global_max)-min(global_max)
    assert e_depth_independence<1e-10
    # Exact depth reduction follows max over angles of max(A_inf,H-D+c_end).
    e_depth_formula=0.
    Hmax=math.hypot(ell,w)
    for usable in [.8,1.5,ell,5.,8.]:
        direct=max(static_A(p,g,usable+.3) for p in ps)
        rhs=max(A,Hmax-usable,0.)
        # Angle grid misses an unconstrained analytic maximum by O(mesh^2).
        e_depth_formula=max(e_depth_formula,abs(direct-rhs))
    assert e_depth_formula<1e-7
    wide_g=Hmax+.1
    wide_p=math.atan(ell/w)
    wide_counter=static_A(wide_p,wide_g,ell+.3)
    assert abs(wide_counter-(Hmax-ell))<1e-12 and wide_counter>.3
    # Strict quarter arc ending directly at the specified final rear-axle pose.
    b=3.9
    Rkin=L/math.tan(.6)
    Rright=(b*b-q*q+g*g/4)/(g-w)
    Rleft=(r*r+q*q-g*g/4)/(g-w)
    Rreq=max(Rkin,b+q,Rright,Rleft)
    Aarc=math.hypot(F,Rreq+q)-b
    xr=Rreq-math.sqrt((Rreq-q)**2-b*b)
    xl=Rreq-math.hypot(r,Rreq+q)
    # Shapely sweep clipping, including the analytic extremum parameters.
    p_right=math.acos(b/(Rreq-q))
    p_left=math.atan((Rreq+q)/r)
    p_top=math.atan(F/(Rreq+q))
    path_angles=np.unique(np.r_[np.linspace(0,math.pi/2,12001),
                                p_right,p_left,p_top])
    xmin,xmax,ymax,ymin=np.inf,-np.inf,-np.inf,np.inf
    local=np.array([[-r,-q],[F,-q],[F,q],[-r,q]])
    for p in path_angles:
        c,s=math.cos(p),math.sin(p)
        V=np.column_stack([Rreq+local[:,0]*c-(Rreq+local[:,1])*s,
                           -b+local[:,0]*s+(Rreq+local[:,1])*c])
        P=Polygon(V)
        ymin=min(ymin,V[:,1].min()); ymax=max(ymax,V[:,1].max())
        B=P.intersection(box(-1000,-1000,1000,0))
        if not B.is_empty:
            xmin=min(xmin,B.bounds[0]); xmax=max(xmax,B.bounds[2])
    e_arc=max(abs(xmin-xl),abs(xmax-xr),abs(ymax-Aarc),abs(ymin-(-b-r)))
    assert e_arc<1e-9
    # Independent SciPy integration of rear axle with p as independent variable.
    from scipy.integrate import solve_ivp
    sol=solve_ivp(lambda p,z:[-Rreq*math.cos(p),-Rreq*math.sin(p)],
                  (0,math.pi/2),(Rreq,Rreq-b),rtol=2.3e-14,atol=1e-13,
                  dense_output=True)
    pp=np.linspace(0,math.pi/2,801)
    true=np.vstack([Rreq-Rreq*np.sin(pp),-b+Rreq*np.cos(pp)])
    e_ivp=np.max(np.abs(sol.sol(pp)-true))
    assert e_ivp<1e-9
    # Common single-entry model: quarter arc, stop and straighten, then reverse
    # vertically to the target. Its arc endpoint depth b is a decision variable.
    k=g-w
    def arc_depth(R):
        return min(b,R-q,math.sqrt(k*R+q*q-g*g/4))
    def arc_straight_aisle(R):
        return math.hypot(F,R+q)-arc_depth(R)
    # Wall-active branch derivative is positive at R_min. Its first term grows
    # with R and its subtracted term decreases, so it remains positive.
    b_arc=arc_depth(Rkin)
    A_arc_straight=arc_straight_aisle(Rkin)
    deriv_at_min=(Rkin+q)/math.hypot(F,Rkin+q)-k/(2*b_arc)
    assert deriv_at_min>0
    assert 2*(2*Rkin-g)*(Rkin+q)**2>k*F**2
    opt=minimize_scalar(arc_straight_aisle,bounds=(Rkin,Rright+10),
                        method='bounded',options={'xatol':1e-13})
    e_opt_arc=abs(opt.fun-A_arc_straight)
    assert e_opt_arc<1e-6
    e_grid_opt=max(0.,A_arc_straight-min(arc_straight_aisle(R)
                     for R in np.linspace(Rkin,Rright+10,3001)))
    assert e_grid_opt<1e-12
    # Independent polygon-clipped sweep, with the extrema inserted explicitly.
    ps_arc=np.unique(np.r_[np.linspace(0,math.pi/2,12001),
                 math.acos(b_arc/(Rkin-q)),math.atan((Rkin+q)/r),
                 math.atan(F/(Rkin+q))])
    xs_lo,xs_hi,ys_lo,ys_hi=np.inf,-np.inf,np.inf,-np.inf
    poses=[]
    for p in ps_arc:
        poses.append((Rkin-Rkin*math.sin(p),-b_arc+Rkin*math.cos(p),p))
    for by in np.linspace(b_arc,b,4001):
        poses.append((0.,-by,math.pi/2))
    for rear_x,rear_y,p in poses:
        cs,sn=math.cos(p),math.sin(p)
        V=np.column_stack([rear_x+local[:,0]*cs-local[:,1]*sn,
                           rear_y+local[:,0]*sn+local[:,1]*cs])
        ys_lo=min(ys_lo,V[:,1].min()); ys_hi=max(ys_hi,V[:,1].max())
        cap=Polygon(V).intersection(box(-1000,-1000,1000,0))
        if not cap.is_empty:
            xs_lo=min(xs_lo,cap.bounds[0]); xs_hi=max(xs_hi,cap.bounds[2])
    true_left=Rkin-math.hypot(r,Rkin+q)
    e_sweep_arc_straight=max(abs(xs_lo-true_left),abs(xs_hi-g/2),
                            abs(ys_hi-A_arc_straight),abs(ys_lo+b+r))
    assert e_sweep_arc_straight<1e-9
    assert xs_lo>=-g/2-1e-12 and xs_hi<=g/2+1e-12
    print('NumPy/Shapely cap width max error [m]:',format(e_width,'.3e'))
    print('Shapely endpoint positive-depth cap width max error [m]:',format(e_endpoint,'.3e'))
    print('Shapely negative-depth empty-clip max error [m]:',format(e_empty,'.3e'))
    print('h=0 uses a closed-set contact edge at endpoint angles; horizontal')
    print('cap_depth=0 for g<ell is an unattained supremum from h<0.')
    print('Shapely+SciPy cap depth max error [m]:',format(e_depth,'.3e'))
    print('SciPy optimization value error [m]:',format(e_opt,'.3e'))
    print('D grid envelope variation [m]:',format(e_depth_independence,'.3e'))
    print('Analytic depth max formula/grid max error [m]:',format(e_depth_formula,'.3e'))
    print('Wide-mouth counterexample to unrestricted D-invariance [m]:',wide_counter)
    print('Static mouth-clipped lower bound [m]:',format(A,'.12f'))
    print('Corresponding psi [degree]:',format(math.degrees(p_star),'.12f'))
    print('Corresponding cap depth h [m]:',format(cap_depth(p_star,g),'.12f'))
    print('Strict fixed-target quarter-arc R required [m]:',format(Rreq,'.12f'))
    print('Strict fixed-target quarter-arc aisle A [m]:',format(Aarc,'.12f'))
    print('Strict quarter-arc mouth x range [m]:',xmin,xmax)
    print('Strict quarter-arc Shapely extrema max error [m]:',format(e_arc,'.3e'))
    print('SciPy rear-axle IVP max error [m]:',format(e_ivp,'.3e'))
    print('R_min arc initial rear y and body bottom [m]:',Rkin-b,Rkin-b-q)
    print('Arc plus straight optimal R [m]:',format(Rkin,'.12f'))
    print('Arc plus straight arc-end rear depth b [m]:',format(b_arc,'.12f'))
    print('Arc plus straight minimum aisle A [m]:',format(A_arc_straight,'.12f'))
    print('Arc plus straight derivative at R_min:',format(deriv_at_min,'.12f'))
    print('SciPy bounded optimization aisle error [m]:',format(e_opt_arc,'.3e'))
    print('Arc plus straight Shapely swept mouth x range [m]:',xs_lo,xs_hi)
    print('Arc plus straight Shapely extrema max error [m]:',format(e_sweep_arc_straight,'.3e'))
    print('Arc plus straight stop before straightening; finite steering rate')
    print('is compatible with this geometry by steering while v=0.')
    print('All numerical assertions PASS; c=0 used only for numerical examples.')


if __name__=='__main__':
    symbolic(); numerical()
