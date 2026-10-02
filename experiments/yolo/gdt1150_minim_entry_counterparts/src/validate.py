#!/usr/bin/env python3
"""Independent exact-window and exhaustive-partner audit; no runner import."""
import csv,gzip,hashlib,json,re,sys
from collections import Counter,defaultdict
from pathlib import Path
sys.dont_write_bytecode=True
BASE=Path(__file__).resolve().parents[1];REPO=BASE.parents[2]
FORMS={'ain','aiin','aiiin','dain','daiin','daiiin'};PURE=re.compile('[a-z]+')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(gzip.decompress(p.read_bytes())) if p.suffix=='.gz' else json.loads(p.read_text())

def reconstruct(source):
    fixed_blocks=read(REPO/next(p['path'] for p in source['inputs'] if p['path'].endswith('/BLOCKS.json')))
    old_cases=read(REPO/next(p['path'] for p in source['inputs'] if p['path'].endswith('/CASES.json.gz')))
    old_cases={e['source_group_id']:e for e in old_cases if e['ivtff_group_raw'] in FORMS}
    paragraphs={}
    for block in fixed_blocks:
        for locus in block['loci']:
            key=(block['edition'],locus);assert key not in paragraphs
            paragraphs[key]=block
    inventory={};seen=set();native_lines={};predecessor_consistent=True
    for pin in source['inputs']:
        match=re.search(r'SOURCE_(DISCOVERY|EVALUATION)_(ZL3b|IT2a|RF1b)\.json$',pin['path'])
        if not match:continue
        reader=match.group(2);packet=read(REPO/pin['path'])
        for row in packet['lines']:
            m=row['metadata']
            if m['kind']!='P':continue
            gs=[dict(zip(packet['group_columns'],g)) for g in row['groups']]
            n=int(m['source_group_count']);assert len(gs)==n
            assert [int(g['source_group_index']) for g in gs]==list(range(1,n+1))
            byindex={int(g['source_group_index']):g for g in gs};native_lines[(reader,m['locus'])]={'metadata':m,'groups':gs}
            block=paragraphs.get((reader,m['locus']))
            scope='UNBOUNDED' if block is None else 'SINGLE_LINE_PARAGRAPH' if block['line_count']==1 else 'SINGLE_GROUP_LINE' if n==1 else 'PRIMARY'
            for g in gs:
                assert g['source_group_id'] not in seen;seen.add(g['source_group_id'])
                raw=g['ivtff_group_raw']
                if raw not in FORMS:continue
                idx=int(g['source_group_index']);tail=raw[1:] if raw.startswith('d') else raw;kind='D' if raw.startswith('d') else 'BARE'
                position='INTERNAL' if idx!=1 else 'PARAGRAPH_START' if m['paragraph_start']=='1' else 'CONTINUATION_START'
                nexts=[byindex.get(idx+1),byindex.get(idx+2)]
                exists=all(x is not None for x in nexts)
                pure=exists and all(PURE.fullmatch(x['ivtff_group_raw']) for x in nexts)
                gaps=exists and g['right_separator']=='DEFINITE_SPACE' and nexts[0]['left_separator']=='DEFINITE_SPACE' and nexts[0]['right_separator']=='DEFINITE_SPACE' and nexts[1]['left_separator']=='DEFINITE_SPACE'
                eligible=scope=='PRIMARY' and exists and pure and gaps
                signature=(tail,*(x['ivtff_group_raw'] for x in nexts)) if eligible else None
                e={'reader':reader,'metadata':m,'source_line':row,'native':g,'scope':scope,'position':position,'paragraph':block['id'] if block else None,
                   'paragraph_lines':block['line_count'] if block else None,'class':kind,'tail':tail,'leaf':int(re.match(r'f([0-9]+)',m['page']).group(1)),
                   'nexts':nexts,'successors_exist':exists,'successors_pure':bool(pure),'definite_gaps':bool(gaps),'eligible':eligible,'signature':signature}
                inventory[g['source_group_id']]=e
                old=old_cases.get(g['source_group_id']);expected={**g,'edition':reader,'page':m['page'],'locus':m['locus'],'leaf':e['leaf'],
                  'class':'D_MINIM' if kind=='D' else 'BARE_MINIM','scope':scope,'position':position,'paragraph':e['paragraph'],'paragraph_lines':e['paragraph_lines'],
                  'source_group_count':n,'paragraph_start':m['paragraph_start'],'paragraph_end':m['paragraph_end']}
                predecessor_consistent=predecessor_consistent and old==expected
    predecessor_consistent=predecessor_consistent and set(old_cases)==set(inventory)
    pairs={}
    for sid,e in inventory.items():
        if not (e['eligible'] and e['class']=='D' and e['position']=='CONTINUATION_START'):continue
        matches={}
        for label in ['PARAGRAPH','LEAF']:
            candidates=[(tid,t) for tid,t in inventory.items() if t['reader']==e['reader'] and t['eligible'] and t['position']=='INTERNAL'
                and t['signature']==e['signature'] and (t['paragraph']==e['paragraph'] if label=='PARAGRAPH' else t['leaf']==e['leaf'])]
            kinds={t['class'] for tid,t in candidates}
            matches[label]={'partners':sorted(tid for tid,t in candidates),'bare':sorted(tid for tid,t in candidates if t['class']=='BARE'),
                'D':sorted(tid for tid,t in candidates if t['class']=='D'),
                'status':'BOTH' if kinds=={'BARE','D'} else 'BARE_ONLY' if kinds=={'BARE'} else 'D_ONLY' if kinds=={'D'} else 'NEITHER'}
        pairs[sid]=matches
    return inventory,pairs,native_lines,predecessor_consistent


def window_record(e):
    m=e['metadata'];g=e['native'];reasons=[]
    if e['scope']!='PRIMARY':reasons.append(e['scope'])
    if not e['successors_exist']:reasons.append('FEWER_THAN_TWO_FOLLOWING_GROUPS')
    else:
        if not e['successors_pure']:reasons.append('ANNOTATED_FOLLOWING_GROUP')
        if not e['definite_gaps']:reasons.append('NONDEFINITE_GAP')
    return {**g,'edition':e['reader'],'page':m['page'],'locus':m['locus'],'leaf':e['leaf'],
      'class':'D_MINIM' if e['class']=='D' else 'BARE_MINIM','scope':e['scope'],'position':e['position'],
      'paragraph':e['paragraph'],'paragraph_lines':e['paragraph_lines'],'source_group_count':int(m['source_group_count']),
      'paragraph_start':m['paragraph_start'],'paragraph_end':m['paragraph_end'],'tail':e['tail'],'form_class':e['class'],
      'following':[q['ivtff_group_raw'] for q in e['nexts'] if q is not None],'eligible':e['eligible'],
      'exclusion_reasons':reasons,'source_line':e['source_line']}

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
    paths=[BASE/f for f in ['METHOD.md','PREREGISTRATION.md','src/SOURCE.json','src/PREREG_LOCK.json','src/run.py','artifacts/WINDOWS.json.gz','artifacts/PARTNERS.json','artifacts/RESULT.json']]
    paths += [REPO/p['path'] for p in source['inputs']];pins={str(p.relative_to(REPO)):sha(p) for p in paths}
    check('registration_exact_method_and_source_byte_lock',all(sha(BASE/p)==h for p,h in lock['hashes'].items()))
    check('all_11_source_and_predecessor_byte_pins',all(sha(REPO/p['path'])==p['sha256'] for p in source['inputs']))
    spec=read(REPO/source['inputs'][0]['path']);allowed=set(spec['allowed_selectors'])
    snapshots=[p for p in source['inputs'] if re.search(r'SOURCE_(DISCOVERY|EVALUATION)_(ZL3b|IT2a|RF1b)\.json$',p['path'])]
    check('six_exact_snapshots_and_sealed_unadmitted_scope',len(snapshots)==6 and not {'f84','f84r','f116v'}&allowed and all(row['metadata']['page'] in allowed and not row['metadata']['page'].startswith('f84') for p in snapshots for row in read(REPO/p['path'])['lines']))
    events,pairs,lines,previous_ok=reconstruct(source)
    check('every_six_form_native_case_exact_1149_scope_and_block',previous_ok)
    windows=read(BASE/'artifacts/WINDOWS.json.gz');partner_rows=read(BASE/'artifacts/PARTNERS.json');result=read(BASE/'artifacts/RESULT.json')
    expected_windows={sid:window_record(e) for sid,e in events.items()};expected_partners={};expected_readers={};compact={};seam_agreement=True
    for sid,e in events.items():
        if e['successors_exist']:
            g=e['native'];a,b=e['nexts']
            seam_agreement=seam_agreement and g['right_separator']==a['left_separator'] and a['right_separator']==b['left_separator']
        if sid in pairs:
            expected_partners[sid]={'target_id':sid,'edition':e['reader'],'tail':e['tail'],
              'following':[q['ivtff_group_raw'] for q in e['nexts']],
              **{k:{'category':pairs[sid][label]['status'],'BARE':pairs[sid][label]['bare'],'D':pairs[sid][label]['D']} for k,label in [('paragraph','PARAGRAPH'),('leaf','LEAF')]}}
    check('both_native_sides_of_each_gap_agree_in_all_two_successor_targets',seam_agreement)
    # Runner tests successor left separators; this equivalence is source-bound,
    # while this audit independently tests BOTH sides and original indices.
    for reader in ['ZL3b','IT2a','RF1b']:
        expected={sid:w for sid,w in expected_windows.items() if w['edition']==reader};actual={w['source_group_id']:w for w in windows if w['edition']==reader}
        check(reader+'_complete_inventory_every_window_exclusion_and_full_source_line',len(actual)==sum(w['edition']==reader for w in windows) and equal(expected,actual,reader+'/windows'))
        ep={sid:p for sid,p in expected_partners.items() if p['edition']==reader};ap={p['target_id']:p for p in partner_rows if p['edition']==reader}
        check(reader+'_all_eligible_D_entry_targets_and_exhaustive_partner_sets',len(ap)==sum(p['edition']==reader for p in partner_rows) and equal(ep,ap,reader+'/partners'))
        rr=list(expected.values());exclusions=Counter(reason for w in rr for reason in w['exclusion_reasons'])
        counts={'all_targets':len(rr),'eligible':sum(w['eligible'] for w in rr),'eligible_D_continuation':len(ep),
          'exclusions':dict(exclusions),'counterparts':{scope:dict(Counter(p[scope]['category'] for p in ep.values())) for scope in ['paragraph','leaf']}}
        expected_readers[reader]=counts
        check(reader+'_all_reader_inventory_exclusion_and_classification_counts',equal(counts,result['readers'][reader],reader+'/counts'))
        compact[reader]={**counts,'exact_form_inventory':dict(Counter(w['ivtff_group_raw'] for w in rr)),
          'eligible_classes_positions':dict(Counter(w['form_class']+':'+w['position'] for w in rr if w['eligible']))}
    check('full_inventory_partner_target_coverage_without_duplicates',len(windows)==len(expected_windows) and len(partner_rows)==len(expected_partners))
    check('window_native_ID_sort_reproducible', [w['source_group_id'] for w in windows]==sorted(expected_windows))
    available=[any(p['edition']==r and p['paragraph']['BARE'] for p in expected_partners.values()) for r in ['ZL3b','IT2a']]
    decision='LOCAL_COUNTERPARTS_AVAILABLE' if all(available) else 'READING_SENSITIVE_COUNTERPARTS' if any(available) else 'NO_LOCAL_COUNTERPARTS'
    expected_result={'experiment':'GDT1150','decision':decision,'readers':expected_readers,'confirmed_words':0,'independent_confirmation_capacity':0,'significance':'NOT_CLAIMED'}
    check('registered_existence_gate_and_complete_result_exact',equal(expected_result,result,'result'))
    check('RF_no_bounded_or_eligible_windows',all(e['scope']=='UNBOUNDED' and not e['eligible'] for e in events.values() if e['reader']=='RF1b'))
    check('all_source_predecessor_runner_and_result_bytes_unchanged',all(sha(REPO/p)==h for p,h in pins.items()))
    out={'experiment':'GDT1150','accounting_pass':all(c['pass'] for c in checks),'checks':checks,'independent_decision':decision,
      'reader_summary':compact,'compared_totals':{'all_exact_six_form_P_occurrences':len(events),'eligible_windows':sum(e['eligible'] for e in events.values()),
          'D_continuation_targets':len(expected_partners),'all_paragraph_partners':sum(len(p['paragraph']['BARE'])+len(p['paragraph']['D']) for p in expected_partners.values()),
          'all_physical_leaf_partners':sum(len(p['leaf']['BARE'])+len(p['leaf']['D']) for p in expected_partners.values())},
      'validator_sha256':sha(Path(__file__)),'bound_hashes':pins,'mismatch_paths':mismatches,
      'implementation_note':'Root checks successor-left separators. Both seam sides agree in every source-bound two-successor target; independent eligibility explicitly requires both sides and native consecutive indices.',
      'limits':['Zero counterpart means no exact fixed-tail + next-two-whole-group match in these eligible windows.','No looser window, new corpus, repaired uncertainty, or reserve access was used.','NEITHER and D_ONLY cannot refute neutralization or determine the unobserved latent source class.','Written signatures are not established full clauses or constructions.','Exposed sources and alternate readers provide no independent meaning confirmation; no meaning, silent d, significance, or semantic PASS is certified.']}
    (BASE/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({'accounting_pass':out['accounting_pass'],'checks':len(checks),'failed':[c['name'] for c in checks if not c['pass']],'decision':decision,'compared_totals':out['compared_totals'],'mismatch_paths':mismatches}))
    return 0 if out['accounting_pass'] else 1
if __name__=='__main__':raise SystemExit(main())
