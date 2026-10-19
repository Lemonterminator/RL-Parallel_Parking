"""Rigid-body displacement bound; sampling cannot certify all grazing contact."""
import json
import sympy as s
import numpy as np
from shapely.geometry import Polygon,box
from scipy.optimize import brentq

def eq(a,b): assert s.simplify(s.trigsimp(a-b))==0

def main():
    x,y,a=s.symbols('x y alpha',real=True)
    Fq=s.Rational(36,10); qq=s.Rational(925,1000); rq=s.Rational(11,10)
    eq(s.sqrt(Fq**2+qq**2)**2,Fq**2+qq**2)
    assert s.simplify(Fq**2-rq**2)>0
    dx=(s.cos(a)-1)*x-s.sin(a)*y; dy=s.sin(a)*x+(s.cos(a)-1)*y
    eq(dx**2+dy**2,2*(1-s.cos(a))*(x*x+y*y))
    eq(2*(1-s.cos(a)),4*s.sin(a/2)**2)
    qstep=s.symbols('q_step',real=True)
    eq((qstep+dx)**2+dy**2,qstep**2+2*(1-s.cos(a))*(x*x+y*y)+2*qstep*((s.cos(a)-1)*x-s.sin(a)*y))
    dmax=np.hypot(3.6,.925); R=2.7/np.tan(.6); v=1.5; h=.02; alpha=v*h/R
    bound=v*h+dmax*abs(alpha)
    corners=np.array([[x,y] for x in [-1.1,3.6] for y in [-.925,.925]])
    rot=lambda a:np.array([[np.cos(a),-np.sin(a)],[np.sin(a),np.cos(a)]])
    # Actual explicit Euler pose increment, maximized at a body vertex.
    diff=corners@rot(alpha).T+np.array([v*h,0])-corners
    forward_actual=float(np.max(np.linalg.norm(diff,axis=1)))
    four_signs={}
    for vv in [v,-v]:
        for dd in [.6,-.6]:
            aa=vv*np.tan(dd)*h/2.7
            displacements=corners@rot(aa).T+np.array([vv*h,0])-corners
            four_signs[f'v={vv},delta={dd}']=float(np.max(np.linalg.norm(displacements,axis=1)))
    actual=max(four_signs.values())
    exact_translation=np.array([R*np.sin(alpha),R*(1-np.cos(alpha))])
    exact=float(np.max(np.linalg.norm(corners@rot(alpha).T+exact_translation-corners,axis=1)))
    rng=np.random.default_rng(20261019); excess=-np.inf; identity_error=0.
    for _ in range(30000):
        p=rng.uniform([-1.1,-.925],[3.6,.925]); theta=rng.uniform(-np.pi,np.pi)
        da=rng.uniform(-alpha,alpha); tr=rng.uniform(-.03,.03,2)
        measured=np.linalg.norm(rot(theta+da)@p+tr-rot(theta)@p)
        upper=np.linalg.norm(tr)+dmax*abs(da)
        excess=max(excess,measured-upper)
        identity_error=max(identity_error,abs(np.linalg.norm((rot(da)-np.eye(2))@p)-2*np.linalg.norm(p)*abs(np.sin(da/2))))
    assert excess<=1e-12 and identity_error<1e-12 and actual<=bound
    # Whole vehicle, exact constant-turn arc: its outer front corner reaches a
    # local maximum y between samples. A wall of arbitrary thickness is grazed.
    wall=box(-100,0,100,100)
    ordered=corners[[0,2,3,1]]
    rc=np.hypot(3.6,R+.925); peak=np.pi-np.arctan2(3.6,R+.925)
    penetration=.5*rc*(1-np.cos(alpha/2))
    C=np.array([0.,-rc+penetration])
    def body(th):
        rear=C+np.array([R*np.sin(th),-R*np.cos(th)])
        return Polygon(ordered@rot(th).T+rear)
    assert not wall.intersects(body(peak-alpha/2))
    assert wall.intersects(body(peak))
    assert not wall.intersects(body(peak+alpha/2))
    # The same phenomenon for linear rear translation + linear heading inside
    # the specified old-state Euler pose update (a common sweep interpolation).
    omega=v/R
    theta0=brentq(lambda th:v*np.sin(th)+omega*(3.6*np.cos(th+alpha/2)+
                              .925*np.sin(th+alpha/2)),np.pi/2,np.pi)
    def top_y(t):
        return v*t*np.sin(theta0)+3.6*np.sin(theta0+omega*t)-.925*np.cos(theta0+omega*t)
    midraw=top_y(h/2); sag=midraw-max(top_y(0),top_y(h))
    assert sag>0
    shift=-midraw+sag/2
    def euler_body(t):
        rear=np.array([v*t*np.cos(theta0),shift+v*t*np.sin(theta0)])
        return Polygon(ordered@rot(theta0+omega*t).T+rear)
    assert not wall.intersects(euler_body(0))
    assert wall.intersects(euler_body(h/2))
    assert not wall.intersects(euler_body(h))
    print('PASS SymPy rotation norm identity; NumPy displacement bound; finite-wall grazing counterexample')
    print(json.dumps(dict(d_max=dmax,alpha=alpha,translation=v*h,corner_displacement_bound=bound,
      actual_euler_corner_max=actual,forward_euler_corner_max=forward_actual,
      four_sign_euler_maxima=four_signs,actual_exact_arc_corner_max=exact,
      random_max_excess=excess,rotation_norm_identity_max_error=identity_error,
      thick_wall_grazing_penetration=penetration,
      euler_interpolation_grazing_penetration=sag/2,
      universal_min_wall_thickness=None,full_crossing_sufficient_wall_thickness_strictly_greater_than=bound),sort_keys=True))

if __name__=='__main__': main()
