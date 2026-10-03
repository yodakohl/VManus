"""Deterministic reconciliation accounting; does not judge image truth."""
import hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2];A=E/'artifacts'
ENTRIES=[f'DEV{i:02d}' for i in range(1,6)]
REVIEWERS=['A','B'];WITNESSES=['LATIN','CLM']
REGIONS={'root','stem','leaf','reproductive','accessory'}
FAMILIES={'BUILT_ENCLOSURE','VESSEL_CONTAINER','ATTACHED_ANIMAL_HUMAN','ARTIFICIAL_SUPPORT_TIE_RING','TREATED_CUT_STEM','INTERTWINED_CLOSED_LOOP'}
STATES={'YES','NO','UNKNOWN','UNCERTAIN','CLIPPED','NOT_RECORDED'}

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(n,x):(A/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def support_reasons(support,prefix):
 reasons=[]
 for reviewer in REVIEWERS:
  for witness in WITNESSES:
   state=support.get(reviewer,{}).get(witness,'NOT_RECORDED')
   if state not in STATES:reasons.append(f'{prefix}:{reviewer}:{witness}:INVALID_STATE:{state}')
   elif state!='YES':reasons.append(f'{prefix}:{reviewer}:{witness}:{state}')
 return reasons

def account(entry):
 eid=entry['entry'];signature=entry.get('signature');manual=entry.get('discovery_rejection_reasons',[])
 assert isinstance(manual,list) and all(isinstance(x,str) and x for x in manual)
 reasons=[];checks=[];descriptors=[];regions=[];families=[]
 if signature is None:
  assert manual,f'{eid}: null signature requires explicit discovery rejection reasons'
  reasons.append('NO_DISCOVERY_SIGNATURE')
 else:
  descriptors=signature['descriptors'];assert isinstance(descriptors,list)
  ids=[d['id'] for d in descriptors];assert all(isinstance(x,str) and x for x in ids) and len(set(ids))==len(ids)
  if len(descriptors)<3:reasons.append('FEWER_THAN_THREE_DESCRIPTORS')
  for d in descriptors:
   did=d['id'];region=d['region'];family=d.get('exception_family')
   if region not in REGIONS:reasons.append(f'INVALID_REGION:{did}:{region}')
   else:regions.append(region)
   if not isinstance(d.get('description'),str) or not d['description'].strip():reasons.append(f'MISSING_CONCRETE_DESCRIPTION:{did}')
   if d.get('concrete') is not True:reasons.append(f'NOT_AFFIRMED_CONCRETE:{did}')
   if not isinstance(d.get('evidence_refs'),list) or not d['evidence_refs']:reasons.append(f'MISSING_DESCRIPTOR_EVIDENCE_REFS:{did}')
   if family is not None:
    if family not in FAMILIES:reasons.append(f'UNALLOWED_EXCEPTION_FAMILY:{did}:{family}')
    else:families.append(family)
   reasons.extend(support_reasons(d.get('support',{}),'DESCRIPTOR_SUPPORT:'+did))
  if len(set(regions))<3:reasons.append('FEWER_THAN_THREE_REGIONS')
  if not families:reasons.append('NO_ALLOWED_EXCEPTIONAL_DETAIL')
  reasons.extend(support_reasons(signature.get('joint_attachment_support',{}),'JOINT_ATTACHMENT_SUPPORT'))
  comparisons=entry.get('comparisons',[]);assert isinstance(comparisons,list)
  by={}
  for comp in comparisons:
   key=(comp['other_entry'],comp['witness'])
   assert key[0] in ENTRIES and key[0]!=eid and key[1] in WITNESSES and key not in by,f'{eid}: invalid or duplicate competitor'
   by[key]=comp
  for other in ENTRIES:
   if other==eid:continue
   for witness in WITNESSES:
    key=(other,witness);comp=by.get(key)
    if comp is None:
     reasons.append(f'MISSING_COMPETITOR_CHECK:{other}:{witness}');checks.append({'other_entry':other,'witness':witness,'status':'MISSING'});continue
    states=comp.get('descriptor_states',{});missing=sorted(set(ids)-set(states));extra=sorted(set(states)-set(ids))
    if missing:reasons.append(f'MISSING_COMPETITOR_DESCRIPTOR_STATES:{other}:{witness}:'+','.join(missing))
    if extra:reasons.append(f'EXTRA_COMPETITOR_DESCRIPTOR_STATES:{other}:{witness}:'+','.join(extra))
    vals=[states.get(did,'NOT_RECORDED') for did in ids]
    if any(x not in STATES for x in vals):reasons.append(f'INVALID_COMPETITOR_STATE:{other}:{witness}')
    if not isinstance(comp.get('evidence_refs'),list) or not comp['evidence_refs']:reasons.append(f'MISSING_COMPETITOR_EVIDENCE_REFS:{other}:{witness}')
    if vals and all(x=='YES' for x in vals):
     status='ENTIRE_SIGNATURE_MATCH';reasons.append(f'COMPETITOR_ENTIRE_SIGNATURE_MATCH:{other}:{witness}')
    elif 'NO' in vals:status='EXCLUDED_BY_OBSERVED_NO'
    else:
     status='UNRESOLVED';reasons.append(f'UNRESOLVED_COMPETITOR:{other}:{witness}')
    checks.append({'other_entry':other,'witness':witness,'status':status,'descriptor_states':states,'observed_no_descriptors':[did for did in ids if states.get(did)=='NO']})
 # Retain human rejections as substantive reasons, not silently discard them.
 reasons.extend('DISCOVERY_REJECTION:'+r for r in manual)
 return {'entry':eid,'label':entry['label'],'signature':signature,'descriptor_count':len(descriptors),'regions':sorted(set(regions)),'exceptional_families':sorted(set(families)),'competitor_checks':checks,'discovery_rejection_reasons':manual,'rejection_reasons':reasons,'qualifies':not reasons,'status':'SOURCE_SIGNATURE_CANDIDATE' if not reasons else 'NOT_QUALIFIED'}

def main():
 lock=json.loads((A/'REGISTRATION_LOCK.json').read_text())
 for name,h in lock['files'].items():assert sha(E/name)==h,name
 path=A/'RECONCILIATION.json';data=json.loads(path.read_text())
 assert data['reviewers']==REVIEWERS and data['witnesses']==WITNESSES
 assert len(data['entries'])==5 and {e['entry'] for e in data['entries']}==set(ENTRIES)
 assert set(data['observation_sources'])==set(REVIEWERS)
 obs=[]
 for reviewer in REVIEWERS:
  source=data['observation_sources'][reviewer];rel=Path(source['path']);assert not rel.is_absolute() and '..' not in rel.parts
  assert sha(R/rel)==source['sha256'],f'{reviewer}: observation source hash mismatch'
  obs.append({'reviewer':reviewer,'path':str(rel),'sha256':source['sha256']})
 entries=[account(e) for e in sorted(data['entries'],key=lambda e:e['entry'])]
 number=sum(e['qualifies'] for e in entries)
 result={'status':'SOURCE_SIGNATURE_CANDIDATES' if number>=2 else 'NO_MULTI_ENTRY_SIGNATURE_CAPACITY','entry_count':5,'qualifying_entries':number,'required_qualifying_entries':2,'entries':entries,'reconciliation_sha256':sha(path),'observation_sources':obs,'accounting_only':True,'visual_truth_validated':False,'voynich_access':False,'meanings':0,'direct_copying_claim':False,'independent_botanical_identification':False,'significance_claim':False}
 dump('RESULT.json',result)
 lines=['# GDT1158 complete five-entry accounting','','This checks the supplied reconciliation against the fixed rules, not the truth of native visual judgments. All rejection reasons remain visible.','','|Entry|Source label|Descriptors|Regions|Exceptional families|Qualified|Rejection reasons|','|---|---|---:|---|---|---|---|']
 for e in entries:
  cells=[e['entry'],e['label'],str(e['descriptor_count']),','.join(e['regions']) or 'NONE',','.join(e['exceptional_families']) or 'NONE',str(e['qualifies']),'; '.join(e['rejection_reasons']) or 'NONE']
  lines.append('|'+ '|'.join(x.replace('|','&#124;').replace('\n',' ') for x in cells)+'|')
 (E/'CANDIDATE_TABLE.md').write_text('\n'.join(lines)+'\n');print(json.dumps({'status':result['status'],'qualifying_entries':number,'entry_count':5}))
if __name__=='__main__':main()
