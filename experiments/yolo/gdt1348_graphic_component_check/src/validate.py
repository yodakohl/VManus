from pathlib import Path
from datetime import datetime
import hashlib,json,gzip
from PIL import Image
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def read(name):return json.loads((B/'artifacts'/name).read_text())
def main():
    registration=read('REGISTRATION_LOCK.json');a=read('STAGE_A.json');alock=read('STAGE_A_LOCK.json');b=read('STAGE_B.json');olock=read('OBSERVATION_LOCK.json');result=read('RESULT.json')
    for lock in [registration,olock]:
        for path,h in lock['hashes'].items():assert hashlib.sha256((R/path).read_bytes()).hexdigest()==h,path
    assert alock['sha256']==hashlib.sha256((B/'artifacts/STAGE_A.json').read_bytes()).hexdigest()
    times=[registration['utc'],a['utc'],alock['utc'],b['utc'],olock['utc']];assert all(datetime.fromisoformat(x)<=datetime.fromisoformat(y) for x,y in zip(times,times[1:]))
    receipts=read('IMAGE_RECEIPTS.json');sizes={'T21_PIXELS.png':(620,100),'T18_PIXELS.png':(535,150),'PARAGRAPH_PIXELS.png':(1910,545)}
    for receipt in receipts['crops']:
        p=R/receipt['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==receipt['sha256']
        with Image.open(p) as im:
            assert im.size==sizes[p.name] and set(im.info)=={'icc_profile'}
            assert hashlib.sha256(im.info['icc_profile']).hexdigest()=='f6bd2776ef85c5a0a9313989eb60f3db7996bc4af48453353f53840643d8e32b'
    packet=read('SOURCE_PACKET.json');p=R/packet['input'];assert hashlib.sha256(p.read_bytes()).hexdigest()==packet['input_sha256']
    # Already guarded and admitted old cache; no mixed/raw TSV extraction.
    rows=json.loads(gzip.decompress(p.read_bytes()));wanted=[r for r in rows if r['locus'] in ['f83r.18','f83r.21','f83r.23']];assert wanted==packet['rows'] and all(r['page']=='f83r' for r in wanted)
    for c in b['fixed_cases']:
        found=[r for r in wanted if r['edition']=='ZL3b' and r['locus']==c['locus'] and int(r['index'])==c['ZL_group']];assert len(found)==1 and found[0]['raw']==c['transcription_locator']
        x1,y1,x2,y2=c['approximate_whole_group_box_in_paragraph'];assert 0<=x1<x2<=1910 and 0<=y1<y2<=545
        assert c['strict_crossed_decision']=='UNSCORABLE_INCOMPLETE_FREE_HEIGHT_TEMPLATES'
    assert a['free_k']['status']=='UPPER_TEMPLATE_CLIPPED_OR_INCOMPLETE' and a['free_t']['status']=='NOT_RELIABLY_INCLUDED'
    assert result['fixed_crossed_test']=='UNSCORABLE' and result['status']=='TEMPLATE_CAPACITY_STOP__INFORMED_GRAPHIC_COMPATIBILITY'
    assert result['fixed_target_cases']==3 and result['descriptive_low_motif_compatible']==3 and result['sound_or_word_values']==0
    out={'status':'PASS_ACCOUNTING_ONLY','registered_images':len(sizes),'complete_reader_lines':len({(r['edition'],r['locus']) for r in wanted}),'retained_source_groups':len(wanted),'fixed_targets':3,'recorded_chronology':'ordered registration,A,Afreeze,B,observationlock','metadata':'Only the bound public standard sRGB ICCprofile; no PNGtext/EXIFmetadata; exact source bytes retained','scientific_limit':'Does not verify perception, actual physical glyph identity, stroke topology, source-text localization or independence. No repaired crossed-test PASS.'}
    (B/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
