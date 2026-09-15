"""Complete label/body census; exact conditional named-reference consistency."""
from collections import defaultdict
from pathlib import Path
import csv, hashlib, json, re
from count import solve

E=Path(__file__).resolve().parents[1]
R=E.parents[2]

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def tsv(p,rows):
    with p.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t');w.writeheader();w.writerows(rows)

def line_records(data,spec):
    raw=defaultdict(list)
    for r in data['raw']:raw[(r['edition'],r['locus'])].append(r)
    legacy={(r['edition'],r['locus']):r for r in data['legacy']}
    out={}
    for key,gs in raw.items():
        gs.sort(key=lambda r:int(r['source_group_index']))
        groups=[g['ivtff_group_raw'] for g in gs]
        clean=[bool(re.fullmatch('[a-z]+',g)) for g in groups]
        definite_seams=all(a['right_separator']==b['left_separator']=='.' for a,b in zip(gs,gs[1:]))
        count_ok=all(int(g['source_group_count'])==len(gs) for g in gs) and [int(g['source_group_index']) for g in gs]==list(range(1,len(gs)+1))
        lr=legacy.get(key);roots=lr['root_sequence'].split() if lr else []
        root_aligned=bool(lr) and lr['surface'].split()==groups and len(roots)==len(groups)
        for model in spec['models']:
            values=groups if model=='LITERAL' else roots if root_aligned else groups
            valid=[c and count_ok and definite_seams and (model=='LITERAL' or root_aligned) for c in clean]
            out[(key[0],key[1],model)]={'values':values,'valid':valid,
                'raw_groups':groups,'uncertain_seams':not definite_seams or (model!='LITERAL' and not root_aligned),'root_aligned':root_aligned,'count_ok':count_ok}
    return out

def compare(title,body):
    # Unknown title length/seams or body seams can alter windows: upper-only possibility.
    if not all(title['valid']):return 'UNKNOWN',[]
    n=len(title['values']);hits=[];possible=False
    for j in range(len(body['values'])-n+1):
        vals=body['values'][j:j+n];known=body['valid'][j:j+n]
        if vals==title['values'] and all(known):hits.append(j+1)
        if all(not k or a==b for a,b,k in zip(title['values'],vals,known)):possible=True
    if hits:return 'PRESENT',hits
    if possible or body['uncertain_seams'] or not body['count_ok']:return 'UNKNOWN',[]
    return 'ABSENT',[]

def main():
    lock=json.loads((E/'PREREG_LOCK.json').read_text())
    for p,h in lock['files'].items():assert sha(E/p)==h,p
    for p,h in lock['source_files'].items():assert sha(R/p)==h,p
    spec=json.loads((E/'src/SPEC.json').read_text());source=json.loads((E/'src/SOURCE.json').read_text())
    data=json.loads((E/'artifacts/INPUT.json').read_text());records=line_records(data,spec)
    edges=[(source['names'].index(a),source['names'].index(b)) for a,b in source['mandatory_edges']]
    evidence=[];result=[];graphs=[];candidates=[];rendered=[]
    for edition in spec['editions']:
        for model in spec['models']:
            titles=[];bodies=[]
            for sec in spec['sectors']:
                title=records[(edition,sec['title'],model)];titles.append(title)
                parts=[records[(edition,l,model)] for l in sec['body']]
                body={'values':sum((p['values'] for p in parts),[]),'valid':sum((p['valid'] for p in parts),[]),
                      'uncertain_seams':any(p['uncertain_seams'] for p in parts),
                      'count_ok':all(p['count_ok'] for p in parts)};bodies.append(body)
                rendered.append({'edition':edition,'model':model,'sector':sec['sector'],'clock':sec['clock'],
                  'title_locus':sec['title'],'title_raw':' '.join(title['raw_groups']),
                  'title_representation':' '.join(title['values']),'title_definite':all(title['valid']),
                  'body_loci':','.join(sec['body']),'body_representation':' '.join(body['values']),
                  'body_known_mask':''.join('1' if x else '0' for x in body['valid'])})
            statuses=[]
            for a,body in enumerate(bodies):
                row=[]
                for b,title in enumerate(titles):
                    status,hits=compare(title,body);row.append(status)
                    evidence.append({'edition':edition,'model':model,'body_sector':a+1,'title_sector':b+1,
                      'body_loci':','.join(spec['sectors'][a]['body']),
                      'title_locus':spec['sectors'][b]['title'],'title_raw':' '.join(title['raw_groups']),
                      'status':status,'window_positions_1based':','.join(map(str,hits))})
                statuses.append(row)
            bounds={}
            for bound in ['lower','upper']:
                adj=[[s=='PRESENT' if bound=='lower' else s!='ABSENT' for s in row] for row in statuses]
                answer=solve(12,edges,adj);bounds[bound]=answer
                graphs.append({'edition':edition,'model':model,'bound':bound,'adjacency':adj,**answer})
            verdict='CONTRADICTED' if bounds['upper']['count']==0 else 'COMPATIBLE' if bounds['lower']['count'] else 'UNRESOLVED_ONLY'
            result.append({'edition':edition,'model':model,'verdict':verdict,
                           'lower_count':bounds['lower']['count'],'upper_count':bounds['upper']['count'],
                           'present_offdiagonal':sum(s=='PRESENT' for a,row in enumerate(statuses) for b,s in enumerate(row) if a!=b),
                           'unknown_offdiagonal':sum(s=='UNKNOWN' for a,row in enumerate(statuses) for b,s in enumerate(row) if a!=b),
                           'definite_titles':sum(all(t['valid']) for t in titles)})
            for i,name in enumerate(source['names']):
                for j,sec in enumerate(spec['sectors']):
                    candidates.append({'edition':edition,'model':model,'name_hypothesis':name,'sector':j+1,
                        'title_locus':sec['title'],'title_raw':' '.join(titles[j]['raw_groups']),
                        'definite_assignments':bounds['lower']['marginals'][i][j],
                        'possible_assignments_upper':bounds['upper']['marginals'][i][j],
                        'meaning_confirmed':False})
    tsv(E/'artifacts/ALL_TITLE_BODY_CONSEQUENCES.tsv',evidence)
    tsv(E/'artifacts/ALL_NAME_CANDIDATES.tsv',candidates)
    tsv(E/'artifacts/COMPLETE_RECORDS.tsv',rendered)
    tsv(E/'artifacts/CANDIDATE_TABLE.tsv',result)
    dump(E/'artifacts/GRAPHS.json',{'source_edges':edges,'graphs':graphs})
    dump(E/'artifacts/RESULT.json',{'experiment':'GDT952','source_edges':len(edges),'assignment_space_per_case':479001600,
       'results':result,'total_title_body_cells':len(evidence),'independent_physical_leaves':0,
       'additional_confirmation_capacity':0,'significance_claim':False,'confirmed_word_count':0,
       'input_sha256':sha(E/'artifacts/INPUT.json'),'claim':'Conditional compatibility of a fixed source graph and invariant label rendering only; upper counts are conservative uncertainty bounds.'})
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
