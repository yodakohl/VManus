"""Independent rigorous sign relaxation; no input-file access.

Machin's pi formula uses alternating-series enclosures. Taylor remainders
bound sin/cos on the complete angular interval; integer quantization rounds
outward. Determinants use interval arithmetic, hence dependency only enlarges
the possible sign set. For four augmented rows [v,1], anchor subtraction
gives MINUS det(v1-v0,v2-v0,v3-v0). This sign is shared by sphere and lift.
Sign compatibility is necessary, never a continuous-map existence proof.
"""
from fractions import Fraction as F
from functools import lru_cache
from itertools import permutations
from math import factorial

SCALE = 10**12

def add(a, b):
    return a[0]+b[0], a[1]+b[1]

def neg(a):
    return -a[1], -a[0]

def sub(a, b):
    return add(a, neg(b))

def mul(a, b):
    p = [x*y for x in a for y in b]
    return min(p), max(p)

def square(a):
    return (0 if a[0] <= 0 <= a[1] else min(a[0]**2,a[1]**2),
            max(a[0]**2,a[1]**2))

def signs(a):
    return frozenset(s for s, yes in ((-1,a[0]<0),(0,a[0]<=0<=a[1]),(1,a[1]>0)) if yes)

@lru_cache(None)
def pi_interval():
    def atan_recip(q):
        n = 40
        total = sum((F((-1)**k, (2*k+1)*q**(2*k+1)) for k in range(n)), F(0))
        remainder = F(1, (2*n+1)*q**(2*n+1))
        # n is even: next term is positive.
        return total, total+remainder
    return sub(mul((16,16),atan_recip(5)),mul((4,4),atan_recip(239)))

def trig_interval(x, cosine=False):
    """Degree 60/61 Taylor polynomial, with Lagrange error bound."""
    x2 = square(x)
    result = (F(0),F(0))
    # Horner in x²: cos through degree 60, sin through degree 61.
    for k in range(30,-1,-1):
        coefficient = F((-1)**k, factorial(2*k+(not cosine)))
        result = add(mul(result,x2),(coefficient,coefficient))
    if not cosine:
        result = mul(result,x)
    degree = 62 if cosine else 63
    radius = max(abs(x[0]),abs(x[1]))
    error = radius**degree / factorial(degree)
    return add(result,(-error,error))

def _quantize(a):
    lo, hi = a[0]*SCALE, a[1]*SCALE
    return lo.numerator//lo.denominator, -((-hi.numerator)//hi.denominator)

@lru_cache(None)
def source_vector(lon_arcmin, lat_arcmin):
    """Integer arcminutes; longitude periodic, latitude in [-90°,90°]."""
    if type(lon_arcmin) is not int or type(lat_arcmin) is not int:
        raise TypeError('angles must be integer arcminutes')
    if not -5400 <= lat_arcmin <= 5400:
        raise ValueError('latitude outside sphere coordinates')
    lon_arcmin = (lon_arcmin+10800)%21600-10800
    lon = mul(pi_interval(),(F(lon_arcmin,10800),)*2)
    lat = mul(pi_interval(),(F(lat_arcmin,10800),)*2)
    clat = trig_interval(lat,True)
    return tuple(map(_quantize,(mul(clat,trig_interval(lon,True)),
                                mul(clat,trig_interval(lon)),trig_interval(lat))))

def determinant3(rows):
    total = (0,0)
    for p in permutations(range(3)):
        value = (1,1)
        for i in range(3):
            value = mul(value, rows[i][p[i]])
        inversions = sum(p[i]>p[j] for i in range(3) for j in range(i+1,3))
        total = add(total, neg(value) if inversions%2 else value)
    return total

def augmented_determinant4(rows):
    if len(rows) != 4:
        raise ValueError('four rows required')
    differences = [tuple(sub(r[k],rows[0][k]) for k in range(3)) for r in rows[1:]]
    return neg(determinant3(differences))

def source_sign(vectors):
    if len(vectors) == 3:
        return signs(determinant3(vectors))
    if len(vectors) == 4:
        return signs(augmented_determinant4(vectors))
    raise ValueError('three or four source vectors required')

def target_sign(boxes, mode='gnomonic'):
    rows = []
    for xmin,ymin,xmax,ymax in boxes:
        if any(type(v) not in (int,F) for v in (xmin,ymin,xmax,ymax)):
            raise TypeError('bounding-box endpoints must be exact int or Fraction')
        if xmin>xmax or ymin>ymax:
            raise ValueError('reversed bounding box')
        x,y = (xmin,xmax),(ymin,ymax)
        rows.append((x,y,(1,1) if mode=='gnomonic' else add(square(x),square(y))))
    if mode=='gnomonic' and len(rows)==3:
        return signs(determinant3(rows))
    if mode=='stereographic' and len(rows)==4:
        return signs(augmented_determinant4(rows))
    raise ValueError('mode/count mismatch')

def selftest():
    pi = pi_interval()
    assert pi[0] > F(314159265358979323846,10**20)
    assert pi[1] < F(314159265358979323847,10**20)
    for lon,lat,want in ((0,0,(1,0,0)),(5400,0,(0,1,0)),(0,5400,(0,0,1)),
                          (10800,0,(-1,0,0)),(-5400,0,(0,-1,0))):
        vec=source_vector(lon,lat)
        assert all(lo<=v*SCALE<=hi for (lo,hi),v in zip(vec,want))
        assert all(hi-lo<=2 for lo,hi in vec)
    assert source_sign([source_vector(0,0),source_vector(5400,0),source_vector(0,5400)])=={1}
    point=lambda x,y:(x,y,x,y)
    assert target_sign([point(0,0),point(2,0),point(0,2)])=={1}
    assert target_sign([point(0,0),point(0,2),point(2,0)])=={-1}
    assert target_sign([point(0,0),point(2,0),point(0,2),point(2,2)],'stereographic')=={0}
    # Exact inverse stereographic identity, including its positive factor.
    points=[(F(0),F(0)),(F(2),F(0)),(F(0),F(2)),(F(1,2),F(1,2))]
    spheres=[]; lifts=[]; denom=F(1)
    for x,y in points:
        r=x*x+y*y; denom*=1+r
        spheres.append(tuple((z,z) for z in (2*x/(1+r),2*y/(1+r),(r-1)/(1+r))))
        lifts.append(tuple((z,z) for z in (x,y,r)))
    ds=augmented_determinant4(spheres); dt=augmented_determinant4(lifts)
    assert ds[0]==ds[1]==8*dt[0]/denom and ds[0]!=0
    assert target_sign([(0,0,1,1)]*3)=={-1,0,1}
    for bad in (0.0,False):
        try:
            target_sign([(bad,0,0,0)]*3)
        except TypeError:
            pass
        else:
            raise AssertionError('inexact or Boolean coordinate accepted')
    return {'status':'PASS','scope':'synthetic arithmetic and determinant identities only'}

if __name__=='__main__':
    print(selftest())
