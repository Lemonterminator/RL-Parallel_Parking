"""Euclidean separation and translational penetration, checked against GEOS."""
import json
import sympy as s
import numpy as np
from shapely.geometry import Polygon,MultiPoint,Point

def eq(a,b): assert s.simplify(s.trigsimp(a-b))==0

def box(center,half,angle):
    p=np.array([[-1,-1],[1,-1],[1,1],[-1,1]])*half
    R=np.array([[np.cos(angle),-np.sin(angle)],[np.sin(angle),np.cos(angle)]])
    return p@R.T+center

def axes(p):
    e=np.roll(p,-1,axis=0)-p
    return np.column_stack((-e[:,1],e[:,0]))/np.linalg.norm(e,axis=1)[:,None]

def vertex_edges(p,q):
    best=np.inf
    for a in p:
        for b,c in zip(q,np.roll(q,-1,axis=0)):
            u=c-b; t=np.clip(np.dot(a-b,u)/np.dot(u,u),0,1)
            best=min(best,np.linalg.norm(a-b-t*u))
    return best

def signed_distance(p,q):
    gaps=[]; depths=[]
    for n in np.vstack((axes(p)[:2],axes(q)[:2])):
        a=p@n; b=q@n
        gaps.append(max(b.min()-a.max(),a.min()-b.max()))
        # Directed exit translations; this also handles contained intervals.
        depths.append(min(a.max()-b.min(),b.max()-a.min()))
    if max(gaps)>0:
        return min(vertex_edges(p,q),vertex_edges(q,p)),max(gaps)
    return -min(depths),max(gaps)

def oracle(p,q):
    A=Polygon(p); B=Polygon(q)
    if not A.intersects(B): return A.distance(B)
    # Independent Minkowski configuration obstacle, formed via GEOS convex hull.
    hull=MultiPoint((q[:,None,:]-p[None,:,:]).reshape(-1,2)).convex_hull
    return -hull.boundary.distance(Point(0,0))

def main():
    x,y,t=s.symbols('x y t',real=True)
    ux,uy,lam=s.symbols('ux uy lam',real=True)
    # Complete the point-to-line squared-distance quadratic, then constrain
    # lambda to [0,1] by clipping its unique unconstrained minimizer.
    den=ux**2+uy**2
    tstar=(x*ux+y*uy)/den
    quadratic=(x-lam*ux)**2+(y-lam*uy)**2
    eq(s.diff(quadratic,lam).subs(lam,tstar),0)
    eq(s.diff(quadratic,lam,2),2*den)
    eq(quadratic,den*(lam-tstar)**2+x*x+y*y-(x*ux+y*uy)**2/den)
    alo,ahi,blo,bhi=s.symbols('alo ahi blo bhi',real=True)
    eq(blo+(ahi-blo),ahi)
    eq(bhi-(bhi-alo),alo)
    eq(x*x+y*y-(x*s.cos(t)+y*s.sin(t))**2,(-x*s.sin(t)+y*s.cos(t))**2)
    eq(s.sqrt(1**2+1**2),s.sqrt(2))
    # Rotated square B about (3/2,3/2); the closest vertex is its original SW.
    ang=s.pi/9; bx=s.Rational(3,2)-s.cos(ang)/2+s.sin(ang)/2
    by=s.Rational(3,2)-s.sin(ang)/2-s.cos(ang)/2
    eq(bx**2+by**2,5-3*s.cos(ang))
    A=box(np.array([-.5,-.5]),np.array([.5,.5]),0)
    examples=[]
    for angle in [0,np.deg2rad(20)]:
        B=box(np.array([1.5,1.5]),np.array([.5,.5]),angle)
        dist,gap=signed_distance(A,B); ref=oracle(A,B)
        assert gap<dist and abs(dist-ref)<1e-12
        examples.append(dict(rotation_deg=np.rad2deg(angle),distance=dist,SAT_gap=gap,shapely=ref))
    assert abs(examples[1]['distance']-float(s.sqrt(5-3*s.cos(ang)) ))<1e-12
    big=box(np.zeros(2),np.array([2.,2.]),0); small=box(np.zeros(2),np.ones(2),0)
    containment=signed_distance(big,small)[0]; assert abs(containment+3)<1e-12
    rng=np.random.default_rng(20261019); err=0.; separated=overlap=contained=0
    for _ in range(2000):
        p=box(rng.uniform(-3,3,2),rng.uniform(.1,2,2),rng.uniform(-np.pi,np.pi))
        q=box(rng.uniform(-3,3,2),rng.uniform(.1,2,2),rng.uniform(-np.pi,np.pi))
        d,g=signed_distance(p,q); ref=oracle(p,q); err=max(err,abs(d-ref))
        if d>0: separated+=1; assert g<=d+1e-12
        else: overlap+=1
        contained+=int(Polygon(p).contains(Polygon(q)) or Polygon(q).contains(Polygon(p)))
    assert err<1e-10
    print('PASS SymPy projection identity; Shapely distance / Minkowski penetration oracle')
    print(json.dumps(dict(examples=examples,containment_signed_distance=containment,
       random_cases=2000,separated=separated,overlap=overlap,contained=contained,max_error=err),sort_keys=True))

if __name__=='__main__': main()
