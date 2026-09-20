"""Independent witness reconstruction; not a native-vision validator."""
import hashlib,json
from pathlib import Path
from PIL import Image
E=Path(__file__).resolve().parents[1];R=E.parents[2]
def read(p):return json.loads(p.read_text())
def main():
 for n,h in read(E/'PREREG_LOCK.json')['files'].items():assert hashlib.sha256((R/n).read_bytes()).hexdigest()==h,n
 spec=read(E/'src/SPEC.json');img=R/spec['image_path'];assert hashlib.sha256(img.read_bytes()).hexdigest()==spec['image']['sha256'];assert list(Image.open(img).size)==spec['image']['dimensions']
 r=read(E/'artifacts/RESULT.json');obs=read(E/'artifacts/NATIVE_OBSERVATIONS.json');assert r['native_observations']==obs
 statuses={}
 for k in ('T18','T21'):
  o=obs['targets'][k];v=o['seam'];statuses[k]='UNRESOLVED'
  if o['localized'] and v!='UNCERTAIN':statuses[k]='COMPATIBLE' if (k=='T18' and v=='INTERNAL_LIKE') or (k=='T21' and v=='SPACE_LIKE') else 'WEAKENED_PHYSICAL_PREMISE'
 assert statuses==r['seams']
 expect='PARK_EXACT_PHYSICAL_TOKEN_REALIZATION' if any(v.startswith('WEAKENED') for v in statuses.values()) else 'RETAIN_LOCAL_SOURCE_COMPATIBILITY_NO_MEANING_SUPPORT' if list(statuses.values())==['COMPATIBLE','COMPATIBLE'] else 'RETAIN_WITH_UNRESOLVED_SOURCE_PREMISE';assert r['decision']==expect
 lex={x['raw']:x['symbol'] for x in read(R/spec['source_draft'])['lexicon']};g=read(R/spec['grammar']);source=read(R/spec['source_packet'])
 for ed,s in source['readers'].items():
  flat=sum((x['groups'] for x in s['rows']),[]);expected=[]
  # Construct a position-indexed allowed-value field independently of runner.
  constraints={i:('INITIAL',v) for i,v in enumerate(g['patterns']['INITIAL'])}
  constraints.update({len(flat)-6+i:('CONCLUSION',v) for i,v in enumerate(g['patterns']['CONCLUSION'])})
  for i,(kind,p) in sorted(constraints.items()):
   word=flat[i];val=lex.get(word['ivtff_group_raw']);allowed=g['types'][p[1:]] if p[0]=='@' else [p]
   if val is not None and val not in allowed:expected.append(dict(required_clause=kind,position=i+1,source_id=word['source_group_id'],raw=word['ivtff_group_raw'],known_value=val,required_values=allowed))
  out=r['source_necessary_conditions'][ed];assert out['witnesses']==expected;assert out['groups']==len(flat);assert out['whole_paragraph_contract']==s['whole_paragraph_contract'];assert out['unknown_groups']==sum(x['ivtff_group_raw'] not in lex for x in flat)
  assert out['necessary_fixed_endpoint_patterns']==('CONTRADICTED' if expected else 'NOT_EXCLUDED_BY_THIS_RELAXATION')
 assert r['confirmed_words']==r['independent_meaning_capacity']==0 and r['significance'] is False
 out=dict(status='PASS',native_targets=2,source_readers=3,visual_perception_verified=False,manual_localization_verified=False,meaning_confirmed=False)
 (E/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
