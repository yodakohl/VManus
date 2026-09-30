import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE=Path(__file__).resolve().parents[1]

def main():
    model=json.loads((HERE/'src/MODEL.json').read_text())
    source=HERE/'src/SOURCE.tsv'
    assert hashlib.sha256(source.read_bytes()).hexdigest()==model['source_sha256']
    rows=list(csv.DictReader(source.open(),delimiter='\t'))
    for row in rows:
        row['source_group_index']=int(row['source_group_index'])
        row['source_group_count']=int(row['source_group_count'])
    loci=defaultdict(list)
    for r in rows: loci[(r['edition'],r['locus'])].append(r)
    candidates=[]
    events=[]
    for r in rows:
        form=r['ivtff_group_raw']
        if form not in model['forms']: continue
        line=loci[(r['edition'],r['locus'])]
        neighbours=[x for x in line if abs(x['source_group_index']-r['source_group_index'])==1]
        partners=[x['source_group_id'] for x in neighbours if x['kind']=='P' and r['kind']=='P' and x['ivtff_group_raw']==('okeey' if form=='qokeey' else 'qokeey')]
        event={'id':r['source_group_id'],'edition':r['edition'],'locus':r['locus'],'kind':r['kind'],'index':r['source_group_index'],'form':form,'partner_candidates':partners}
        events.append(event)
        for key,mapping in model['candidates'].items():
            spec=mapping[form]
            candidates.append({'candidate':key,**event,'gloss':spec['gloss'],'role':spec['role'],
                'candidate_argument':','.join(partners) or 'UNBOUND',
                'unbound_obligations':('drinker' if key=='D' else 'referent_identity') if partners and form=='qokeey' else ','.join(spec['obligations']),
                'observed_meaning':'UNIDENTIFIED','contradiction':'NOT_EVALUABLE_FROM_UNKNOWN_NEIGHBOURS'})
    out=HERE/'artifacts'
    (out/'EVENTS.json').write_text(json.dumps(events,indent=2)+'\n')
    fields=list(candidates[0])
    with (out/'CANDIDATE_TABLE.tsv').open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=fields,delimiter='\t',lineterminator='\n')
        writer.writeheader(); writer.writerows(candidates)
    reader=['# Complete scoped raw reader and conditional candidates','',
        'All raw groups retained. `|` below marks group boundaries, not punctuation; exact separator values are in src/SOURCE.tsv.',
        'D/F annotations are stipulated alternatives, not observed meanings. All other groups are UNKNOWN. Labels are separate from prose.','']
    for (ed,loc),line in loci.items():
        reader.append(f"- {ed} {loc} {line[0]['kind']}: "+' | '.join(r['ivtff_group_raw'] for r in line))
        for key,mapping in model['candidates'].items():
            rendered=[mapping[r['ivtff_group_raw']]['gloss'] if r['ivtff_group_raw'] in mapping else 'UNKNOWN' for r in line]
            reader.append(f"  - {key}: "+' | '.join(rendered))
    (out/'FULL_READER.md').write_text('\n'.join(reader)+'\n')
    counts={ed:dict(Counter(r['ivtff_group_raw'] for r in rows if r['edition']==ed and r['kind']=='P' and r['ivtff_group_raw'] in model['forms'])) for ed in ('ZL3b','IT2a','RF1b')}
    pair_loci={ed:sorted({e['locus'] for e in events if e['edition']==ed and e['form']=='qokeey' and e['partner_candidates']}) for ed in counts}
    native=json.loads((HERE/'src/NATIVE_OBSERVATION.json').read_text())
    result={'decision':'NO_LABEL_OWNER_OR_WRITTEN_MEANING_DISCRIMINATOR','phase':model['phase'],
        'source_groups':len(rows),'target_events':len(events),'candidate_rows':len(candidates),
        'P_target_counts':counts,'direct_pair_loci':pair_loci,
        'native_ownership':native['ownership'],'label_forms':['okeey','lol'],
        'unresolved':['D drink/draught and F flows/fluid','state/quality alternative not excluded','roles of lol, kain and lchedy','repetition, clause boundaries and referent identity'],
        'independent_meaning_capacity':0,'confirmed_words':0,
        'scored_relation_packet':False,'significance_claim':False,
        'source_sha256':model['source_sha256']}
    (out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__': main()
