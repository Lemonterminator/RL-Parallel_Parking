"""Rear-axle / CoG bicycle derivation; run directly with Python 3."""
import json
import sympy as s
import numpy as np
from scipy.integrate import solve_ivp

def eq(lhs, rhs):
    assert s.simplify(s.expand_trig(lhs-rhs)) == 0

def main():
    L,v,k,b,t = s.symbols('L v k b t', real=True, nonzero=True)
    th,x,y = s.symbols('theta x y', real=True)
    rho=L/k
    cx=x-rho*s.sin(th); cy=y+rho*s.cos(th)
    eq(s.diff(cx,x)*v*s.cos(th)+s.diff(cx,th)*v*k/L,0)
    eq(s.diff(cy,y)*v*s.sin(th)+s.diff(cy,th)*v*k/L,0)
    eq((x-cx)**2+(y-cy)**2,rho**2)
    # CoG velocity = v*u + b*omega*u_perp. beta=atan(b*k/L).
    eq((v*s.cos(th)-b*v*k/L*s.sin(th))**2+
       (v*s.sin(th)+b*v*k/L*s.cos(th))**2,v**2*(1+(b*k/L)**2))
    eq(rho**2+b**2, (L**2+b**2*k**2)/k**2)
    beta=s.atan(b*k/L)
    # L is positive physically; substitute positive L for the trig identity.
    lp=s.symbols('lp',positive=True)
    eq(s.tan(beta),b*k/L)
    eq((v/s.cos(beta))*s.cos(beta)*k/L,v*k/L)
    eq(s.sin(beta)/s.cos(beta),b*k/L)
    eq(v/s.cos(beta)*s.cos(th+beta),v*s.cos(th)-b*v*k/L*s.sin(th))
    eq(v/s.cos(beta)*s.sin(th+beta),v*s.sin(th)+b*v*k/L*s.cos(th))
    xx=x+rho*(s.sin(th+v*k/L*t)-s.sin(th))
    yy=y-rho*(s.cos(th+v*k/L*t)-s.cos(th))
    eq(xx.subs(t,0),x); eq(yy.subs(t,0),y)
    eq(s.diff(xx,t),v*s.cos(th+v*k/L*t))
    eq(s.diff(yy,t),v*s.sin(th+v*k/L*t))
    rng=np.random.default_rng(20261019); maxerr=0.; rotations={}
    for vv,dd in [(1.5,.6),(1.5,-.6),(-1.5,.6),(-1.5,-.6)]:
        omega=vv*np.tan(dd)/2.7; R=2.7/np.tan(dd)
        ini=np.array([.2,-.3,.41]); T=3.
        sol=solve_ivp(lambda _,z:[vv*np.cos(z[2]),vv*np.sin(z[2]),omega],
                      [0,T],ini,rtol=2e-12,atol=2e-13,dense_output=True)
        tt=np.linspace(0,T,301); z=sol.sol(tt); a=ini[2]+omega*tt
        exact=np.array([ini[0]+R*(np.sin(a)-np.sin(ini[2])),
                        ini[1]-R*(np.cos(a)-np.cos(ini[2])),a])
        maxerr=max(maxerr,float(np.max(np.abs(z-exact))))
        assert np.sign(z[2,-1]-ini[2])==np.sign(vv*dd)
        rotations[f'v={vv},delta={dd}']='CCW' if omega>0 else 'CW'
    assert maxerr<1e-8
    print('PASS SymPy identities; solve_ivp four sign combinations')
    print(json.dumps(dict(R_min=2.7/np.tan(.6),max_integration_error=maxerr,
                         rotation=rotations),sort_keys=True))

if __name__=='__main__': main()
