#!/usr/bin/env python3
"""Independent paragraph-stream audit. Never imports the experiment runner."""
import csv,gzip,hashlib,json,re,sys
from collections import Counter
from pathlib import Path
sys.dont_write_bytecode=True
BASE=Path(__file__).resolve().parents[1];REPO=BASE.parents[2]
def read(p):return json.loads(gzip.decompress(p.read_bytes())) if p.suffix=='.gz' else json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def reconstruct(source):
    lines={};ol={};all_native=0
    for pin in source['inputs']:
        m=re.search(r'SOURCE_(DISCOVERY|EVALUATION)_(ZL3b|IT2a|RF1b)\.json$',pin['path'])
        if not m:continue
        packet=read(REPO/pin['path']);ed=m.group(2)
        for row in packet['lines']:
            meta=row['metadata']
            if meta['kind']!='P':continue
            key=(ed,meta['locus']);assert key not in lines
            groups=[dict(zip(packet['group_columns'],g)) for g in row['groups']]
            assert len(groups)==int(meta['source_group_count'])
            assert [int(g['source_group_index']) for g in groups]==list(range(1,len(groups)+1))
            lines[key]={'row':row,'groups':groups};all_native+=len(groups)
            for g in groups:
                if g['ivtff_group_raw']=='ol':ol[g['source_group_id']]={'metadata':meta,'native':g,'paragraph':None}
    blocks=read(REPO/next(p['path'] for p in source['inputs'] if p['path'].endswith('/BLOCKS.json')))
    cases={}
    for b in blocks:
        selected=[lines[(b['edition'],locus)] for locus in b['loci']]
        assert [int(x['row']['metadata']['source_row_index']) for x in selected]==sorted(int(x['row']['metadata']['source_row_index']) for x in selected)
        stream=[g for line in selected for g in line['groups']];positions=[i for i,g in enumerate(stream) if g['ivtff_group_raw']=='ol']
        for i in positions:ol[stream[i]['source_group_id']]['paragraph']=b['id']
        if not positions:continue
        annotated=[g['source_group_id'] for g in stream if not re.fullmatch('[a-z]+',g['ivtff_group_raw'])]
        roles=[{'id':stream[i]['source_group_id'],'ordinal':j+1,'role':'OPEN' if j%2==0 else 'CLOSE','position':i} for j,i in enumerate(positions)]
        closed=[{'open':stream[positions[j]]['source_group_id'],'close':stream[positions[j+1]]['source_group_id'],
                 'inside':[g['source_group_id'] for g in stream[positions[j]+1:positions[j+1]]]} for j in range(0,len(positions)-1,2)]
        adjacent=[{'first':stream[positions[j]]['source_group_id'],'second':stream[positions[j+1]]['source_group_id'],
                   'first_ordinal':j+1,'compatible':j%2==1} for j in range(len(positions)-1) if positions[j+1]==positions[j]+1]
        cases[b['id']]={'block':b,'source_lines':[x['row'] for x in selected],'stream':stream,'positions':positions,'annotations':annotated,
          'events':roles,'fields':closed,'unmatched':stream[positions[-1]]['source_group_id'] if len(positions)%2 else None,
          'empty_fields':[f for f in closed if not f['inside']],'adjacent':adjacent,
          'status':'UNTESTABLE_ANNOTATION' if annotated else 'CONTRADICTION' if len(positions)%2 or any(not f['inside'] for f in closed) else 'COMPATIBLE'}
    return ol,cases,all_native

def case_record(c):
    b=c['block']
    return {**b,'leaf':int(re.match('f([0-9]+)',b['page']).group(1)),'ol_count':len(c['positions']),'group_count':len(c['stream']),
      'scorable':not bool(c['annotations']),'decision':c['status'],
      'ol_events':[{'id':e['id'],'paragraph_group_index':e['position']+1,'ol_ordinal':e['ordinal'],'role':e['role']} for e in c['events']],
      'fields':[{'open_id':f['open'],'close_id':f['close'],'content_ids':f['inside'],'empty':not bool(f['inside'])} for f in c['fields']],
      'adjacent_pairs':[{'left_id':p['first'],'right_id':p['second'],'first_ol_ordinal':p['first_ordinal'],'direction':'CLOSE_OPEN' if p['compatible'] else 'OPEN_CLOSE','violating':not p['compatible']} for p in c['adjacent']],
      'unmatched_open':c['unmatched'],'empty_fields':len(c['empty_fields']),'raw_lines':c['source_lines']}

def main():
    checks=[];mismatches=[]
    def check(name,ok):checks.append({'name':name,'pass':bool(ok)})
    def equal(a,b,path=''):
        if isinstance(a,dict) and isinstance(b,dict):
            ok=set(a)==set(b)
            if ok:ok=all(equal(a[k],b[k],path+'/'+str(k)) for k in a)
        elif isinstance(a,list) and isinstance(b,list):
            ok=len(a)==len(b)
            if ok:ok=all(equal(x,y,path+'/'+str(i)) for i,(x,y) in enumerate(zip(a,b)))
        else:ok=type(a)==type(b) and a==b
        if not ok and len(mismatches)<20:mismatches.append(path)
        return ok
    source=read(BASE/'src/SOURCE.json');lock=read(BASE/'src/PREREG_LOCK.json')
    paths=[BASE/f for f in ['METHOD.md','PREREGISTRATION.md','src/SOURCE.json','src/PREREG_LOCK.json','src/run.py',
          'artifacts/PARAGRAPHS.json.gz','artifacts/OCCURRENCES.json','artifacts/RESULT.json','artifacts/PARAGRAPH_DECISIONS.tsv','artifacts/ADJACENT_PAIRS.tsv']]
    paths += [REPO/p['path'] for p in source['inputs']];pins={str(p.relative_to(REPO)):sha(p) for p in paths}
    check('registration_method_prereg_source_byte_lock',all(sha(BASE/p)==h for p,h in lock['hashes'].items()))
    check('all_nine_source_predecessor_pins',all(sha(REPO/p['path'])==p['sha256'] for p in source['inputs']))
    allowed=set(read(REPO/source['inputs'][0]['path'])['allowed_selectors'])
    snapshots=[p for p in source['inputs'] if re.search(r'SOURCE_(DISCOVERY|EVALUATION)_(ZL3b|IT2a|RF1b)\.json$',p['path'])]
    check('exact_six_snapshots_allowlisted_sealed_scope',len(snapshots)==6 and not {'f84','f84r','f116v'}&allowed and all(row['metadata']['page'] in allowed and not row['metadata']['page'].startswith('f84') for pin in snapshots for row in read(REPO/pin['path'])['lines']))
    ol,cases,all_native=reconstruct(source);expected={sid:case_record(c) for sid,c in cases.items()}
    occurrences=read(BASE/'artifacts/OCCURRENCES.json');paragraphs=read(BASE/'artifacts/PARAGRAPHS.json.gz');result=read(BASE/'artifacts/RESULT.json')
    expected_occurrences={sid:{**e['native'],'edition':e['metadata']['edition'],'page':e['metadata']['page'],'locus':e['metadata']['locus'],'paragraph':e['paragraph']} for sid,e in ol.items()}
    blockpin=next(p['path'] for p in source['inputs'] if p['path'].endswith('/BLOCKS.json'));blocks=read(REPO/blockpin)
    summaries={};violations={}
    for ed in ['ZL3b','IT2a','RF1b']:
        ep={sid:c for sid,c in expected.items() if c['edition']==ed};ap={c['id']:c for c in paragraphs if c['edition']==ed}
        check(ed+'_every_bearing_paragraph_full_native_stream_fields_events_barrier',len(ap)==sum(c['edition']==ed for c in paragraphs) and equal(ep,ap,ed+'/paragraphs'))
        eo={sid:e for sid,e in expected_occurrences.items() if e['edition']==ed};ao={e['source_group_id']:e for e in occurrences if e['edition']==ed}
        check(ed+'_all_exact_free_ol_positions_separators_and_bound_status',len(ao)==sum(e['edition']==ed for e in occurrences) and equal(eo,ao,ed+'/occurrences'))
        cc=list(ep.values());ss=[c for c in cc if c['scorable']];contr=[c for c in ss if c['decision']=='CONTRADICTION']
        summaries[ed]={'all_P_ol':len(eo),'unbounded_ol':sum(e['paragraph'] is None for e in eo.values()),'complete_paragraphs':sum(b['edition']==ed for b in blocks),
          'ol_bearing_paragraphs':len(cc),'scorable_paragraphs':len(ss),'scorable_leaves':len({c['leaf'] for c in ss}),
          'paragraph_decisions':dict(Counter(c['decision'] for c in cc)),'scorable_odd_paragraphs':sum(c['unmatched_open'] is not None for c in ss),
          'scorable_empty_field_paragraphs':sum(c['empty_fields']>0 for c in ss),'scorable_adjacent_pair_paragraphs':sum(bool(c['adjacent_pairs']) for c in ss),
          'scorable_adjacent_pair_directions':dict(Counter(p['direction'] for c in ss for p in c['adjacent_pairs'])),
          'decision':'REFUTED_FIXED_PAIRED_FIELD_SCOPE' if contr else 'COMPATIBLE_UNSELECTED' if ss else 'INSUFFICIENT_CAPACITY'}
        check(ed+'_all_summary_violation_and_capacity_counts',equal(summaries[ed],result['readers'][ed],ed+'/summary'))
        violations[ed]={'odd_paragraphs':[c['id'] for c in ss if c['unmatched_open'] is not None],
          'empty_fields':[{'paragraph':c['id'],**f} for c in ss for f in c['fields'] if f['empty']]}
    check('complete_occurrence_and_paragraph_accounting_no_duplicates',len(occurrences)==len(expected_occurrences) and len(paragraphs)==len(expected))
    def textrow(row):return {k:'' if v is None else str(v) for k,v in row.items()}
    expected_decisions={c['id']:textrow({k:c[k] for k in ['edition','id','page','line_count','group_count','ol_count','scorable','decision','unmatched_open','empty_fields']}) for c in expected.values()}
    expected_pairs={}
    for c in expected.values():
        for p in c['adjacent_pairs']:
            row={'edition':c['edition'],'paragraph':c['id'],'scorable':c['scorable'],'decision':c['decision'],**p};expected_pairs[(c['id'],p['left_id'],p['right_id'])]=textrow(row)
    for name,ex,keyfn in [('PARAGRAPH_DECISIONS.tsv',expected_decisions,lambda row:row['id']),('ADJACENT_PAIRS.tsv',expected_pairs,lambda row:(row['paragraph'],row['left_id'],row['right_id']))]:
        with (BASE/'artifacts'/name).open(newline='') as f:rows=list(csv.DictReader(f,delimiter='\t'))
        actual={keyfn(row):row for row in rows};check(name+'_all_raw_references_and_decisions',len(rows)==len(actual) and equal(ex,actual,name))
    primary=[summaries[ed] for ed in ['ZL3b','IT2a']]
    decision='REFUTED_FIXED_PAIRED_FIELD_SCOPE' if any(r['decision']=='REFUTED_FIXED_PAIRED_FIELD_SCOPE' for r in primary) else 'PROVISIONAL_SCOPE_COMPATIBILITY' if all(r['scorable_paragraphs']>=10 and r['scorable_leaves']>=5 and r['scorable_adjacent_pair_paragraphs']>=2 for r in primary) else 'INSUFFICIENT_CAPACITY'
    check('complete_result_and_fixed_global_decision',equal({'experiment':'GDT1151','decision':decision,'readers':summaries,'confirmed_words':0,'independent_confirmation_capacity':0,'significance':'NOT_CLAIMED'},result,'result'))
    check('RF_unbounded_and_unscored_no_inherited_boundary',summaries['RF1b']['complete_paragraphs']==0 and summaries['RF1b']['unbounded_ol']==summaries['RF1b']['all_P_ol'] and not summaries['RF1b']['scorable_paragraphs'])
    check('all_registered_and_root_source_output_bytes_unchanged',all(sha(REPO/p)==h for p,h in pins.items()))
    out={'experiment':'GDT1151','accounting_pass':all(c['pass'] for c in checks),'checks':checks,'independent_decision':decision,'reader_summary':summaries,
      'all_scorable_violations':violations,'compared_totals':{'native_P_groups':all_native,'free_ol_occurrences':len(ol),'all_ol_bearing_paragraphs':len(expected),
       'proposed_closed_fields_including_unscorable_diagnostics':sum(len(c['fields']) for c in expected.values()),'adjacent_pair_table_rows':len(expected_pairs)},
      'validator_sha256':sha(Path(__file__)),'bound_hashes':pins,'mismatch_paths':mismatches,
      'limits':['Refutation applies to the fixed conjunction of paragraph reset, exact free-ol identity, native boundaries, alternating nonnested roles and nonempty fields.','All annotated paragraphs are UNTESTABLE; their stored role/field projections are diagnostics and are not used as contradictions.','Uncertain-small-space groups remain fixed native groups; no optical authentication is claimed.','Compatible subsets do not rescue universal contradictions; this does not refute all delimiters or any particular English meaning.','No significance, word meaning, independent semantic confirmation or reserve access is claimed.']}
    (BASE/'artifacts/VALIDATION.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'accounting_pass':out['accounting_pass'],'checks':len(checks),'failed':[c['name'] for c in checks if not c['pass']],'decision':decision,'compared_totals':out['compared_totals'],'mismatch_paths':mismatches}))
    return 0 if out['accounting_pass'] else 1
if __name__=='__main__':raise SystemExit(main())
