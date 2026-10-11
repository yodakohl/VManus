from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent
path=P/'THEOPHILUS_SHARED_LESSON_EXPANSION_20261011.json';w=json.loads(path.read_text());src=R/w['source']['path'];assert hashlib.sha256(src.read_bytes()).hexdigest()==w['source']['sha256'];s=json.loads(src.read_text());chapters={c['chapter']:c for c in s['chapters']};assert set(chapters)=={f'I.{i}' for i in range(1,10)}
for a in w['explicit_applications']:
 c=chapters[a['chapter']];assert a['source_literal']==c['latin_complete_normalized'];assert a['materials_written']==c['materials_written'];assert a['ALL_application_loci_written']==c['application_loci_written'];assert 'cum simplici membrina' in a['source_literal']
for chapter,claims in w['retained_full_context'].items():assert claims==chapters[chapter]['ordered_claim_inventory']
assert set(w['retained_full_context'])|{a['chapter'] for a in w['explicit_applications']}|{w['stored_lesson']['definition_chapter']}==set(chapters)
assert 'arbitrio' in chapters['I.1']['latin_complete_normalized'];assert 'qui dicitur rosa' in chapters['I.4']['latin_complete_normalized'];assert 'qui dicitur lumina' in chapters['I.5']['latin_complete_normalized']
out={'status':'PASS_OWNED_SOURCE_LITERAL_AND_INVENTORY_CHECK','source_sha256':w['source']['sha256'],'witness_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'complete_application_texts':2,'chapters_retained':9,'native_word_values':0,'limit':'Literal text and complete application-locus/material inventory match the already owned edition projection. Manual I.1 wording and knowledge-versus-action interpretation are not machine-proved. No new source acquisition, compression or historical oral-learning claim.'};(P/'THEOPHILUS_SHARED_LESSON_VALIDATION_20261011.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
