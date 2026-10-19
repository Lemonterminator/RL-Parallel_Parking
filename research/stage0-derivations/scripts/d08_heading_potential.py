"""Wrapped half-angle potential: branch derivative, cusp and valid lower bound."""
import json
import sympy as s
import numpy as np

def eq(a,b): assert s.simplify(s.trigsimp(a-b))==0

def main():
    e,eps=s.symbols('e epsilon',real=True)
    phi=1-s.cos(e/2)  # cos even, so abs has no effect on the principal branch
    derivative=s.diff(phi,e); eq(derivative,s.sin(e/2)/2)
    eq(s.diff(phi,e,2),s.cos(e/2)/4)
    eq(s.limit(derivative,e,0),0); eq(derivative.subs(e,s.pi/2),s.sqrt(2)/4)
    eq(derivative.subs(e,s.pi),s.Rational(1,2))
    eq(derivative.subs(e,s.pi-eps),s.cos(eps/2)/2)
    eq(s.limit(phi/e**2,e,0),s.Rational(1,8))
    # At the wrap boundary right branch uses e-2*pi.
    eq(s.diff(1-s.cos((e-2*s.pi)/2),e).subs(e,s.pi),-s.Rational(1,2))
    ee=np.linspace(1e-5,np.pi-1e-5,50000); dh=1e-6
    numerical=((1-np.cos((ee+dh)/2))-(1-np.cos((ee-dh)/2)))/(2*dh)
    analytic=.5*np.sin(ee/2); maxerr=float(np.max(np.abs(numerical-analytic)))
    assert maxerr<1e-8 and np.all(analytic>0)
    epsilon=np.deg2rad(10); region=np.linspace(np.pi-epsilon,np.pi,10000)
    lower=.5*np.cos(epsilon/2)
    bounderror=float(np.min(.5*np.sin(region/2))-lower); assert bounderror>=-1e-14
    tiny=1e-6; assert .5*np.sin(tiny/2)<.1
    print('PASS SymPy derivative / limits / wrap cusp; NumPy finite differences and valid interval bound')
    print(json.dumps(dict(derivative_at_pi_over_2=float(s.sqrt(2)/4),left_derivative_at_pi=.5,
       right_derivative_at_pi=-.5,derivative_at_1e_6=.5*np.sin(tiny/2),
       finite_difference_max_error=maxerr,epsilon_deg=10,near_pi_lower_bound=lower,
       near_pi_lower_bound_numeric_error=abs(bounderror)),sort_keys=True))

if __name__=='__main__': main()
