"""Explicit old-state Euler: its displaced circle, chord and closure errors."""
import json
import sympy as s
import numpy as np

def eq(a,b):
    residual=a-b
    # Set alpha=2*u before expanding the half-angle identities (invertible).
    residual=s.expand_trig(residual.subs(s.Symbol('alpha',real=True),2*s.Symbol('_u',real=True)))
    if isinstance(residual,s.MatrixBase):
        for entry in residual: assert s.simplify(s.trigsimp(entry,method='fu'))==0
    else: assert s.simplify(s.trigsimp(residual,method='fu'))==0

def main():
    a,t,q=s.symbols('alpha theta q',real=True)
    # Circle center relative to z0 is (q/2, q*cot(a/2)/2) in initial frame.
    C=s.Matrix([q/2,q*s.cos(a/2)/(2*s.sin(a/2))])
    Rot=s.Matrix([[s.cos(a),-s.sin(a)],[s.sin(a),s.cos(a)]])
    eq((s.eye(2)-Rot)*C,s.Matrix([q,0]))
    eq(C.dot(C),q**2/(4*s.sin(a/2)**2))
    eq(q-2*(q/a)*s.sin(a/2),q*(1-s.sin(a/2)/(a/2)))
    # Series coefficients are exact symbolic equalities, not numerical fits.
    eq(s.limit((1-s.sin(a/2)/(a/2))/a**2,a,0),s.Rational(1,24))
    eq(s.limit((a/2*s.cos(a/2)/s.sin(a/2)-1)/a**2,a,0),-s.Rational(1,12))
    endpoint_normalized_squared=(1-s.sin(a)/a)**2+((1-s.cos(a))/a)**2
    eq(s.limit(endpoint_normalized_squared/a**2,a,0),s.Rational(1,4))
    eq((2*(q/(2*s.sin(a/2)))*s.sin(a/4)),q/(2*s.cos(a/4)))
    v=1.5; h=.02; rho=2.7/np.tan(.6); alpha=v*h/rho; N=round(2*np.pi/alpha)
    n=np.arange(N+1); theta=n*alpha
    positions=np.zeros((N+1,2)); positions[1:]=np.cumsum(v*h*np.column_stack((np.cos(theta[:-1]),np.sin(theta[:-1]))),axis=0)
    center=np.array([v*h/2,v*h/(2*np.tan(alpha/2))]); RE=v*h/(2*np.sin(alpha/2))
    circle_error=float(np.max(np.abs(np.linalg.norm(positions-center,axis=1)-RE)))
    closure=float(np.linalg.norm(positions[-1])); closure_formula=2*RE*abs(np.sin(N*alpha/2))
    assert abs(closure-closure_formula)<1e-10 and circle_error<1e-10
    assert closure<1.5*abs(v)*h
    # Randomized sign, speed, radius and step sizes; nearest integer closure.
    rng=np.random.default_rng(20261019); err=0.; ratio=0.
    for _ in range(3000):
        vv=rng.uniform(.01,1.5)*rng.choice([-1,1]); rr=rng.uniform(3.9,30)*rng.choice([-1,1]); hh=rng.uniform(.001,.02)
        aa=vv*hh/rr; nn=round(2*np.pi/abs(aa)); re=abs(vv*hh)/(2*abs(np.sin(aa/2)))
        measured=2*re*abs(np.sin(nn*aa/2)); ratio=max(ratio,measured/(abs(vv)*hh))
        bound=abs(vv*hh)/(2*np.cos(abs(aa)/4))
        assert measured<=bound+1e-10
    qn=abs(v*h)
    print('PASS SymPy circle / recurrence / series; NumPy trajectory and 3000 closure cases')
    print(json.dumps(dict(N=N,alpha=alpha,euler_radius=RE,physical_radius=rho,
      circle_radial_max_error=circle_error,chord_length_error=qn-2*rho*np.sin(alpha/2),
      one_step_endpoint_error=float(np.linalg.norm(np.array([qn,0])-np.array([rho*np.sin(alpha),rho*(1-np.cos(alpha))]))),
      closure=closure,closure_formula_error=abs(closure-closure_formula),closure_bound=1.5*qn,
      random_max_closure_step_ratio=ratio),sort_keys=True))

if __name__=='__main__': main()
