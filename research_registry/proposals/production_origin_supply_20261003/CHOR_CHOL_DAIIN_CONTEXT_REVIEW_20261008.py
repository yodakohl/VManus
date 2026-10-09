"""Native context and old lexical-contract coverage only; no word-value adoption."""
import csv,json,hashlib
from pathlib import Path
B=Path('research_registry/proposals/production_origin_supply_20261003')
SOURCE=B/'CHOR_CHOL_DAIIN_PAGES_20261008.tsv'
OLD=Path('research_registry/proposals/raw_shared_ingredient_goal_contract.json')
rows=list(csv.DictReader(SOURCE.open(),delimiter='\t'))
assert len(rows)==553
lex=set(json.loads(OLD.read_text())['design']['exact_whole_word_lexicon'])
out=[]
for edition in ['ZL3b','IT2a','RF1b']:
    for page,start,end,target in [('f21r',8,12,12),('f32v',7,11,10)]:
        block=sorted([r for r in rows if r['edition']==edition and r['locus'].split('.')[0]==page and start<=int(r['locus'].split('.')[1])<=end],key=lambda r:(int(r['locus'].split('.')[1]),int(r['source_group_index'])))
        line=[r for r in block if r['locus']==f'{page}.{target}'];words=[r['ivtff_group_raw'] for r in line]
        matches=[i for i in range(len(words)-2) if words[i:i+3]==['chor','chol','daiin']]
        assert len(matches)==1;i=matches[0]
        assert all(line[j]['right_separator']==line[j+1]['left_separator']=='DEFINITE_SPACE' for j in [i,i+1])
        out.append({'reader':edition,'page':page,'span':f'{page}.{start}–{end}','groups':len(block),'own_paragraph_start':block[0]['paragraph_start'],'own_paragraph_end':block[-1]['paragraph_end'],'complete_rows':block,'target_locus':f'{page}.{target}','target_line':line,'motif_start_index0':i,'following_groups':words[i+3:],'old14word_lexicon_missing_exact_forms':sorted(set(words)-lex)})
    f21=out[-2]['target_line'];f32=out[-1]['target_line']
    assert sum(r['ivtff_group_raw']=='chor' for r in f21)==2
    ws=[r['ivtff_group_raw'] for r in out[-1]['complete_rows'] if r['locus']=='f32v.8']
    assert any(ws[j:j+2]==['daiin','daiin'] for j in range(len(ws)-1))
    if edition=='ZL3b':
        i=next(i for i,r in enumerate(f32) if r['ivtff_group_raw']=='cpho')
        assert f32[i+1]['ivtff_group_raw']=='l'
        assert f32[i]['right_separator']==f32[i+1]['left_separator']=='UNCERTAIN_SMALL_SPACE'
    else:assert any(r['ivtff_group_raw']=='cphol' for r in f32)
inputs=[SOURCE,OLD,Path(__file__)]
result={'status':'FULL_CONTEXT_REVIEW_NO_SEMANTIC_SELECTION','cases':out,'bound_inputs':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},'decisions':['Two exact three-group motifs retained in allreaders; both embedded with further material on their physical line.','RF same-line spans are not independent paragraph evidence: own paragraph flags0.','Precedingchor and repeateddaiin must remain in any full reading.','Old shared14exact-form lexicon has unbound ykeea/cphol and RFannotations; this is literal coverage, not validation of any gloss or rejection of general segmentation.','ZL cpho~l boundary is uncertain; IT/RF cphol is one raw group. No silently shared standalone l.','No actual clause boundary, amount, degree, operation, referent identity or translated word follows.'], 'limits':'Old observations and manuscript data; no novelty, score, meaning or independent confirmation. No GDT rerun. No raw entities normalized, images or reserves.'}
(B/'CHOR_CHOL_DAIIN_CONTEXT_RESULT_20261008.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps([{'reader':x['reader'],'span':x['span'],'groups':x['groups'],'missing_old_keys':x['old14word_lexicon_missing_exact_forms']} for x in out],ensure_ascii=False))
