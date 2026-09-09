"""Freeze complete interval-sign tensors, without joint correspondence search."""
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import geometry_reference as ref

ROOT = Path(__file__).resolve().parents[1]

def plus(a,b): return (a[0]+b[0],a[1]+b[1])
def minus(a,b): return (a[0]-b[1],a[1]-b[0])
def times(a,b):
    z=(a[0]*b[0],a[0]*b[1],a[1]*b[0],a[1]*b[1]);return min(z),max(z)
def sq(a): return (0 if a[0]<=0<=a[1] else min(a[0]**2,a[1]**2),max(a[0]**2,a[1]**2))
def det2(a,b): return minus(times(a[0],b[1]),times(a[1],b[0]))
def det3(r):
    a=times(r[0][0],det2((r[1][1],r[1][2]),(r[2][1],r[2][2])))
    b=times(r[0][1],det2((r[1][0],r[1][2]),(r[2][0],r[2][2])))
    c=times(r[0][2],det2((r[1][0],r[1][1]),(r[2][0],r[2][1])))
    return plus(minus(a,b),c)
def mask_interval(a): return (1 if a[0]<0 else 0)|(2 if a[0]<=0<=a[1] else 0)|(4 if a[1]>0 else 0)
def flip(m): return ((m&1)<<2)|(m&2)|((m&4)>>2)
def flat(t,n):
    z=0
    for x in t:z=z*n+x
    return z
def target_mask(boxes,mode):
    for box in boxes:
        if len(box)!=4 or any(type(v) is not int for v in box):raise TypeError('integer boxes required')
        if box[0]>box[2] or box[1]>box[3]:raise ValueError('reversed box')
    anchor=boxes[0];rows=[]
    for b in boxes[1:]:
        x=minus((b[0],b[2]),(anchor[0],anchor[2]));y=minus((b[1],b[3]),(anchor[1],anchor[3]))
        rows.append((x,y,plus(sq(x),sq(y))))
    if mode=='gnomonic' and len(boxes)==3:return mask_interval(det2(rows[0],rows[1]))
    if mode=='stereographic' and len(boxes)==4:
        lo,hi=det3(rows);return mask_interval((-hi,-lo))
    raise ValueError('mode/count mismatch')
def tensor(n,k,calculate):
    out=[0]*(n**k)
    for combo in itertools.combinations(range(n),k):
        m=calculate(combo)
        for perm in itertools.permutations(range(k)):
            parity=sum(perm[i]>perm[j] for i in range(k) for j in range(i+1,k))%2
            out[flat(tuple(combo[i] for i in perm),n)]=flip(m) if parity else m
    return out
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def build():
    source_path=ROOT/'artifacts/SOURCE_UNITS.json'; target_path=ROOT/'artifacts/TARGET_INVENTORY.json'
    src=json.loads(source_path.read_text());target=json.loads(target_path.read_text())
    records={r['id']:r for r in src['records']}
    field=target['fields']['LEFT'];alternatives=[('LEFT29',field['definite']),('LEFT30',field['definite']+field['uncertain'])]
    cases=[];sources={};targets={}
    for target_id,objects in alternatives:
        n=len(objects)
        boxes=[(o['bbox'][0]*7993,o['bbox'][1]*3828,o['bbox'][2]*7993,o['bbox'][3]*3828) for o in objects]
        for mode,k in [('gnomonic',3),('stereographic',4)]:
            tm=tensor(n,k,lambda t:target_mask([boxes[i] for i in t],mode))
            targets[target_id+':'+mode]={'objects':[o['id'] for o in objects],'boxes':boxes}
            for unit in src['units']:
                if len(unit['member_ids'])!=n:continue
                vectors=[ref.source_vector(records[i]['longitude_arcmin'],records[i]['latitude_arcmin']) for i in unit['member_ids']]
                sm=tensor(n,k,lambda t:sum({-1:1,0:2,1:4}[s] for s in ref.source_sign([vectors[i] for i in t])))
                case_id=target_id+'|'+unit['case_id']+'|'+mode
                cases.append({'case_id':case_id,'source_case':unit['case_id'],'target_id':target_id,'mode':mode,'n':n,'source_masks':sm,'target_masks':tm})
                sources[unit['case_id']]={'member_ids':unit['member_ids'],'vectors':vectors}
                print('prepared',case_id,flush=True)
    return {'schema':'GDT897_SEARCH_PACKET_V1','source_sha256':sha(source_path),'target_sha256':sha(target_path),'mask_encoding':{'negative':1,'zero':2,'positive':4,'repeated_index':0},'flat_index':'left-to-right base n','source_vectors_scale':ref.SCALE,'sources':sources,'targets':targets,'cases':cases,'cardinality':{'MIDDLE':{'definite':59,'source_maximum':max(len(u['member_ids']) for u in src['units']),'status':'UNSAT_CARDINALITY'}}}
def main():
    packet=build();path=ROOT/'artifacts/SEARCH_PACKET.json.gz'
    raw=json.dumps(packet,separators=(',',':'),sort_keys=True).encode()
    path.write_bytes(gzip.compress(raw,mtime=0));print('packet_sha256',sha(path),flush=True)
if __name__=='__main__':main()
