"""Equal opposite-curvature two-arc S path. Geometry vs ODE quadrature."""
import json
import sympy as s
import numpy as np
from scipy.integrate import solve_ivp

def eq(a,b): assert s.simplify(s.trigsimp(a-b))==0

def main():
    R,phi,t=s.symbols('R phi t',positive=True)
    # Integrate heading u then phi-u on two arcs parametrized by arc angle.
    x1=s.integrate(R*s.cos(t),(t,0,phi)); y1=s.integrate(R*s.sin(t),(t,0,phi))
    x2=s.integrate(R*s.cos(phi-t),(t,0,phi)); y2=s.integrate(R*s.sin(phi-t),(t,0,phi))
    eq(x1+x2,2*R*s.sin(phi)); eq(y1+y2,2*R*(1-s.cos(phi)))
    eq((x1+x2)**2,4*R*(y1+y2)-(y1+y2)**2)
    maxerr=0.; cases=0
    for rr in np.linspace(3.946,12,13):
        for dd in np.linspace(.03,2*rr,31):
            pp=np.arccos(1-dd/(2*rr))
            z=np.zeros(3)
            for sign in [1,-1]:
                result=solve_ivp(lambda _,z:[rr*np.cos(z[2]),rr*np.sin(z[2]),sign],
                                 [0,pp],z,rtol=2e-12,atol=2e-13)
                z=result.y[:,-1]
            target=np.array([np.sqrt(4*rr*dd-dd**2),dd,0])
            maxerr=max(maxerr,float(np.max(np.abs(z-target)))); cases+=1
    assert maxerr<1e-6
    # Finite steering slew does not force additional spatial distance if stopping
    # at the arc junction is permitted: v=0 makes every pose derivative zero.
    stationary=solve_ivp(lambda _,z:[0.,0.,0.,-.6],[0,2.],
                         [1.,2.,.4,.6],rtol=2e-12,atol=2e-13).y[:,-1]
    assert np.max(np.abs(stationary[:3]-[1.,2.,.4]))==0
    assert abs(stationary[3]+.6)<1e-12
    print('PASS SymPy integration and eliminated-angle identity; SciPy S-curve grid')
    print(json.dumps(dict(grid_cases=cases,max_coordinate_error=maxerr,example_R=2.7/np.tan(.6),
                         example_d=2.,example_longitudinal=np.sqrt(4*(2.7/np.tan(.6))*2-4),
                         stationary_steering_switch_seconds=2.,stationary_pose_error=0.),sort_keys=True))

if __name__=='__main__': main()
