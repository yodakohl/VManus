import argparse,hashlib,json
from pathlib import Path
from PIL import Image
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
def schema(o):
 assert isinstance(o['localized'],bool) and o['endpoint_topology'] in {'ONE_UPRIGHT_FLOURISH','TWO_UPRIGHT_LINK','UNCERTAIN'} and type(o['uncertainty']) is bool
 n=o['complete_intervening_groups'];assert n is None or type(n)==int and n>=0;assert (o['localized'] and not o['uncertainty'] and o['endpoint_topology']!='UNCERTAIN') or n is None
 for name in ['group_boundary_evidence','endpoint_description','note']:assert isinstance(o[name],str)
def decision(a,b):
 for o in [a,b]:
  if o['localized'] is not True or o['uncertainty'] is not False or o['endpoint_topology']=='UNCERTAIN' or type(o['complete_intervening_groups'])!=int:return 'UNRESOLVED_OR_DISAGREEMENT'
 if a['endpoint_topology']==b['endpoint_topology']=='TWO_UPRIGHT_LINK' and min(a['complete_intervening_groups'],b['complete_intervening_groups'])>0:return 'BOTH_VIEWERS_INTERVENING_GROUP_LINK'
 if a['complete_intervening_groups']==0 and b['complete_intervening_groups']==0 and a['endpoint_topology']==b['endpoint_topology']:return 'BOTH_VIEWERS_NO_COMPLETE_INTERVENING_GROUP'
 return 'UNRESOLVED_OR_DISAGREEMENT'
def main():
 p=argparse.ArgumentParser();p.add_argument('--controls',action='store_true');args=p.parse_args();a=dict(localized=True,endpoint_topology='TWO_UPRIGHT_LINK',complete_intervening_groups=1,group_boundary_evidence='',endpoint_description='',uncertainty=False,note='');schema(a);z=dict(a,complete_intervening_groups=0);f=dict(z,endpoint_topology='ONE_UPRIGHT_FLOURISH');assert decision(a,a)=='BOTH_VIEWERS_INTERVENING_GROUP_LINK' and decision(z,z)==decision(f,f)=='BOTH_VIEWERS_NO_COMPLETE_INTERVENING_GROUP';assert all(decision(a,x)=='UNRESOLVED_OR_DISAGREEMENT' for x in [z,dict(a,uncertainty=True),dict(a,localized=False,complete_intervening_groups=None),dict(a,endpoint_topology='UNCERTAIN')]);assert decision(z,f)=='UNRESOLVED_OR_DISAGREEMENT'
 if args.controls:print('INDEPENDENT CONTROLS PASS');return
 read=lambda n:json.loads((E/'artifacts'/n).read_text());s=json.loads((E/'src/SPEC.json').read_text());provenance=json.loads((E/'SOURCES.json').read_text());assert provenance['source']==s['image'] and provenance['cache_path']==s['image_path'] and provenance['page_selector']==s['target']['selector'];im=provenance['source'];p=ROOT/provenance['cache_path'];assert p.is_file() and p.stat().st_size==im['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==im['sha256']
 with Image.open(p) as image:assert image.size==(im['width'],im['height'])
 assert im in json.loads((ROOT/s['source_provenance']).read_text())['source_images'];a=read('VIEWER_A.json');b=read('VIEWER_B.json');schema(a);schema(b);seal=read('A_SEAL.json');assert hashlib.sha256((E/'artifacts/VIEWER_A.json').read_bytes()).hexdigest()==seal['sha256'];assert isinstance(seal['sealed_at_utc'],str) and seal['sealed_at_utc'];assert read('RESULT.json')==dict(status=decision(a,b),A=a,B=b,A_seal=seal,vision_verified_by_software=False)
 v=dict(status='PASS',image_hash_bytes_dimensions_checked=True,A_seal_schema_checked=True,independent_decision=True,vision_verified_by_software=False,controls='PASS');(E/'artifacts/VALIDATION.json').write_text(json.dumps(v,sort_keys=True,separators=(',',':'))+'\n');print(json.dumps(v))
if __name__=='__main__':main()
