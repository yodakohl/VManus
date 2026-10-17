#!/usr/bin/env python3
"""Source/header/record accounting only; never validates visual perception."""
import datetime,hashlib,json
from pathlib import Path
from PIL import Image
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2];A=E/'artifacts'
BASE='https://collections.library.yale.edu/iiif/2/1006101/'
CATEGORIES={'INTERNAL_LIKE','SPACE_LIKE','UNRESOLVED'}
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def stamp(value):
    t=datetime.datetime.fromisoformat(value.replace('Z','+00:00'))
    assert t.tzinfo is not None,'Timestamp must include timezone'
    return t
def pinned(lock):
    files=lock['pins']
    assert isinstance(files,dict)
    for name,digest in files.items():
        path=Path(name);assert not path.is_absolute() and '..' not in path.parts
        assert sha(ROOT/path)==digest,name
    return files
def source(receipt,url,width,height):
    assert receipt['url']==url
    assert receipt['width']==width and receipt['height']==height
    relative=Path(receipt['path'])
    assert not relative.is_absolute() and '..' not in relative.parts
    path=ROOT/relative
    assert path.parent.resolve()==A.resolve()
    assert path.is_file() and path.stat().st_size==receipt['bytes']
    assert sha(path)==receipt['sha256']
    # Header metadata only: no load(), pixel arrays, crop or display.
    with Image.open(path) as im:
        assert im.format=='JPEG' and im.size==(width,height)
    return {'url':url,'sha256':receipt['sha256'],'bytes':receipt['bytes'],
            'width':width,'height':height}
def main():
    lock=read(E/'src/PROTOCOL_LOCK.json');pins=pinned(lock);spec=read(E/'src/SPEC.json')
    assert spec['canvas_id']=='1006101' and spec['label']=='14v'
    assert spec['overview_dimensions']==[2812,3772]
    assert spec['overview_url']==BASE+'full/full/0/default.jpg'
    assert spec['detail_url_template']==BASE+'{region}/full/0/default.jpg'
    assert set(spec['categories'])==CATEGORIES and spec['confirmed_words']==0
    ids=[s['id'] for s in spec['seams']]
    assert ids==['r6_left_external','r6_inner_1','r6_inner_2','r6_right_external','r7_left_external','r7_inner','r7_right_external']
    overview=read(A/'OVERVIEW_SOURCE.json');overview_checked=source(overview,spec['overview_url'],2812,3772)
    assert stamp(lock['locked_at'])<=stamp(overview['fetched_at'])
    obs=read(A/'OBSERVATION.json');result=read(A/'RESULT.json')
    assert obs['observer']=='root informed AI' and isinstance(obs['localization'],str) and obs['localization'].strip()
    assert isinstance(obs['limits'],list) and obs['limits']
    assert stamp(overview['fetched_at'])<=stamp(obs['observed_at'])
    detail=None;detail_checked=None;crop=None
    if obs['status']=='OBSERVED':
        assert obs['oneoverview_onecrop'] is True
        crop=read(A/'CROP_SCOPE.json');region=crop['region']
        assert len(region)==4 and all(type(n) is int for n in region)
        x,y,w,h=region;assert x>=0 and y>=0 and w>0 and h>0 and x+w<=2812 and y+h<=3772
        assert crop['overview_sha256']==overview['sha256'] and crop['localization'].strip()
        detail=read(A/'DETAIL_SOURCE.json');url=BASE+','.join(map(str,region))+'/full/0/default.jpg'
        detail_checked=source(detail,url,w,h)
        assert stamp(overview['fetched_at'])<=stamp(crop['locked_at'])<stamp(detail['fetched_at'])<=stamp(obs['observed_at'])
        reported=[o['id'] for o in obs['observations']]
        assert len(reported)==7 and set(reported)==set(ids)
        for o in obs['observations']:
            assert o['category'] in CATEGORIES and isinstance(o['reason'],str) and o['reason'].strip()
        expected_images={Path(overview['path']).name,Path(detail['path']).name}
    else:
        assert obs['status']=='TARGET_LOCALIZATION_STOP' and obs['observations']==[]
        assert obs.get('oneoverview_onecrop') is not True
        assert not (A/'DETAIL_SOURCE.json').exists() and not (A/'native_detail.jpg').exists()
        expected_images={Path(overview['path']).name}
    images={p.name for p in A.iterdir() if p.suffix.lower() in {'.jpg','.jpeg','.png','.tif','.tiff','.webp'}}
    assert images==expected_images
    assert result['status']==obs['status'] and result['observation']==obs
    assert result['source_receipts']=={'overview':overview,'detail':detail}
    assert result['confirmed_words']==0 and isinstance(result['claim_ceiling'],str) and result['claim_ceiling'].strip()
    rpins=result['pins'];assert isinstance(rpins,dict)
    expected_hashes={sha(E/'src/SPEC.json'),sha(A/'OBSERVATION.json')}
    assert expected_hashes<=set(rpins.values())
    allowed_hashes=set(pins.values())|expected_hashes|{sha(E/'src/PROTOCOL_LOCK.json'),sha(A/'OVERVIEW_SOURCE.json'),overview['sha256']}
    if detail:allowed_hashes|={sha(A/'DETAIL_SOURCE.json'),sha(A/'CROP_SCOPE.json'),detail['sha256']}
    assert set(rpins.values())<=allowed_hashes,'Unverified named result pin'
    for key,value in rpins.items():
        assert isinstance(value,str) and len(value)==64 and all(c in '0123456789abcdef' for c in value)
        # Explicit path keys, if present, must match; named receipt keys are bound below.
        for candidate in (ROOT/key,E/key,A/key):
            if candidate.is_file():assert sha(candidate)==value
    receipt={'experiment_id':'GDT1432','status':'PASS_NOT_PERCEPTION',
       'observation_status':'OBSERVED' if detail else 'NOT_OBSERVED',
       'protocol_lock_sha256':sha(E/'src/PROTOCOL_LOCK.json'),'protocol_pins':pins,
       'validator_sha256':sha(Path(__file__)),'spec_sha256':sha(E/'src/SPEC.json'),
       'observation_sha256':sha(A/'OBSERVATION.json'),'result_sha256':sha(A/'RESULT.json'),
       'source_receipt_sha256':{'overview':sha(A/'OVERVIEW_SOURCE.json'),'detail':sha(A/'DETAIL_SOURCE.json') if detail else None},
       'crop_scope_sha256':sha(A/'CROP_SCOPE.json') if crop else None,
       'image_metadata':{'overview':overview_checked,'detail':detail_checked},
       'observations_checked':len(obs['observations']),
       'limits':['Validates exact saved image bytes/header metadata and recorded chronology, not externally attested view behavior.',
                 'No pixels viewed or decoded by this validator. Row localization, crop semantic coverage and seven visual judgments are not independently validated.',
                 'No physical word boundary, alphabet, numeric value, source meaning or independent manuscript replication follows.']}
    out=A/'VALIDATION.json'
    if out.exists():assert read(out)==receipt
    else:out.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':receipt['status'],'observation_status':receipt['observation_status'],'observations_checked':receipt['observations_checked']}))
if __name__=='__main__':main()
