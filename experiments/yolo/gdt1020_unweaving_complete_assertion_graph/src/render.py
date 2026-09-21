"""Post-result whole-position and graph disclosure; no changes to readings."""
from common import *
import csv,collections

def table(name,rows):
    with (A/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)

def main():
    spec,source=inputs();rows=read(A/'ROWS.json');words=[w for l in source['projected_lines'] for w in l['raw'].split()]
    loci=[(l['locus'],i+1) for l in source['projected_lines'] for i,w in enumerate(l['raw'].split())];full=[];summary=[]
    docs=['# Complete conditional assertion readings','All values are unconfirmed. P12projection only; two diplomatic forms remain unbound.','']
    for r in rows:
        for pno,p in enumerate(r['result']['parses']):
            if p['status']!='COMPLETE_CONDITIONAL_READING':continue
            g=p['graph'];phases={e['action']:e['phase'] for e in g['events'] if e['kind']=='HABIT'}
            summary.append(dict(candidate=r['candidate'],prediction=json.dumps(next(c['prediction'] for c in spec['candidates'] if c['id']==r['candidate']),sort_keys=True),status=r['result']['status'],complete_parses=len(r['result']['parses']),positions=33,observed_phases=json.dumps(phases,sort_keys=True),assertion_frames=len(g['events']),asserted_finish_states=sum('asserted_state' in e for e in g['events']),asserted_marriages=0,diplomatic_missing='salche\'dy;saii@208;',independent_meaning_capacity=0))
            docs += ['## '+r['candidate'],'','Habitual phase assignments: '+json.dumps(phases,sort_keys=True)+'.','', '|Clause|All written groups|Construction|Created assertion frames|Resolved references|','|---|---|---|---|---|']
            for c,t in zip(p['parse'],g['trace'],strict=True):
                docs.append('|'+t['clause']+'|`'+' '.join(words[c['start']:c['end']])+'`|'+c['kind']+'|'+','.join(t['new_events'])+'|'+','.join(t['references'])+'|')
                for i in range(c['start'],c['end']):full.append(dict(candidate=r['candidate'],parse=pno,position=i+1,locus=loci[i][0],group=loci[i][1],word=words[i],lexical_type=spec['lexicon'][words[i]][0],hypothetical_value=spec['lexicon'][words[i]][1],clause=t['clause'],construction=c['kind'],new_assertions=','.join(t['new_events']),references=','.join(t['references']),confirmed=False))
            docs += ['', 'Computed complete assertion graph:','', '```json',json.dumps(g,ensure_ascii=False,indent=2),'```','']
    table('CANDIDATES.tsv',summary);table('ALL_POSITIONS.tsv',full)
    (A/'READINGS.md').write_text('\n'.join(docs).rstrip()+'\n')
    result=dict(status='SUPPORTED_LIMITED_TWO_PROJECTED_UNWEAVING_READINGS',candidates=2,complete_grammatical_parses=1,complete_candidate_graphs=len(summary),candidate_statuses={r['candidate']:r['result']['status'] for r in rows},target_groups=33,lexical_guesses=24,new_parent_guesses=17,new_parent_singletons=16,independent_source_forms_unresolved=read(A/'DIPLOMATIC_SCOPE.json')['unknown'],diplomatic_scope='SOURCE_FORMS_UNBOUND',confirmed_words=0,independent_meaning_capacity=0,significance=False)
    put('RESULT.json',result);print(json.dumps(result))
if __name__=='__main__':main()
