#!/usr/bin/env python3
"""Independent native-source reconstruction; no imports from runners/helpers."""
import hashlib,json,re,sys
from collections import Counter,defaultdict
from pathlib import Path
sys.dont_write_bytecode=True
BASE=Path(__file__).resolve().parents[1];REPO=BASE.parents[2]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def native_lines(lock):
    panels=defaultdict(list);allowed=set(read(REPO/'experiments/yolo/gdt915_terminal_lr_phrase_transfer/src/SPEC.json')['allowed_selectors'])
    for pin in lock['files']:
        match=re.search(r'SOURCE_(DISCOVERY|EVALUATION)_(ZL3b|IT2a|RF1b)\.json$',pin)
        if not match:continue
        reader=match.group(2);packet=read(REPO/pin)
        for row in packet['lines']:
            m=row['metadata'];assert m['page'] in allowed and not m['page'].startswith('f84') and m['page']!='f116v'
            if m['kind']!='P':continue
            groups=[dict(zip(packet['group_columns'],g)) for g in row['groups']]
            assert len(groups)==int(m['source_group_count'])
            ids=[g['source_group_id'] for g in groups];words=[g['ivtff_group_raw'] for g in groups]
            edges=[]
            for i in range(len(groups)-1):
                a,b=groups[i:i+2];edges.append(a['right_separator']=='DEFINITE_SPACE' and b['left_separator']=='DEFINITE_SPACE' and int(b['source_group_index'])-int(a['source_group_index'])==1)
            safe=[all(edges[max(0,i-1):min(len(edges),i+1)]) for i in range(len(groups))]
            panels[reader].append({'id':m['page']+'|'+m['locus'],'metadata':m,'words':words,'group_ids':ids,'safe':safe,'seams':edges,
              'literal_line':len(words)>=2 and all(re.fullmatch('[a-z]+',w) for w in words) and all(edges)})
    for reader,lines in panels.items():
        lines.sort(key=lambda line:(line['metadata']['page'],int(line['metadata']['source_row_index'])))
        assert len({line['id'] for line in lines})==len(lines)
    return panels

def reconstruct_paragraph(page_lines,host):
    index=page_lines.index(host);first=index;last=index
    while first>0 and page_lines[first]['metadata']['paragraph_start']!='1':first-=1
    while last<len(page_lines)-1 and page_lines[last]['metadata']['paragraph_end']!='1':last+=1
    has_start=page_lines[first]['metadata']['paragraph_start']=='1';has_end=page_lines[last]['metadata']['paragraph_end']=='1'
    chosen=page_lines[first:last+1];numbers=[int(line['metadata']['locus'].rsplit('.',1)[1]) for line in chosen]
    gap=any(b-a!=1 for a,b in zip(numbers,numbers[1:]));internal=any(line['metadata']['paragraph_start']=='1' for line in chosen[1:]) or any(line['metadata']['paragraph_end']=='1' for line in chosen[:-1])
    return {'seed':host['metadata']['locus'],'complete_marked_paragraph':has_start and has_end and not gap and not internal,
      'has_start':has_start,'has_end':has_end,'consecutive_loci':not gap,'internal_boundary':internal,'lines':chosen,'groups':sum(len(line['words']) for line in chosen)}

def enumerate_cases(panels,candidates):
    rows=[];paragraphs={};prefix_audits=[]
    for reader in ['ZL3b','IT2a','RF1b']:
        lines=panels[reader];lookup={line['id']:line for line in lines};pages=defaultdict(list)
        for line in lines:pages[line['metadata']['page']].append(line)
        for candidate in candidates:
            anchor=candidate['anchor'];forms=sorted(branch['next'] for branch in candidate['branches']);assert len(forms)==len(set(forms))==2
            for occurrence in candidate['occurrences']:
                line=lookup.get(occurrence['line']);actual=occurrence['next']
                row={'reader':reader,'context_id':candidate['id'],'anchor':anchor,'line':occurrence['line'],'chosen':actual,'competitors':forms,
                  'original_start':occurrence['start'],'leaf':occurrence['leaf']}
                wanted=anchor+[actual]
                indices=[i for i in range(len(line['words'])-len(wanted)+1) if line['words'][i:i+len(wanted)]==wanted] if line else []
                row['matches']=indices
                if line is None or len(indices)!=1 or not line['literal_line']:
                    row.update(status='UNTESTABLE',reason='NATIVE_TRIPLE_NOT_UNIQUE_OR_HOST_UNCERTAIN')
                    if line is not None:row['host_line']=line
                    rows.append(row);continue
                start=indices[0]
                if reader=='ZL3b':assert start==occurrence['start']
                assert int(re.match(r'f([0-9]+)',line['metadata']['page']).group(1))==occurrence['leaf']
                paragraph=reconstruct_paragraph(pages[line['metadata']['page']],line)
                key=reader+'|'+paragraph['lines'][0]['id']+'--'+paragraph['lines'][-1]['id'];paragraphs[key]={k:v for k,v in paragraph.items() if k!='seed'};row['paragraph_key']=key
                stream=[(part,i,w,gid) for part in paragraph['lines'] for i,(w,gid) in enumerate(zip(part['words'],part['group_ids']))]
                anchor_offset=next(i for i,(part,local,w,gid) in enumerate(stream) if part['id']==line['id'] and local==start)
                before=stream[:anchor_offset];reliable=all(re.fullmatch('[a-z]+',w) for part,local,w,gid in before)
                for prior in paragraph['lines']:
                    limit=start if prior['id']==line['id'] else len(prior['words'])
                    reliable=reliable and all(prior['seams'][:max(0,limit-1)])
                    if prior['id']==line['id']:break
                earlier={form:[{'word':w,'group_id':gid,'line':part['id'],'distance_to_anchor':anchor_offset-i} for i,(part,local,w,gid) in enumerate(before) if w==form] for form in forms}
                row.update(prefix_groups=len(before),prefix_reliable=bool(reliable),earlier=earlier,counts={form:len(items) for form,items in earlier.items()})
                prefix_audits.append({'reader':reader,'context_id':candidate['id'],'line':line['id'],'anchor_id':stream[anchor_offset][3],
                  'prefix_group_ids':[item[3] for item in before],'anchor_excluded':all(item[3]!=stream[anchor_offset][3] for item in before),
                  'one_group_prior_lines':sum(len(part['words'])==1 for part in paragraph['lines'][:paragraph['lines'].index(line)])})
                if not paragraph['complete_marked_paragraph']:row.update(status='UNTESTABLE',reason='NO_COMPLETE_MARKED_PARAGRAPH')
                elif not reliable:row.update(status='UNTESTABLE',reason='UNCERTAIN_PRIOR_SCOPE')
                else:
                    present=[form for form in forms if earlier[form]]
                    if len(present)!=1:row.update(status='ABSTAIN',reason='BOTH_PREVIOUS' if present else 'NEITHER_PREVIOUS')
                    else:row.update(predicted=present[0],status='COMPATIBLE' if present[0]==actual else 'CONTRADICTION',reason='EXACTLY_ONE_PREVIOUS')
                rows.append(row)
    return rows,paragraphs,prefix_audits


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
    lock=read(BASE/'PREREG_LOCK.json');nested=read(REPO/'experiments/yolo/gdt927_chor_continuation_full_context_audit/PREREG_LOCK.json')
    paths={**lock['files'],**nested['files']}
    watched=[REPO/p for p in paths]+[BASE/p for p in ['PREREG_LOCK.json','src/run.py','artifacts/CASES.json','artifacts/PARAGRAPHS.json','artifacts/RESULT.json','CANDIDATE_TABLE.md']]
    pins={str(p.relative_to(REPO)):sha(p) for p in watched}
    check('all_12_registration_and_source_pins',all(sha(REPO/p)==h for p,h in lock['files'].items()))
    check('all_referenced_927_legacy_pins',all(sha(REPO/p)==h for p,h in nested['files'].items()))
    candidates=read(REPO/'experiments/yolo/gdt926_repeated_context_continuation_atlas/artifacts/CANDIDATES_ZL3b.json')
    check('all_13_contexts_26_occurrences_two_first_divergent_forms',len(candidates)==13 and sum(len(c['occurrences']) for c in candidates)==26 and all(len(c['branches'])==2 and {o['next'] for o in c['occurrences']}=={b['next'] for b in c['branches']} and all(o['tail'][0]==o['next'] for o in c['occurrences']) for c in candidates))
    spec=read(REPO/'experiments/yolo/gdt915_terminal_lr_phrase_transfer/src/SPEC.json');check('sealed_and_unadmitted_scope',not {'f84','f84r','f116v'}&set(spec['allowed_selectors']))
    panels=native_lines(lock);rows,paragraphs,prefix_audits=enumerate_cases(panels,candidates)
    actual_rows=read(BASE/'artifacts/CASES.json');actual_paragraphs=read(BASE/'artifacts/PARAGRAPHS.json');actual_result=read(BASE/'artifacts/RESULT.json')
    summaries={};overlap={};violations=[]
    for reader in ['ZL3b','IT2a','RF1b']:
        expected=[row for row in rows if row['reader']==reader];actual=[row for row in actual_rows if row['reader']==reader]
        check(reader+'_all_26_host_matches_prefix_exclusion_counts_ids_distances_and_outcomes',len(expected)==26 and equal(expected,actual,reader+'/cases'))
        ep={k:p for k,p in paragraphs.items() if k.startswith(reader+'|')};ap={k:p for k,p in actual_paragraphs.items() if k.startswith(reader+'|')}
        check(reader+'_all_complete_partial_paragraph_metadata_words_ids_gaps_and_uncertainty',equal(ep,ap,reader+'/paragraphs'))
        counts=dict(Counter(row['status'] for row in expected));choice=[row for row in expected if row['status'] in ['COMPATIBLE','CONTRADICTION']]
        summary={'cases':len(expected),'counts':counts,'reasons':dict(Counter(row['reason'] for row in expected)),'physical_leaves':len({row['leaf'] for row in expected}),
          'choice_leaves':len({row['leaf'] for row in choice}),
          'complete_paragraphs':len({row['paragraph_key'] for row in expected if 'paragraph_key' in row and paragraphs[row['paragraph_key']]['complete_marked_paragraph']}),
          'decision':'CONTRADICTED' if counts.get('CONTRADICTION') else 'LOCALLY_COMPATIBLE' if counts.get('COMPATIBLE') else 'NO_CHOICE_CAPACITY'}
        summaries[reader]=summary;check(reader+'_all_panel_counts_leaf_capacity_and_decision',equal(summary,actual_result['panels'][reader],reader+'/summary'))
        uses=Counter(row['paragraph_key'] for row in expected if 'paragraph_key' in row);overlap[reader]={key:n for key,n in uses.items() if n>1}
        violations.extend(row for row in expected if row['status']=='CONTRADICTION')
    check('all_78_rows_order_retained_and_no_extra_selection',equal(rows,actual_rows,'all_cases'))
    check('all_prefixes_exclude_anchor_and_later_stream',all(a['anchor_excluded'] for a in prefix_audits))
    result={'status':'FIXED_PRIOR_CONTINUATION_CHOICE_COMPLETE','panels':summaries,'primary_case_count':26,'readers_are_alternatives':True,'independent_confirmation':0,'meanings_identified':0,'significance_claim':False}
    check('full_fixed_result_exact',equal(result,actual_result,'result'))
    # The table is also checked; untestable counts are rendered as diagnostic counts.
    table=['# All fixed continuation choices','','Counts concern only the complete paragraph prefix before the shared context. Uncertain prefixes are not scored. Readers are alternatives.','','|Reader|Context|Locus|Chosen|Competing earlier counts|Prediction|Outcome|Reason|','|---|---|---|---|---|---|---|---|']
    for row in rows:
        count_text=', '.join(w+':'+str(n) for w,n in row.get('counts',{}).items()) or 'unavailable'
        table.append('|'+ '|'.join([row['reader'],row['context_id'],row['line'].split('|')[1],row['chosen'],count_text,row.get('predicted','—'),row['status'],row['reason']])+'|')
    check('every_human_table_row_matches_independent_case',(BASE/'CANDIDATE_TABLE.md').read_text()=='\n'.join(table)+'\n')
    check('all_registered_legacy_runner_and_source_output_bytes_unchanged',all(sha(REPO/p)==h for p,h in pins.items()))
    out={'experiment':'GDT1153','accounting_pass':all(c['pass'] for c in checks),'checks':checks,'independent_panels':summaries,
      'contradictions':violations,'shared_paragraph_case_counts':overlap,'compared_totals':{'contexts':len(candidates),'original_occurrences':sum(len(c['occurrences']) for c in candidates),'reader_cases':len(rows),'retained_paragraph_windows':len(paragraphs),'prefix_audits':len(prefix_audits)},
      'prefix_anchor_exclusion_verified':all(a['anchor_excluded'] for a in prefix_audits),'native_one_group_prior_lines_retained':sum(a['one_group_prior_lines'] for a in prefix_audits),
      'validator_sha256':sha(Path(__file__)),'bound_hashes':pins,'mismatch_paths':mismatches,
      'artifact_schema_note':'Root removed the old helper call-specific seed label before paragraph deduplication; this validator compares all paragraph content/boundary fields and excludes only that documented metadata label.',
      'limits':['All sources and selected contexts were already exposed; no independent holdout or semantic confirmation.','Unknown/partial paragraph prior counts remain diagnostic; zero there is not an eligible absence claim.','Alternative readings and overlapping paragraphs are not independent cases.','Matching uses the complete literal host line and exact original anchor+chosen form, not repaired or reader-specific branch selection.','Contradictions refute only the fixed exactly-one-prior reuse selection rule, not anaphora, referent identity, meanings or IDEA198 generally.','No significance, whole-search null, meaning assignment, threshold repair or target expansion.']}
    (BASE/'artifacts/VALIDATION.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    md=['# GDT1153 independent validation','',f"Accounting: {'PASS' if out['accounting_pass'] else 'FAIL'} ({sum(c['pass'] for c in checks)}/{len(checks)} checks). No root/helper algorithm was imported.",'',
      'All 13 pinned ZL contexts and their 26 original occurrences were reconstructed in each reader directly from the six GDT915 native JSON snapshots. All 78 case rows, matched host strings, full/partial paragraph streams, prefix exclusions, competitor group IDs/counts/distances and decisions were compared.', '',
      '|Reader|Compatible|Contradiction|Abstain|Untestable|Decision|','|---|---:|---:|---:|---:|---|']
    for reader,s in summaries.items():md.append('|'+reader+'|'+ '|'.join(str(s['counts'].get(k,0)) for k in ['COMPATIBLE','CONTRADICTION','ABSTAIN','UNTESTABLE'])+'|'+s['decision']+'|')
    md += ['', 'The current shared context and all later words are excluded from prior memory. Missing boundaries or uncertain prior words/seams prevent scoring; recorded counts in these rows are descriptive only. One-word prior lines are allowed. All annotated words and native paragraph flags remain retained.', '',
      'The strict rule is contradicted separately in ZL and IT. This does not determine meanings, establish shared referents or refute other continuation rules. These are exposed development cases; reader alternatives and overlapping paragraph windows provide no independent confirmation or significance.', '',
      'Paragraph artifact metadata: root removed the old helper call-specific `seed` label before deduplication. This audit excludes only that label from paragraph serialization; all native lines, uncertainty and boundary checks are compared.', '', 'Reproduce: `python experiments/yolo/gdt1153_prior_continuation_choice/src/validate.py`.', '',
      'Detailed checks, all six contradiction rows, native source pins and overlapping paragraph counts are in VALIDATION.json.']
    (BASE/'artifacts/VALIDATION.md').write_text('\n'.join(md)+'\n')
    print(json.dumps({'accounting_pass':out['accounting_pass'],'checks':len(checks),'failed':[c['name'] for c in checks if not c['pass']],'panels':summaries,'mismatch_paths':mismatches}))
    return 0 if out['accounting_pass'] else 1
if __name__=='__main__':raise SystemExit(main())
