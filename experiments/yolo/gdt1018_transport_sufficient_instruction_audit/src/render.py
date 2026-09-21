"""Post-result presentation and lossless JSON compaction; no scientific query."""
from common import *
import csv,collections

def table(name,fields,rows):
    with (A/name).open('w') as f:
        w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)

def main():
    rows=read(A/'ROWS.json');originals={r['id']:r for r in rows if r['scope']=='original'}
    saved=[r for r in rows if r['scope']=='saved'];lifts=[r for r in rows if r['scope']=='lift']
    cases=read(R/inputs()['source_cases']);candidates=[]
    for c in cases:
        for m in c['members']:
            checked=[r for r in lifts if r['case']==c['id'] and r['original_id']==m['original_id']]
            good=[r for r in checked if r['result']['status']=='SUFFICIENT']
            original=originals[m['original_id']+'_V'+str(c['variant_index'])]
            assert original['result']['status']=='SUFFICIENT'
            candidates.append(dict(case=c['id'],original=m['original_id'],variant_index=c['variant_index'],context=c['context'],prediction='Every currently safe choice must satisfy whole suffix',original_status=original['result']['status'],saved_witnesses=len({r['witness'] for r in checked}),saved_lifts=len(checked),sufficient_lifts=len(good),positive_saved_witnesses=','.join(sorted({r['witness'] for r in good})),status='SAVED_SUFFICIENT_EXTENSION' if good else 'NO_SAVED_SUFFICIENT_WITNESS_FULL_SPACE_OPEN',independent_meaning_capacity=0))
    assert len(candidates)==312
    table('CANDIDATES.tsv',list(candidates[0]),candidates)
    summaries=[];words=[];text=['# All29 fixed complete readings under the new instruction law','All values remain hypothetical. No aliases were changed. C/G/W are unnamed cargo roles.']
    panel=read(R/inputs()['source_panel']);sourceby={p['id']:p for p in panel}
    for r in saved:
        a=r['result'];own=[x for x in lifts if x['witness']==r['id']]
        summaries.append(dict(witness=r['id'],context=r['context'],status=a['status'],successful_safe_paths=a['successful_paths'],failed_safe_prefixes=a['failed_prefixes'],open_choice_prefixes=len(a['choices']),multi_eligible_prefixes=sum(len(c['eligible'])>1 for c in a['choices']),then_positions=sum(c['kind']=='THEN' for c in r['parse']),lifts=len(own),first_failure=json.dumps(a['failures'][0] if a['failures'] else None,separators=(',',':')),independent_meaning_capacity=0))
        for word,value in sorted(r['aliases'].items()):words.append(dict(witness=r['id'],word=word,value=value,provenance='unchanged GDT1013 saved dictionary'))
        text += ['', '## '+r['id']+' — '+a['status'], '', 'Setting: `'+json.dumps(r['variant'],sort_keys=True)+'`', '', '|Clause|Groups (1-based)|Written complete span|Assumed construction|', '|---|---|---|---|']
        paragraph=sourceby[r['context']]
        for i,c in enumerate(r['parse'],1):text.append('|S%02d|%s–%s|%s|%s %s|'%(i,c['start']+1,c['end'],' '.join(paragraph['words'][c['start']:c['end']]),c['kind'],' '.join(c['symbols'])))
        text += ['',f"Successful eligible complete paths: {a['successful_paths']}; failed eligible prefixes: {a['failed_prefixes']}."]
        if a['status']=='SUFFICIENT':
            for path in a['successes']:text.append('Voyages: '+' → '.join(t['clause']+':'+(t['load'] or 'empty') for t in path)+'.')
        else:
            for failure in a['failures']:text.append('- '+failure['clause']+' '+failure['reason']+'; prefix '+', '.join(t['clause']+':'+(t['load'] or 'empty') for t in failure['trace'])+'.')
    table('SAVED_WITNESSES.tsv',list(summaries[0]),summaries);table('ALL_WORD_ASSIGNMENTS.tsv',list(words[0]),words)
    (A/'READINGS.md').write_text('\n'.join(text)+'\n')
    result=dict(status='SUPPORTED_LIMITED_TWO_FIXED_SUFFICIENT_READINGS',original_settings=156,original_sufficient=156,saved=29,saved_sufficient=2,saved_insufficient=27,member_lifts=492,sufficient_lifts=30,member_cases=312,constructively_retained_member_cases=sum(c['sufficient_lifts']>0 for c in candidates),full_extension_space_not_tested_member_cases=sum(c['sufficient_lifts']==0 for c in candidates),positive_witnesses=[r['id'] for r in saved if r['result']['status']=='SUFFICIENT'],original_codes_with_saved_sufficient_extension=len({c['original'] for c in candidates if c['sufficient_lifts']}),confirmed_words=0,independent_meaning_capacity=0,significance=False)
    put('RESULT.json',result)
    for name in ['ROWS.json','INDEPENDENT.json']:
        p=A/name;before=read(p);p.write_text(json.dumps(before,ensure_ascii=False,separators=(',',':'))+'\n');assert read(p)==before
    print(json.dumps(result))
if __name__=='__main__':main()
