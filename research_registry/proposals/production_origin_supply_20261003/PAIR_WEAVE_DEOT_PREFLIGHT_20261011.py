"""Apply the new necessary pair-weave condition to five OLD source certificates.
No source census, encoder, key search or Voynich query is run.
"""
from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parent;R=P.parents[2]
SOURCE='experiments/yolo/gdt1228_bare_hebrew_bijection_screen/artifacts/SOURCE_PROJECTION.json'
CAP='experiments/yolo/gdt1303_paired_coordinate_exchange/artifacts/LADDER_CAPACITY.json'
REPORT='experiments/yolo/gdt1303_paired_coordinate_exchange/REPORT.md'
LOCK='experiments/yolo/gdt1303_paired_coordinate_exchange/src/REGISTRATION_LOCK.json'
# Exactly the exhaustive five length6/6/6 cases printed in the old report.
OLD=[('3:1',4,['והקנאה','והתאוה','והכבוד']),('3:1',5,['והתאוה','והכבוד','וכיוצא']),('4:6',7,['ותאנימ','ותותימ','ואגסימ']),('4:9',89,['גדולימ','ותישימ','גדולימ']),('4:13',39,['מלוחימ','שלוקימ','מתבלינ'])]
def main():
    oldlock=json.loads((R/LOCK).read_text());assert hashlib.sha256((R/SOURCE).read_bytes()).hexdigest()==oldlock[SOURCE]
    source=json.loads((R/SOURCE).read_text());cap=json.loads((R/CAP).read_text());report=(R/REPORT).read_text()
    assert cap['length_six_triples']==len(OLD)==5 and cap['within_section_word_triples']==6146
    assert len({(ref,index) for ref,index,_ in OLD})==len(OLD)
    sections={s['ref']:s['words'] for s in source['source_sections']};rows=[]
    for ref,index,words in OLD:
        assert words==sections[ref][index:index+3]
        assert all(len(w)==6 for w in words)
        assert f'|{ref};{index}|'+' / '.join(words)+'|' in report
        flags=[w[:3]==w[3:] for w in words]
        eligible=[pair for pair in [[0,1],[1,2]] if all(flags[i] for i in pair)]
        rows.append({'section':ref,'start_zero_based':index,'words':words,'halves':[[w[:3],w[3:]] for w in words],'square_words':flags,'possible_aligned_square_pairs':eligible})
    out={'status':'FIXED_DEOT_PROJECTION_CANNOT_SUPPLY_PAIR_WEAVE_EVEN_TRIPLE','phase':'post-exposure logical preflight over old exhaustive certificates; not a new source census or preregistered source experiment','decision_note':{'question':'Does the unchanged old22-token source already satisfy the necessary native even-triple obligation?','selection':'Chosen for bounded preflight because it is already an exact22-token source with a complete length6triple certificate. It is not selected as the manuscript source. The oldfive cases were already exposed before this consequence was checked.','outcomes':'A missing requiredpair prevents a Deot-specific fullwriter/keyrun. Capacity alone would not support the mechanism or justify its source identity. Neither outcome licenses generalized language claims.','budget':'Only certificate reconciliation and publication; no decoder, source resampling or new control suite.'},'old_complete_scope':{'source_words':6288,'source_sections':71,'within_section_word_triples':cap['within_section_word_triples'],'length6_triples':cap['length_six_triples'],'completeness':'Inherited source-bound GDT1303certificate plus these5distinct confirmed members; not a new full-source enumeration.'},'cases':rows,'native_obligation':'The already reviewed qokedy×3 under1014forces one alignedpair of length6source squares under eitherlocalphase. Word lengths and boundaries preserved. No newnativequery; sourcekeyrenaming cannot alter equality.','possible_source_cases':sum(bool(x['possible_aligned_square_pairs']) for x in rows),'different_from1303':'1303tested source end-overlap underfixed LETTER-pairtables. This checks adjacent squares underwhole WORD-pairinterleaving. Its oldfailure is not itself the newproof.','decision':'Do not implement or score a full1014writer on this unchanged Deot stream. IDEA1014remains unresolved for other independentlyjustified sources, with no empirical nativefit or priority established. No source/boundary/paragraph switch after the result.','limits':['No general Hebrew, natural-language or pairweave exclusion.','No prediction of how often any other source shouldcontain squares.','No word or sound value; exactinverse remains automatically true and is not evidence of nativeuse.','Same fixed projected source and sectionboundaries; oldprojectionlosses remain.','No newGDTexperiment, nativeimage, reserve or mixedTSVread.'], 'hashes':{f:hashlib.sha256((R/f).read_bytes()).hexdigest() for f in [SOURCE,CAP,REPORT,LOCK,'research_registry/proposals/production_origin_supply_20261003/PAIRED_WORD_INTERLEAVING_LENGTH_CHANNEL_RAW_20261011.json','research_registry/proposals/production_origin_supply_20261003/PAIR_WEAVE_HAND_ASSESSMENT_20261011.json']}}
    assert out['possible_source_cases']==0
    (P/'PAIR_WEAVE_DEOT_PREFLIGHT_20261011.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':out['status'],'old_cases_checked':len(rows),'possible_source_cases':out['possible_source_cases'],'new_source_census':False}))
if __name__=='__main__':main()
