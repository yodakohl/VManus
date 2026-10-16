"""Record checks and fixed qualitative conjunction; does not analyze pixels."""
from pathlib import Path
import hashlib,json
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,data):(B/'artifacts'/name).write_text(json.dumps(data,indent=2)+'\n')
def main():
 lock=read(B/'src/VIEW_LOCK.json')
 for p,h in lock['files'].items():assert sha(R/p)==h,p
 seal=read(B/'artifacts/A_SEAL.json');assert sha(R/seal['path'])==seal['sha256']
 source_path=R/'research_registry/proposals/laufenberg_f85r2_20260926/source_supply_20260929/R_COMPLETE_UNITS.json'
 src=read(source_path);u=next(u for u in src['units'] if u['edition']=='IT2a');line=next(l for l in u['lines'] if l['metadata']['locus']=='f75v.47')
 groups=[g for g in line['groups'] if int(g[1]) in [5,6,10]];assert [g[2] for g in groups]==['ol','shedy','olshedy'];assert all(g[3]==g[4]=='DEFINITE_SPACE' for g in groups)
 image=read(B/'artifacts/INHERITED_SOURCES.json');views={key:read(B/f'artifacts/VIEWER_{key}.json') for key in ['A','B']}
 for v in views.values():
  assert v['image_sha256']==image['sha256'];assert v['T1'] in ['SPACE_LIKE','INTERNAL_LIKE','UNCLEAR'];assert v['T2'] in ['SPACE_LIKE','INTERNAL_LIKE','UNCLEAR'];assert v['contrast'] in ['LOCAL_CONTRAST','NO_CLEAR_CONTRAST','UNSCORABLE']
 qualified={k:v['location_confidence']=='SUFFICIENT' and v['T1']=='SPACE_LIKE' and v['T2']=='INTERNAL_LIKE' and v['contrast']=='LOCAL_CONTRAST' for k,v in views.items()}
 save('SOURCE.json',{'path':str(source_path.relative_to(R)),'sha256':sha(source_path),'metadata':line['metadata'],'group_columns':u['group_columns'],'groups':groups})
 result={'status':'LOCAL_SPACING_CONTRAST_SUPPORTED' if all(qualified.values()) else 'SPACING_CONTRAST_UNRESOLVED','qualified':qualified,'views':{k:{f:v[f] for f in ['location_confidence','T1','T2','contrast']} for k,v in views.items()},'viewer_hashes':{k:sha(B/f'artifacts/VIEWER_{k}.json') for k in views},'image_sha256':image['sha256'],'claim_ceiling':'Two AI judgments of one already-owned image at a second fixed location. No independent physical witness, meanings, equal lexical content, measured spacing or compression mechanism.'}
 save('RESULT.json',result);print(json.dumps(result))
if __name__=='__main__':main()
