from pathlib import Path
from datetime import datetime
from PIL import Image
import hashlib,json
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def read(p):return json.loads(p.read_text())
def main():
    registration=read(B/'artifacts/REGISTRATION_LOCK.json');receipt=read(B/'artifacts/SOURCE_RECEIPT.json');obs=read(B/'artifacts/OBSERVATION.json');lock=read(B/'artifacts/OBSERVATION_LOCK.json');result=read(B/'artifacts/RESULT.json')
    for p,h in registration['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
    assert hashlib.sha256((R/lock['path']).read_bytes()).hexdigest()==lock['sha256']
    reference=read(R/'experiments/yolo/gdt1169_f57_annular_continuation_layout/artifacts/SOURCE.json');raw=(B/'source/F57V_ORIGINAL.jpg').read_bytes();assert hashlib.sha256(raw).hexdigest()==reference['sha256']==receipt['sha256'];assert len(raw)==reference['bytes']==receipt['bytes'];assert receipt['url']==reference['url']
    im=Image.open(B/'source/F57V_ORIGINAL.jpg');assert list(im.size)==receipt['dimensions']==[3028,3769];assert not im.getexif();assert list(im.info)==receipt['metadata']['info_keys'];assert hashlib.sha256(im.info['icc_profile']).hexdigest()==receipt['metadata']['icc_sha256']=='f6bd2776ef85c5a0a9313989eb60f3db7996bc4af48453353f53840643d8e32b'
    assert datetime.fromisoformat(registration['utc'])<datetime.fromisoformat(receipt['acquired_utc'])<datetime.fromisoformat(obs['observed_at_utc'])<=datetime.fromisoformat(lock['utc'])
    assert set(obs['coverage_notes'])=={'upper_arc','right_arc','lower_arc','left_arc'};assert obs['view_count']==1 and obs['whole_band_coverage'];assert obs['exact_item_count'] is None and obs['exact_type_inventory'] is None and obs['linguistic_atomicity']=='UNRESOLVED';assert not obs['new_transcription'] and not obs['native_cache_changed'];assert obs['new_sound_assignments']==obs['new_word_meanings']==0
    assert result['status']==obs['status']=='SPACED_GRAPHIC_FORMS__AUTHORIAL_UNIT_BOUNDARIES_UNRESOLVED';assert result['exact_item_count'] is None and result['exact_type_inventory'] is None and result['claimed_new_phonemes']==result['claimed_new_meanings']==0
    for k,v in [('localized','localization'),('boundary_device','boundary_device'),('repeat_limits','repeat_limits'),('graphic_forms','multi_part_shapes'),('coverage_notes','coverage_notes')]:assert result['observations'][k]==obs[v]
    assert 'f84/f84r' in (R/'docs/57v-signs.md').read_text();assert (R/'docs/VOYNICH_DATA_SCOPE.md').read_text().count('[Prospective scope](57v-signs.md)')==1
    out={'status':'PASS_ACCOUNTING_ONLY','historical_image_bytes_identical':True,'image_dimensions':[3028,3769],'metadata':'No EXIF; standard public sRGB profile matches prior inspected profile hash.','observed_views':1,'coverage_notes':4,'source_and_observation_chronology':'RECORDED_ORDER_PASS_NOT_INDEPENDENT_ATTESTATION','perception_independently_validated':False,'scope':'Source/hash/record consistency only, not physical alphabet or visual truth.'};(B/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
