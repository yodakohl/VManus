import csv,json,hashlib
from pathlib import Path
from collections import Counter,defaultdict
D=Path(__file__).parent;S=json.loads((D/'SPEC.json').read_text())
for p,h in S['hashes'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
allowed=set(json.loads(Path(S['allow_source']).read_text())['allowed_selectors']);assert len(allowed)==179 and not any(p.startswith('f84') for p in allowed)
paragraphs=json.loads(Path(S['paragraphs']).read_text());pmap={};roles={};wholelines=[];counts=defaultdict(Counter)
for ed in ['ZL3b','IT2a','RF1b']:counts[ed]['exact_hits']=0
for ed,pp in paragraphs.items():
 for p in pp:
  assert p['page'] in allowed and not p['page'].startswith('f84')
  for line in p['lines']:
   key=(ed,line['locus']);assert key not in pmap;pmap[key]=p
for source in S['role_sources']:
 rmap={}
 for r in csv.DictReader(Path(source).open(),delimiter='\t'):
  assert not r['locus'].startswith('f84')
  rmap.setdefault(r['form'],set()).add(r['role'])
 assert all(len(v)==1 for v in rmap.values())
 roles[Path(source).name.split('_SOURCE')[0]]={k:next(iter(v)) for k,v in rmap.items()}
hits=[];seen=set();packets={}
for source in S['sources']:
 data=json.loads(Path(source).read_text())
 for line in data['lines']:
  m=line['metadata'];assert m['page'] in allowed and not m['page'].startswith('f84')
  key=(m['edition'],m['locus']);assert key not in seen;seen.add(key)
  groups=[dict(zip(data['group_columns'],g)) for g in line['groups']]
  words=[g['ivtff_group_raw'] for g in groups]
  wholelines.append(dict(source=source,metadata=m,groups=groups))
  counts[m['edition']]['lines']+=1;counts[m['edition']]['groups']+=len(groups)
  for i,g in enumerate(groups):
   if g['ivtff_group_raw']!=S['target']:continue
   prev=groups[i-1] if i else None;p=pmap.get(key)
   seam=bool(prev and int(g['source_group_index'])==int(prev['source_group_index'])+1 and prev['right_separator']==g['left_separator']=='DEFINITE_SPACE')
   rs={k:v.get(prev['ivtff_group_raw'],'OPEN') if prev else 'NONE' for k,v in roles.items()}
   capacity={k:bool(p and m['kind']=='P' and seam and role=='ACTION') for k,role in rs.items()}
   h=dict(edition=m['edition'],page=m['page'],locus=m['locus'],kind=m['kind'],group_index=g['source_group_index'],source_id=g['source_group_id'],paragraph=p['id'] if p else 'NO_COMPLETE_PARAGRAPH',old_locus=m['locus']==S['old_locus'],previous=prev['ivtff_group_raw'] if prev else 'NONE',definite_predecessor_seam=seam,role_A=rs['C_A'],role_Q=rs['C_Q'],capacity_A=capacity['C_A'],capacity_Q=capacity['C_Q'],raw_line=' '.join(words))
   hits.append(h);counts[m['edition']]['exact_hits']+=1
   if p:packets[(m['edition'],p['id'])]=dict(edition=m['edition'],**p)
locs={h['locus'] for h in hits}
alternates=[l for l in wholelines if l['metadata']['locus'] in locs]
for h in hits:
 h['same_locus_readings']=';'.join(l['metadata']['edition']+':'+ ' '.join(g['ivtff_group_raw'] for g in l['groups']) for l in alternates if l['metadata']['locus']==h['locus'])
def tab(n,rr,cols):
 with (D/n).open('w') as f:
  w=csv.DictWriter(f,fieldnames=cols+['row_status'],delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(dict(r,row_status='recorded') for r in rr)
tab('OCCURRENCES.tsv',hits,list(hits[0]) if hits else ['edition','page','locus','source_id'])
(D/'CONTEXTS.json').write_text(json.dumps(dict(paragraphs=list(packets.values()),same_locus_source_lines=alternates),ensure_ascii=False,separators=(',',':'))+'\n')
md=['# W45 — sämtliche ysheol-Kontexte','','Exakte ganze Gruppen; alle Lesungen eines Manuskripts. Keine neue Übersetzung.','']
for h in hits:md += ['## '+h['edition']+' '+h['source_id'],'','`'+h['raw_line']+'`','',f"Vorher: {h['previous']}; eindeutige Grenze: {h['definite_predecessor_seam']}; Rollen A/Q: {h['role_A']}/{h['role_Q']}; Absatz: {h['paragraph']}.",'']
for (ed,pid),p in packets.items():
 md+=['## Vollständiger Absatz '+ed+' '+pid,'']
 for line in p['lines']:md += [line['locus']+': `'+ ' '.join(line['words'])+'`','']
md += ['## Alle am Ziellocus verfügbaren Lesungen','']
for line in alternates:md += [line['metadata']['edition']+' '+line['metadata']['locus']+': `'+ ' '.join(g['ivtff_group_raw'] for g in line['groups'])+'`','']
(D/'CONTEXTS.md').write_text('\n'.join(md)+'\n')
result=dict(selector_allowlist=len(allowed),counts={ed:dict(counts[ed]) for ed in ['ZL3b','IT2a','RF1b']},exact_target_rows=len(hits),physical_leaves=sorted({h['page'].split('r')[0].split('v')[0] for h in hits}),additional_loci=sorted({h['locus'] for h in hits if not h['old_locus']}),complete_target_paragraphs=len(packets),eligible_additional_A=sum(h['capacity_A'] and not h['old_locus'] for h in hits),eligible_additional_Q=sum(h['capacity_Q'] and not h['old_locus'] for h in hits),independent_confirmation_capacity=0,new_word_meanings=0,held_access=False)
(D/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
