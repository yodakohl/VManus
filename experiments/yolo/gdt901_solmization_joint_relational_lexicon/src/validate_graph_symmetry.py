"""Source-only typed-relation automorphism audit; no target inputs.
Stable color refinement preserves every type/argument-position automorphism.
Exhaustive residual permutations certify the count; a cap reports UNKNOWN.
"""
import argparse,json,hashlib,itertools,time,math
from pathlib import Path
parser=argparse.ArgumentParser()
base=Path(__file__).resolve().parents[1]
parser.add_argument('--input',type=Path,default=base/'artifacts/SOURCE_INPUT.json')
parser.add_argument('--output',type=Path,default=base/'artifacts/SOURCE_SYMMETRY.json')
a=parser.parse_args()
raw=a.input.read_bytes(); packet=json.loads(raw)
data=packet.get('source_graph',packet)
rows=[(p['id'],[(m['voice'],m['origin']) for m in p['memberships']]) for p in data['pitches']]
origins={o['id']:o['cantus_type'] for o in data['origins']}
mutations=data['mutations']
# Typed relational structure, names are never colors.
entities={**{'P:'+p:'pitch' for p,vs in rows},**{'V:'+v:'voice' for v in data['voices']},**{'H:'+h:'origin' for h in origins},**{'T:'+t:'cantus_type' for t in set(origins.values())}}
rels=[]
for p,vs in rows:
 for v,h in vs:rels.append(('membership',('P:'+p,'V:'+v,'H:'+h)))
 if len(vs)==1:rels.append(('zero',('P:'+p,)))
for h,t in origins.items():rels.extend([('origin_pitch',('H:'+h,'P:'+h)),('cantus',('H:'+h,'T:'+t))])
for m in mutations:rels.append(('mutation_'+m['direction'],tuple(prefix+m[key] for prefix,key in [('P:','pitch'),('V:','from_voice'),('H:','from_origin'),('V:','to_voice'),('H:','to_origin')])))
colors={x:t for x,t in entities.items()}
for iteration in range(100):
 sig={x:(colors[x],tuple(sorted((name,k,tuple(colors[y] for y in args)) for name,args in rels for k,y in enumerate(args) if x==y))) for x in entities}
 labels={s:i for i,s in enumerate(sorted(set(sig.values()),key=repr))}
 new={x:labels[sig[x]] for x in entities}
 if len(set(new.values()))==len(set(colors.values())):colors=new;break
 colors=new
classes=[[x for x in entities if colors[x]==c] for c in sorted(set(colors.values()))]
space=1
import math
for c in classes:space*=math.factorial(len(c))
rs=set(rels);autos=[];status='COMPLETE';start=time.monotonic()
if space>1000000:status='UNKNOWN_RESIDUAL_CAP'
else:
 for choices in itertools.product(*(itertools.permutations(c) for c in classes)):
  mapping={a:b for c,perm in zip(classes,choices) for a,b in zip(c,perm)}
  if {(name,tuple(mapping[x] for x in args)) for name,args in rels}==rs:autos.append({x:y for x,y in mapping.items() if x!=y})
result={'status':status,'pitch_count':len(rows),'membership_count':sum(len(vs) for p,vs in rows),'mutation_count':len(mutations),'zero_records':sum(len(vs)==1 for p,vs in rows),'entity_count':len(entities),'refinement_rounds':iteration+1,'residual_classes':[c for c in classes if len(c)>1],'residual_permutations':space,'automorphism_count':len(autos) if status=='COMPLETE' else None,'nonidentity_maps':[a for a in autos if a],'scope':data['graph_scope'],'meaning':'Source graph rigidity only; no target encoding, observation, or identification established.'}

result['input_sha256']=hashlib.sha256(raw).hexdigest()
result['auditor_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
# Independently parse the typed compiler stream. No source-record lengths used.
if 'records' in packet:
    reconstructed=[]; reconstructed_mutations=[]; observed_origins={}; zero=[]
    for record in packet['records']:
        seq=record['sequence']; head=seq[0]
        assert head.startswith('PITCH:') and head==record['head_atom']
        pitch=head[6:]; i=1; memberships=[]
        def origin(atom):
            assert atom=='SELF' or atom.startswith('PITCH:')
            return pitch if atom=='SELF' else atom[6:]
        while i+1<len(seq) and seq[i].startswith('VOICE:') and seq[i+1].startswith('CANTUS:'):
            voice=seq[i][6:]; typ=seq[i+1][7:]; h=origin(seq[i+2])
            assert h not in observed_origins or observed_origins[h]==typ
            observed_origins[h]=typ; memberships.append((voice,h)); i+=3
        vm=dict(memberships); assert len(vm)==len(memberships)
        if seq[i:]==['ZERO']:
            zero.append(pitch);i+=1
        else:
            while i<len(seq):
                f,t,d,c,h=seq[i:i+5]
                assert f.startswith('VOICE:') and t.startswith('VOICE:') and d.startswith('DIRECTION:') and c.startswith('CANTUS:')
                f=f[6:];t=t[6:];h=origin(h)
                assert vm[t]==h and observed_origins[h]==c[7:]
                reconstructed_mutations.append(dict(pitch=pitch,from_voice=f,from_origin=vm[f],to_voice=t,to_origin=h,direction=d[10:]))
                i+=5
        assert i==len(seq)
        reconstructed.append((pitch,memberships))
    assert reconstructed==rows
    assert reconstructed_mutations==mutations
    assert observed_origins==origins
    assert set(zero)=={p['id'] for p in data['pitches'] if p['zero_explicit']}
    assert all(o['origin_pitch']==o['id'] for o in data['origins'])
    result['compiler_roundtrip']='PASS_MEMBERSHIPS_MUTATIONS_ORIGIN_PITCH_CANTUS_ZERO'
    result['prohibition_scope']='Cross-pitch mutation prohibition is a semantic grammar axiom, not an emitted negative-list token; flat/square names remain distinct pitch nodes. Rigidity claim does not require explicit-prohibition edges.'
else:
    result['compiler_roundtrip']='NOT_CHECKED_GRAPH_ONLY_INPUT'
a.output.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
