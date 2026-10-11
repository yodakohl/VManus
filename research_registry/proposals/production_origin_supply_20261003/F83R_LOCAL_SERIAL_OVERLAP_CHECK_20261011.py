from pathlib import Path
import gzip,hashlib,itertools,json
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent
review=P/'F83R_LOCAL_SERIAL_OVERLAP_REVIEW_20261011.json';r=json.loads(review.read_text())
for p,h in r['inputs'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
D=('a','c');same=0;different=0
for bits in itertools.product((0,1),repeat=2):
 pred={x for x,b in zip(D,bits) if b}
 for first,second in itertools.product(D,repeat=2):
  local=(first in pred,second in pred);serial=(first in pred,first in pred)
  if local==serial:same+=1
  else:different+=1
assert (same,different)==(12,4)
assert (True,True)==('a' in {'a'},'a' in {'a'})
assert ('a' in {'a'},'c' in {'a'})!=('a' in {'a'},'a' in {'a'})
# Different state stores are irrelevant when the output never reads them.
for size in range(9):
 local=[];serial=[];memory=[]
 for i in range(size):
  obj=D[i%2];local.append(obj=='a');memory.append(obj);serial.append(obj=='a')
 assert local==serial
# Exact typed consumer. The depicted Person cannot supply a produced Result.
produced=('Result','v');image={'figure':('Person','a')}
def consume(store):
 v=store.get('r');return v if v and v[0]=='Result' else None
assert consume(dict(image)) is None
assert consume(dict(image,r=produced))==produced
# An explicit import is a distinct permitted rival, not proof of persistence.
assert consume(dict(image,r=produced))==consume({'r':produced})
packet=P/'THREE_MODELS_F83R_SOURCE_20261011.json.gz';rows=json.loads(gzip.decompress(packet.read_bytes()))['rows'];obs={}
for ed in ['ZL3b','IT2a','RF1b']:
 selected=[]
 for locus,word in [('f83r.1','tchedy'),('f83r.16','tchedy'),('f83r.23','tchedy'),('f83r.20','solkeedy'),('f83r.21','solkeedy')]:
  row=next(x for x in rows if x['edition']==ed and x['locus']==locus and int(x['source_group_index'])==1);assert row['ivtff_group_raw']==word;selected.append({'locus':locus,'raw':word,'source_group_index':row['source_group_index'],'paragraph_start_raw':row['paragraph_start']})
 obs[ed]=selected
 if ed!='RF1b':assert [x['paragraph_start_raw'] for x in selected[:3]]==['1','0','0']
out={'status':'PASS_FINITE_COUNTEREXAMPLES_AND_CACHED_POINTERS_ONLY','proof_input_sha256':hashlib.sha256(review.read_bytes()).hexdigest(),'cached_packet_sha256':hashlib.sha256(packet.read_bytes()).hexdigest(),'finite_scope_cases':{'same':same,'different':different,'not_probabilities':True},'typed_fixed_contrast':{'reset_without_import':'missing_Result','carry':'resolves_Result','explicit_import_rival':'also_resolves_Result'},'cached_reference_candidates':obs,'limits':'No native semantic score, universal local/serial equivalence, new world evidence or translation. RF paragraph flags remain unscorable; five selected pointers do not exhaust possible references.'};(P/'F83R_LOCAL_SERIAL_OVERLAP_RESULT_20261011.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'status':out['status'],'finite_cases':16,'cached_pointers':15,'new_meanings':0}))
