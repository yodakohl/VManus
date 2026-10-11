from pathlib import Path
import csv,gzip,hashlib,io,json,subprocess
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent
trial=json.loads((P/'THREE_BIG_MODELS_TRIAL_20261011.json').read_text())
for p,h in trial['input_hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
pack=json.loads(gzip.decompress((P/'THREE_MODELS_F83R_SOURCE_20261011.json.gz').read_bytes()));assert hashlib.sha256((R/pack['source']).read_bytes()).hexdigest()==pack['source_sha256'];assert pack['command'][pack['command'].index('--allow')+1]=='f83r' and pack['command'][pack['command'].index('--selector')+1]=='page'
x=subprocess.run(pack['command'],cwd=R,text=True,capture_output=True,check=True);lines=[l for l in x.stdout.splitlines() if not l.startswith('GUARD_STATS ')];rows=list(csv.DictReader(io.StringIO('\n'.join(lines)),delimiter='\t'));assert rows==pack['rows'];assert all(r['page']=='f83r' for r in rows)
counts={}
for ed in ['ZL3b','IT2a','RF1b']:
 counts[ed]={}
 for name,(a,b) in trial['blocks'].items():counts[ed][name]=sum(r['edition']==ed and r['locus'] in {f'f83r.{i}' for i in range(a,b+1)} for r in rows)
 repeat=sorted([r for r in rows if r['edition']==ed and r['locus']=='f83r.7'],key=lambda r:int(r['source_group_index']));assert [r['ivtff_group_raw'] for r in repeat[-2:]]==['qoteedy','qoteedy'];assert int(repeat[-1]['source_group_index'])==int(repeat[-2]['source_group_index'])+1 and repeat[-1]['left_separator']=='DEFINITE_SPACE'
assert counts==trial['exact_raw_counts_by_reader']
for ed,raw in [('ZL3b','sasoldal'),('IT2a','saroldal'),('RF1b','s@221;roldal')]:assert [r['ivtff_group_raw'] for r in rows if r['edition']==ed and r['locus']=='f83r.50']==[raw]
base={'object':'A','vessel':'V','interval':1};first=dict(base,vessel='W');independent=dict(base,interval=2);chained=dict(first,interval=2);assert independent['vessel']=='V' and chained['vessel']=='W' and base['vessel']=='V'
out={'status':'PASS_SOURCE_ACCOUNTING_AND_SYNTHETIC_SCOPE_EXAMPLE_ONLY','source_groups':len(rows),'reader_block_accounts':21,'new_meanings':0,'meaning_validation':False,'scope':'Exact guarded recollation, input hashes, full-page block counts, retained repeated forms and caption variants; synthetic immutable-base versus chained example. No semantic winner, ink validation, glyph renderer or full statistical fit.'};(P/'THREE_BIG_MODELS_VALIDATION_20261011.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
