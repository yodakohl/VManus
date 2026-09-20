"""Post-run human-readable census; no new search or changed scientific model."""
import collections,csv,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2];A=E/'artifacts'
def read(p):return json.loads(p.read_text())
cfg=read(E/'src/SPEC.json');rows=read(A/'ROWS.json');pred=read(A/'PREDICTIONS.json');g=read(R/cfg['grammar']);lex={x['raw']:x['symbol'] for x in read(R/cfg['source_draft'])['lexicon']}
# The sole singleton is already forced by the old mandatory initial syntax.
p=pred[1]['paragraphs'][0];assert p['words'][3]=='shodol' and g['patterns']['INITIAL'][3]=='@Agent' and g['types']['Agent']==['M']
proof=dict(word='shodol',value='M',source=p['id'],position=4,reason='Mandatory INITIAL is the only first clause; its fourth terminal is the singleton Agent type. Uniqueness is inherited syntax, not a new semantic identification.')
lines=['# Every projected shared code and complete representative reading','','All values below are hypothetical fixed terminal meanings, not word translations. Every paragraph is shown completely. W/G/C denote anonymous cargo labels here; their conventional source names have no independent support. M is the assumed transporting agent, B the assumed boat. Each tuple has one full representative; its other possible full dictionaries/parses were not exhausted.']
table=[];details=[]
for r,pr in zip(rows,pred):
 assert r['projection']['exhaustive']
 lines+=['',f"## {r['id']} — {len(r['tuples'])} complete shared tuples",'']
 for i,t in enumerate(r['tuples'],1):
  ident=r['id']+'-T'+str(i).zfill(2);w=t['witness'];vc=[v['variant_id'] for v in w['variant_checks'] if v['joint_coherent']];full={**lex,**w['aliases']};positive=[]
  thenforms=sorted(k for k,v in w['aliases'].items() if v=='THEN')
  lines+=['',f"### {ident}: "+', '.join(k+'='+v for k,v in t['values'].items()),'',f"Coherent variants for this representative: {', '.join(vc)}. New whole-word aliases: {len(w['aliases'])}; distinct new THEN aliases: {len(thenforms)}."]
  for p,parsed,rp in zip(pr['paragraphs'],w['parses'],w['replays']):
   paths=[q for q in rp['paths'] if q['consistent']];assert paths
   stats=dict(member=p['id'],groups=len(p['words']),strict_anchor_eligible=p['strict_anchor_eligible'],cargo=rp['program']['cargo'],voyages=sorted(set(len(x['trace'])-1 for x in paths)),hazard_pairs=len(rp['program']['hazards']),then_positions=sum(n['kind']=='THEN' for n in parsed))
   positive.append(stats)
   lines+=['',p['id'], '',f"Source flag: {p['strict_anchor_eligible']}; cargo: {','.join(stats['cargo'])}; voyages: {stats['voyages']}; hazard pairs: {stats['hazard_pairs']}.",'','| Written groups, complete clause | Assumed fixed interpretation |','|---|---|']
   for n in parsed:
    assert [full[x] for x in p['words'][n['start']:n['end']]]==n['symbols']
    lines.append('| '+' '.join(p['words'][n['start']:n['end']])+' | '+n['kind']+': '+' '.join(n['symbols'])+' |')
   for path in paths:
    lines+=['','Complete successful path: '+' → '.join(('initial' if j==0 else 'load '+str(st['load']))+' ['+', '.join(k+'='+v for k,v in sorted(st['positions'].items()))+']' for j,st in enumerate(path['trace']))+'.']
  failed=[v for v in w['variant_checks'] if not v['joint_coherent']]
  lines+=['','Other variants: '+('none fail this representative.' if not failed else '; '.join(v['variant_id']+': '+', '.join(p['id']+' '+p['status']+(' '+p['error'] if 'error' in p else '') for p in v['paragraphs'] if p['status']!='COHERENT') for v in failed))+ ' Every full failed path remains in ROWS.json.']
  d=dict(id=ident,system=r['id'],values=t['values'],new_aliases=len(w['aliases']),new_then_aliases=thenforms,representative_coherent_variants=vc,paragraphs=positive);details.append(d)
  table.append([ident,r['id'],json.dumps(t['values'],sort_keys=True),len(w['aliases']),len(thenforms),','.join(vc),';'.join(p['member']+':'+str(len(p['cargo']))+'cargo/'+','.join(map(str,p['voyages']))+'trips' for p in positive),0])
(A/'READINGS.md').write_text('\n'.join(lines)+'\n')
with (A/'SHARED_TUPLES.tsv').open('w',newline='') as f:
 w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['id','system','shared_values','new_aliases','new_then_types','coherent_variants_for_representative','world_sizes','independent_meaning_capacity']);w.writerows(table)
out=dict(status='PASS',scope='Post-run direct census and inherited singleton certificate; no added model search',inherited_singleton=proof,tuples=details,tuple_count=len(details),two_cargo_representatives=sum(any(len(p['cargo'])==2 for p in d['paragraphs']) for d in details),hazard_pairs=sum(p['hazard_pairs'] for d in details for p in d['paragraphs']),new_alias_range=[min(d['new_aliases'] for d in details),max(d['new_aliases'] for d in details)],new_then_type_range=[min(len(d['new_then_aliases']) for d in details),max(len(d['new_then_aliases']) for d in details)])
(A/'EXPLANATIONS.json').write_text(json.dumps(out,separators=(',',':'))+'\n');print(json.dumps({k:v for k,v in out.items() if k!='tuples'},indent=2))
