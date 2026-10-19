"""Three subrectangle circumcircles cover the rear-axle body rectangle."""
import json
import sympy as s
import numpy as np

def eq(a,b): assert s.simplify(a-b)==0

def main():
    length,w,r=s.symbols('length w r',positive=True)
    radius=s.sqrt((length/6)**2+(w/2)**2)
    eq(radius**2,length**2/36+w**2/4)
    for i in range(3):
        center=-r+(s.Rational(i,3)+s.Rational(1,6))*length
        left=-r+s.Rational(i,3)*length; right=left+length/3
        eq(center-left,length/6); eq(right-center,length/6)
        eq((left-center)**2+(w/2)**2,radius**2)
        eq((right-center)**2+(w/2)**2,radius**2)
    ell=4.7; ww=1.85; rr=1.1
    centers=-rr+(np.arange(3)+.5)*ell/3; rad=np.hypot(ell/6,ww/2)
    rng=np.random.default_rng(20261019)
    p=rng.uniform([-rr,-ww/2],[ell-rr,ww/2],size=(200000,2))
    # Include every subrectangle corner, where the bound is attained exactly.
    corners=np.array([[xx,yy] for xx in np.linspace(-rr,ell-rr,4) for yy in [-ww/2,ww/2]])
    p=np.vstack((p,corners)); idx=np.minimum((3*(p[:,0]+rr)/ell).astype(int),2)
    d2=(p[:,0]-centers[idx])**2+p[:,1]**2
    excess=float(np.max(d2-rad**2)); assert excess<2e-14
    print('PASS SymPy corner equalities; analytic interval-square proof in report and Lean')
    print(json.dumps(dict(radius=rad,radius_squared=rad**2,centers=centers.tolist(),
                         samples=len(p),max_squared_excess=excess,
                         corner_max_radius_error=float(np.max(np.abs(np.min(np.hypot(corners[:,0,None]-centers,corners[:,1,None]),axis=1)-rad)))),sort_keys=True))

if __name__=='__main__': main()
