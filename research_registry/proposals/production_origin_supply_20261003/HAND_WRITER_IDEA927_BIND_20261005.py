"""Bind an already reported conditional countercase; no new census or decoder."""
from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
C=P/'HAND_WRITER_IDEA927_CONTRACT_20261005.json';OUT=P/'HAND_WRITER_IDEA927_RESULT_20261005.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 c=json.loads(C.read_text())
 for name,h in c['files'].items():assert sha(ROOT/name)==h,name
 D=ROOT/'experiments/yolo/gdt851_primitive_tandem_raw_group_discovery'
 hits=json.loads((D/'artifacts/HITS.json').read_text());sources={e:json.loads((D/f'artifacts/SOURCE_{e}.json').read_text()) for e in c['editions']}
 pools={form:{e:{} for e in c['editions']} for form in c['target_forms']}
 for h in hits:
  if h['period']!=1 or len(h['groups'])!=2 or h['groups'][0] not in pools:continue
  form=h['groups'][0];assert h['groups']==[form,form]
  e=h['edition'];s=sources[e];line=s['lines'][h['line_array_index']];m=line['metadata'];assert m['locus']==h['locus'] and not m['page'].startswith('f84')
  gg=[dict(zip(s['group_columns'],g)) for g in line['groups']];byid={g['source_group_id']:i for i,g in enumerate(gg)};inds=[byid[x] for x in h['source_ids']];i,j=inds
  assert j==i+1 and int(gg[j]['source_group_index'])==int(gg[i]['source_group_index'])+1
  assert [gg[z]['ivtff_group_raw'] for z in inds]==[form,form]
  if gg[i]['right_separator']!='DEFINITE_SPACE' or gg[j]['left_separator']!='DEFINITE_SPACE':continue
  left=gg[i]['left_separator']=='LINE_START' if i==0 else gg[i-1]['right_separator']==gg[i]['left_separator']=='DEFINITE_SPACE'
  right=gg[j]['right_separator']=='LINE_END' if j==len(gg)-1 else gg[j]['right_separator']==gg[j+1]['left_separator']=='DEFINITE_SPACE'
  if not(left and right):continue
  pools[form][e][(h['locus'],int(h['start_index']))]={'edition':e,'hit':h,'metadata':m,'groups':gg,'target_array_indices':inds}
 selected=[]
 for form in c['target_forms']:
  keys=set.intersection(*(set(pools[form][e]) for e in c['editions']))
  if not keys:selected.append({'form':form,'status':'NO_SHARED_ELIGIBLE_ANCHOR'});continue
  k=min(keys);selected.append({'form':form,'status':'BOUND','locus':k[0],'start_index':k[1],'literal_initial':form[0],'literal_sign_count':len(form),'readings':[pools[form][e][k] for e in c['editions']]})
 bound=[x for x in selected if x['status']=='BOUND'];initials=sorted({x['literal_initial'] for x in bound if x['literal_sign_count']>1})
 status='LITERAL_ATOM_PREFIX_COPY_CONTRADICTED' if len(initials)>1 else 'INSUFFICIENT_BOUND_COUNTERCASE'
 result={'status':status,'contract_sha256':sha(C),'runner_sha256':sha(Path(__file__)),'anchors':selected,'distinct_literal_initials':initials,'necessity':'Every same-line exact adjacent multicharacter output doublet must start with the same single H4 atom under the fixed mandatory cap4 rule.','literal_atom_binding_assumed':True,'native_atoms_proven':False,'meanings_assigned':0,'new_manuscript_discovery':False,'new_frequency_census':False,'independent_confirmation_capacity':0}
 OUT.write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({'status':status,'anchors':[{k:x.get(k) for k in ['form','status','locus','start_index','literal_initial']} for x in selected],'conditional_on':'literal atomic signs and complete group/line binding'},indent=2))
if __name__=='__main__':main()
