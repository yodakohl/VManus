#!/usr/bin/env python3
"""Independent native-position census; does not import run.py."""
import csv,gzip,hashlib,json,re,sys
from collections import Counter,defaultdict
from pathlib import Path
sys.dont_write_bytecode=True
BASE=Path(__file__).resolve().parents[1];REPO=BASE.parents[2]
PURE=re.compile('[a-z]+');BARE={'ain','aiin','aiiin'};D={'dain','daiin','daiiin'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(gzip.decompress(p.read_bytes())) if p.suffix=='.gz' else json.loads(p.read_text())
def cls(raw):
    if not PURE.fullmatch(raw):return 'UNCERTAIN'
    return 'BARE_MINIM' if raw in BARE else 'D_MINIM' if raw in D else 'OTHER_A' if raw.startswith('a') else 'OTHER'

def native_reader(source,reader):
    pages=defaultdict(list);ids=[]
    for pin in source['inputs']:
        if not re.search(r'SOURCE_(DISCOVERY|EVALUATION)_'+reader+r'\.json$',pin['path']):continue
        packet=read(REPO/pin['path'])
        for row in packet['lines']:
            m=row['metadata'];groups=[dict(zip(packet['group_columns'],g)) for g in row['groups']]
            assert len(groups)==int(m['source_group_count'])
            assert [int(g['source_group_index']) for g in groups]==list(range(1,len(groups)+1))
            ids.extend(g['source_group_id'] for g in groups)
            pages[m['page']].append({'metadata':m,'groups':groups})
    assert len(ids)==len(set(ids))
    for page in pages:pages[page].sort(key=lambda line:int(line['metadata']['source_row_index']))
    return pages

def census(pages):
    paragraphs=[];membership={};status={};prose=[]
    for page,lines in pages.items():
        pending=[]
        for line in lines:
            m=line['metadata'];locus=m['locus']
            if m['kind']!='P':continue
            prose.append(line)
            if m['paragraph_start']=='1':
                for old in pending:status[old['metadata']['locus']]='INVALIDATED_BY_NEW_START'
                pending=[line]
            elif pending:pending.append(line)
            else:status[locus]='END_WITHOUT_START' if m['paragraph_end']=='1' else 'NO_OPEN_START'
            if m['paragraph_end']=='1' and pending:
                pi=len(paragraphs);paragraphs.append(pending)
                for offset,part in enumerate(pending):membership[part['metadata']['locus']]=(pi,offset);status[part['metadata']['locus']]='COMPLETE'
                pending=[]
        for old in pending:status[old['metadata']['locus']]='OPEN_REMAINDER'
    inventory=Counter();words=defaultdict(Counter);position=defaultdict(Counter);details=[];diagnostic=Counter();leaves=defaultdict(set);tailcounts=defaultdict(Counter)
    for line in prose:
        m=line['metadata'];locus=m['locus'];n=len(line['groups']);pm=membership.get(locus);block=paragraphs[pm[0]] if pm else None
        if pm and len(block)>=2 and n>=2:category='PARAGRAPH_START' if pm[1]==0 else 'CONTINUATION_START'
        else:category=None
        if not pm:diagnostic['unbounded_P_lines']+=1
        elif len(block)==1:diagnostic['complete_singleline_P_lines']+=1
        if n==1:diagnostic['singlegroup_P_lines']+=1
        for g in line['groups']:
            raw=g['ivtff_group_raw'];c=cls(raw);idx=int(g['source_group_index']);inventory[c]+=1
            if c in ('BARE_MINIM','D_MINIM','OTHER_A'):words[c][raw]+=1
            pos=(category if idx==1 else 'INTERNAL') if category else None
            if pos:
                position[pos]['ALL_NATIVE']+=1
                if c!='UNCERTAIN':position[pos]['ALL_PURE']+=1
                position[pos][c]+=1
                if c in ('BARE_MINIM','D_MINIM','OTHER_A'):leaves[(pos,c)].add(int(re.match(r'f([0-9]+)',m['page']).group(1)))
                if c in ('BARE_MINIM','D_MINIM'):tailcounts[pos][raw]+=1
            if c in ('BARE_MINIM','D_MINIM','OTHER_A'):
                details.append({'metadata':m,'native':g,'class':c,'primary_position':pos,'block':block,'block_index':pm[1] if pm else None,
                                'paragraph_status':status[locus],'first':idx==1,'full_line':line})
    bare_leaf=set()
    for line in prose:
        if line['metadata']['locus'] in membership and any(cls(g['ivtff_group_raw'])=='BARE_MINIM' for g in line['groups']):
            bare_leaf.add(int(re.match(r'f([0-9]+)',line['metadata']['page']).group(1)))
    capacity=(position['CONTINUATION_START']['ALL_NATIVE']>=100 and position['INTERNAL']['BARE_MINIM']>=50 and len(bare_leaf)>=5)
    other_control=(position['CONTINUATION_START']['OTHER_A']>=5 and len(leaves[('CONTINUATION_START','OTHER_A')])>=2)
    d_control=(position['CONTINUATION_START']['D_MINIM']>=10 and len(leaves[('CONTINUATION_START','D_MINIM')])>=3)
    return {'paragraphs':paragraphs,'membership':membership,'status':status,'prose':prose,'inventory':inventory,'words':words,'positions':position,
      'cases':details,'diagnostics':diagnostic,'leaves':leaves,'tailcounts':tailcounts,'bare_complete_leaves':bare_leaf,
      'capacity':capacity,'other_control':other_control,'d_control':d_control}


def block_record(block,reader):
    first=block[0]['metadata'];last=block[-1]['metadata']
    return {'edition':reader,'id':reader+'|'+first['page']+'|'+first['locus']+'..'+last['locus'],
            'page':first['page'],'loci':[line['metadata']['locus'] for line in block],'line_count':len(block)}

def native_scope(line,block):
    return 'UNBOUNDED' if block is None else 'SINGLE_LINE_PARAGRAPH' if len(block)==1 else 'SINGLE_GROUP_LINE' if len(line['groups'])==1 else 'PRIMARY'

def main():
    checks=[];mismatches=[]
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
    def check(name,ok):checks.append({'name':name,'pass':bool(ok)})
    source=read(BASE/'src/SOURCE.json');lock=read(BASE/'src/PREREG_LOCK.json')
    paths=[BASE/f for f in ['METHOD.md','PREREGISTRATION.md','src/SOURCE.json','src/PREREG_LOCK.json','src/run.py',
          'artifacts/RESULT.json','artifacts/BLOCKS.json','artifacts/CASES.json.gz','artifacts/ALL_FIRST_LINES.json.gz','artifacts/CANDIDATES.tsv']]
    paths += [REPO/p['path'] for p in source['inputs']]
    pins={str(p.relative_to(REPO)):sha(p) for p in paths}
    check('registration_method_source_byte_lock',all(sha(BASE/k)==h for k,h in lock['hashes'].items()))
    check('nine_bound_source_and_predecessor_byte_pins',all(sha(REPO/p['path'])==p['sha256'] for p in source['inputs']))
    spec=read(REPO/source['inputs'][0]['path']);allowed=set(spec['allowed_selectors'])
    check('sealed_and_unadmitted_selectors_absent',not {'f84','f84r','f116v'}&allowed)
    packets=[pin for pin in source['inputs'] if re.search(r'SOURCE_(DISCOVERY|EVALUATION)_(ZL3b|IT2a|RF1b)\.json$',pin['path'])]
    check('exact_six_snapshots_with_allowlisted_metadata',len(packets)==6 and all(row['metadata']['page'] in allowed and not row['metadata']['page'].startswith('f84') for pin in packets for row in read(REPO/pin['path'])['lines']))
    result=read(BASE/'artifacts/RESULT.json');cases=read(BASE/'artifacts/CASES.json.gz');blocks=read(BASE/'artifacts/BLOCKS.json');firstlines=read(BASE/'artifacts/ALL_FIRST_LINES.json.gz')
    expected_readers={};all_cases={};all_blocks={};all_firsts={};expected_table={};compact={};tail_summary={};counterexamples=[];control_examples={}
    for reader in ['ZL3b','IT2a','RF1b']:
        pages=native_reader(source,reader);c=census(pages);expected_blocks={b['id']:b for b in [block_record(block,reader) for block in c['paragraphs']]}
        actual_blocks={b['id']:b for b in blocks if b['edition']==reader}
        check(reader+'_all_flag_selected_complete_blocks_exact_native_order',len(actual_blocks)==sum(b['edition']==reader for b in blocks) and equal(expected_blocks,actual_blocks,reader+'/blocks'));all_blocks.update(expected_blocks)
        check(reader+'_every_P_line_has_one_complete_or_unbounded_status',len(c['status'])==len(c['prose']) and len(c['membership'])==sum(len(b) for b in c['paragraphs']))
        expected_cases={};expected_first={};forms=defaultdict(Counter);first_counts=Counter();diagnostic=Counter();bare_multiline=set()
        for line in c['prose']:
            m=line['metadata'];member=c['membership'].get(m['locus']);block=c['paragraphs'][member[0]] if member else None
            scope=native_scope(line,block);n=len(line['groups']);leaf=int(re.match('f([0-9]+)',m['page']).group(1))
            if block and len(block)>=2 and any(cls(g['ivtff_group_raw'])=='BARE_MINIM' for g in line['groups']):bare_multiline.add(leaf)
            diagnostic['ALL_P_GROUPS']+=n;diagnostic[scope]+=n
            if block and len(block)==1:diagnostic['FLAG_SINGLE_LINE_PARAGRAPH']+=n
            if n==1:diagnostic['FLAG_SINGLE_GROUP_LINE']+=n
            for g in line['groups']:
                k=cls(g['ivtff_group_raw']);idx=int(g['source_group_index']);pos='PARAGRAPH_START' if idx==1 and m['paragraph_start']=='1' else 'CONTINUATION_START' if idx==1 else 'INTERNAL'
                if idx==1:first_counts[k]+=1
                if k not in ['BARE_MINIM','D_MINIM','OTHER_A']:continue
                f=forms[g['ivtff_group_raw']];f['ALL']+=1;f['ALL_FIRST' if idx==1 else 'ALL_NONFIRST']+=1;f[scope+':'+pos]+=1
                e={**g,'edition':reader,'page':m['page'],'locus':m['locus'],'leaf':leaf,'class':k,'scope':scope,'position':pos,
                   'paragraph':block_record(block,reader)['id'] if block else None,'paragraph_lines':len(block) if block else None,
                   'source_group_count':n,'paragraph_start':m['paragraph_start'],'paragraph_end':m['paragraph_end']}
                expected_cases[g['source_group_id']]=e
                if idx==1:expected_first[reader+'|'+m['locus']]=line
                if scope=='PRIMARY' and pos=='CONTINUATION_START' and k=='BARE_MINIM':counterexamples.append(e['source_group_id'])
        positions={pos:{('ALL' if k=='ALL_NATIVE' else 'PURE' if k=='ALL_PURE' else k):v for k,v in c['positions'].get(pos,{}).items() if v} for pos in ['PARAGRAPH_START','CONTINUATION_START','INTERNAL']}
        # Each primary category is disjoint; excluded scopes plus primary exhaust native P groups.
        check(reader+'_all_native_group_and_pure_denominators_exhaustive',sum(diagnostic[k] for k in ('PRIMARY','UNBOUNDED','SINGLE_LINE_PARAGRAPH','SINGLE_GROUP_LINE'))==sum(c['inventory'].values()) and sum(v.get('ALL',0) for v in positions.values())==diagnostic['PRIMARY'] and all(v.get('PURE',0)+v.get('UNCERTAIN',0)==v.get('ALL',0) for v in positions.values()))
        leafsets={k:sorted(v) for (pos,k),v in c['leaves'].items() if pos=='CONTINUATION_START' and v}
        # Include all classes' continuation leaf sets, not just the target/control classes.
        for line in c['prose']:
            member=c['membership'].get(line['metadata']['locus']);block=c['paragraphs'][member[0]] if member else None
            if not block or len(block)<2 or len(line['groups'])<2 or member[1]==0:continue
            k=cls(line['groups'][0]['ivtff_group_raw']);leaf=int(re.match('f([0-9]+)',line['metadata']['page']).group(1))
            leafsets.setdefault(k,[])
            if leaf not in leafsets[k]:leafsets[k].append(leaf)
        leafsets={k:sorted(v) for k,v in leafsets.items()}
        other=(positions['CONTINUATION_START'].get('OTHER_A',0)>=5 and len(leafsets.get('OTHER_A',[]))>=2)
        dent=(positions['CONTINUATION_START'].get('D_MINIM',0)>=10 and len(leafsets.get('D_MINIM',[]))>=3)
        capacity=(positions['CONTINUATION_START'].get('ALL',0)>=100 and positions['INTERNAL'].get('BARE_MINIM',0)>=50 and len(bare_multiline)>=5)
        expected={'inventory':dict(c['inventory']),'all_P_first_groups':dict(first_counts),'complete_paragraphs':len(c['paragraphs']),
           'diagnostic_scopes':dict(diagnostic),'positions':positions,'forms':{k:dict(v) for k,v in forms.items()},
           'bare_multiline_paragraph_leaves':sorted(bare_multiline),'continuation_leaves':leafsets,'capacity':capacity,'other_a_control':other,'d_entry_capacity':dent}
        actual_cases={e['source_group_id']:e for e in cases if e['edition']==reader}
        check(reader+'_every_target_and_all_other_A_case_fields_flags_scopes',len(actual_cases)==sum(e['edition']==reader for e in cases) and equal(expected_cases,actual_cases,reader+'/cases'))
        actual_first={k:v for k,v in firstlines.items() if k.startswith(reader+'|')}
        check(reader+'_all_first_position_cases_have_full_exact_native_lines',equal(expected_first,actual_first,reader+'/full_first_lines'))
        check(reader+'_all_inventory_forms_positions_diagnostics_and_gates',equal(expected,result['readers'][reader],reader+'/result'))
        all_cases.update(expected_cases);all_firsts.update(expected_first);expected_readers[reader]=expected
        for form,counts in forms.items():expected_table[(reader,form)]={'edition':reader,'form':form,**{k:counts.get(k,0) for k in ['ALL','ALL_FIRST','ALL_NONFIRST','PRIMARY:PARAGRAPH_START','PRIMARY:CONTINUATION_START','PRIMARY:INTERNAL']}}
        tail_summary[reader]={tail:{pos:{'BARE':c['tailcounts'].get(pos,{}).get(tail,0),'D':c['tailcounts'].get(pos,{}).get('d'+tail,0)} for pos in ['PARAGRAPH_START','CONTINUATION_START','INTERNAL']} for tail in ['ain','aiin','aiiin']}
        compact[reader]={'all_P_groups':sum(c['inventory'].values()),'all_P_lines':len(c['prose']),'complete_paragraphs':len(c['paragraphs']),'inventory':dict(c['inventory']),
          'positions':positions,'diagnostic_scopes':dict(diagnostic),'capacity':capacity,'other_a_control':other,'d_entry_capacity':dent,
          'bare_multiline_leaves':len(bare_multiline),'other_A_continuation_leaves':leafsets.get('OTHER_A',[]),'D_continuation_leaf_count':len(leafsets.get('D_MINIM',[])),
          'cases':len(expected_cases),'first_position_lines':len(expected_first)}
        control_examples[reader]=[e['source_group_id'] for e in expected_cases.values() if e['class']=='OTHER_A' and e['scope']=='PRIMARY' and e['position']=='CONTINUATION_START']
    check('all_case_block_and_firstline_references_exhaustive',len(cases)==len(all_cases) and len(blocks)==len(all_blocks) and len(firstlines)==len(all_firsts))
    with (BASE/'artifacts/CANDIDATES.tsv').open(newline='') as f:table=list(csv.DictReader(f,delimiter='\t'))
    actual_table={}
    for row in table:
        for k in row:
            if k not in ('edition','form'):row[k]=int(row[k])
        actual_table[(row['edition'],row['form'])]=row
    check('every_CANDIDATES_TSV_member_and_position_count',len(table)==len(actual_table) and equal(expected_table,actual_table,'table'))
    primary=[expected_readers[r] for r in ['ZL3b','IT2a']]
    decision='INSUFFICIENT_CAPACITY' if not all(r['capacity'] for r in primary) else 'BARE_SERIES_BAN_CONTRADICTED' if counterexamples else 'MINIM_SPECIFIC_CONTINUATION_AVOIDANCE' if all(r['other_a_control'] and r['d_entry_capacity'] for r in primary) else 'CONTROL_OR_DENTRY_CAPACITY_INSUFFICIENT'
    expected_result={'experiment':'GDT1149','decision':decision,'readers':expected_readers,'confirmed_words':0,'independent_confirmation_capacity':0,'significance':'NOT_CLAIMED','RF':'LINE_DIAGNOSTICS_ONLY_NO_NATIVE_PARAGRAPH_FLAGS'}
    check('full_result_and_registered_decision_exact',equal(expected_result,result,'result'))
    check('all_bound_source_protocol_runner_and_output_bytes_unchanged',all(sha(REPO/p)==h for p,h in pins.items()))
    out={'experiment':'GDT1149','accounting_pass':all(c['pass'] for c in checks),'checks':checks,'independent_decision':decision,'reader_summary':compact,
      'tail_position_counts':tail_summary,'all_bare_primary_continuation_counterexamples':counterexamples,'other_A_primary_continuation_cases':control_examples,
      'compared_totals':{'native_P_groups':sum(r['all_P_groups'] for r in compact.values()),'target_and_control_cases':len(all_cases),'complete_blocks':len(all_blocks),'full_first_position_lines':len(all_firsts),'candidate_table_rows':len(expected_table)},
      'validator_sha256':sha(Path(__file__)),'bound_hashes':pins,'mismatch_paths':mismatches,
      'limits':['This audits registered source selection and census, not native visual truth or meanings.','Previously exposed sources and alternate readers provide no independent meaning confirmation.','RF has no native paragraph flags; all RF P groups remain unbounded diagnostics.','The result is a fixed-scope descriptive pattern, not a significance test, causal explanation, or proof of a universal manuscript-wide ban.','No same-meaning, silent-d, minim-numeral, clause-boundary, pronunciation, or English translation is established.']}
    (BASE/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({'accounting_pass':out['accounting_pass'],'checks':len(checks),'failed':[c['name'] for c in checks if not c['pass']],'decision':decision,'compared_totals':out['compared_totals'],'mismatch_paths':mismatches}))
    return 0 if out['accounting_pass'] else 1
if __name__=='__main__':raise SystemExit(main())
