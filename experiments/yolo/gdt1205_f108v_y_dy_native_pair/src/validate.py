"""Validate scope/source identities and reduction, not visual judgments."""
from pathlib import Path
from datetime import datetime
from PIL import Image
import hashlib,json
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
def load(name):return json.loads((A/name).read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    lock=load('REGISTRATION_LOCK.json');obs=load('OBSERVATION.json');seal=load('OBSERVATION_SEAL.json');source=load('SOURCE_IMAGE.json');regions=load('REGION_IMAGES.json');result=load('RESULT.json')
    for p,h in lock['files'].items():assert sha(ROOT/p)==h,p
    for name,key in [('OBSERVATION.json','observation_sha256'),('SOURCE_IMAGE.json','source_receipt_sha256'),('REGION_IMAGES.json','region_receipt_sha256')]:assert sha(A/name)==seal[key]
    assert sha(D/'PREREGISTRATION.md')==seal['registration_sha256'] and sha(D/'src/run.py')==load('RUN_RECEIPT.json')['runner_sha256']
    registered=datetime.fromisoformat(lock['registered_utc']);observed=datetime.fromisoformat(obs['recorded_utc']);assert registered<observed<=datetime.fromisoformat(seal['sealed_utc'])
    assert lock['before_pixel_access'] and source['before_first_view'] and source['canvas']=='1006265' and source['label']=='108v'
    assert source['url']=='https://collections.library.yale.edu/iiif/2/1006265/full/full/0/default.jpg'
    assert registered<datetime.fromisoformat(source['fetched_utc'])<observed
    assert sha(ROOT/source['path'])==source['sha256']==obs['image_sha256'] and obs['source_image']==source['path']
    with Image.open(ROOT/source['path']) as im:assert im.size==(2649,3706)==tuple(source['dimensions'])
    canvas=load('CANVAS_METADATA.json')['canvas'];assert canvas['label']['none']==['108v'] and canvas['id'].endswith('/1006265') and canvas['width']==2649 and canvas['height']==3706
    assert len(regions)==2 and {r['target'] for r in regions}=={'f108v.35','f108v.52'}
    for reg in regions:
        x,y,w,h=reg['region'];assert x>=0 and y>=0 and w>0 and h>0 and x+w<=2649 and y+h<=3706 and reg['before_view']
        assert reg['url']=='https://collections.library.yale.edu/iiif/2/1006265/'+','.join(map(str,reg['region']))+'/full/0/default.jpg'
        assert sha(ROOT/reg['path'])==reg['sha256'] and registered<datetime.fromisoformat(reg['fetched_utc'])<observed
        with Image.open(ROOT/reg['path']) as im:assert im.size==(w,h)==tuple(reg['dimensions'])
    ts={t['locus']:t for t in obs['targets']};fs={f['side']:f for f in obs['flank_pairs']};assert len(obs['targets'])==len(ts)==2 and set(ts)=={'f108v.35','f108v.52'};assert len(obs['flank_pairs'])==len(fs)==2 and set(fs)=={'left','right'}
    for t in ts.values():
        assert type(t['located']) is bool and t['center_extra_body'] in {'PRESENT','ABSENT','UNRESOLVED','UNLOCATED'} and t['boundaries'] in {'BOTH_SPACE_LIKE','CONTRADICTED','UNRESOLVED','UNLOCATED'}
        assert all(t[k] for k in ('location','observation','limitations','rivals'))
    for f in fs.values():assert f['classification'] in {'SAME_SEQUENCE_COMPATIBLE','DIFFERENT_SEQUENCE','UNRESOLVED','UNLOCATED'} and f['observation'] and f['limitations']
    answer='UNRESOLVED_NATIVE_PAIR'
    if ts['f108v.35']['located'] and ts['f108v.52']['located']:
        bad=ts['f108v.35']['center_extra_body']=='PRESENT' or ts['f108v.52']['center_extra_body']=='ABSENT' or 'DIFFERENT_SEQUENCE' in {f['classification'] for f in fs.values()} or 'CONTRADICTED' in {t['boundaries'] for t in ts.values()}
        if bad:answer='VISUAL_COUNTEREVIDENCE'
        elif ts['f108v.35']['center_extra_body']=='ABSENT' and ts['f108v.52']['center_extra_body']=='PRESENT' and {f['classification'] for f in fs.values()}=={'SAME_SEQUENCE_COMPATIBLE'} and {t['boundaries'] for t in ts.values()}=={'BOTH_SPACE_LIKE'}:answer='SOURCE_AWARE_VISUAL_SUPPORT'
    assert result['status']==answer and result['observer_count']==1 and result['independent_confirmation_capacity']==0 and result['native_meanings_assigned']==0 and not result['word_identity_proven'] and not result['earlier_literal_result_replaced']
    assert obs['observer_count']==1 and not obs['blind'] and obs['views_used']=={'whole_original':1,'registered_native_regions':2}
    for t in result['targets']:assert t=={k:ts[t['locus']][k] for k in ('locus','located','center_extra_body','boundaries')}
    for f in result['flank_pairs']:assert f=={k:fs[f['side']][k] for k in ('side','classification')}
    out={'status':'PASS','scope':'Registered admission/source receipt chronology, exact image hashes/dimensions, region bounds, sealed observation schema and fixed decision reduction only','palaeography_validated':False,'same_author':True,'scientific_status':answer,'new_image_keys':1,'source_region_views':2,'validator_sha256':sha(Path(__file__))}
    (A/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
