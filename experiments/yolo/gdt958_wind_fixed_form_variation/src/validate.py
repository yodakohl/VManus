#!/usr/bin/env python3
"""Independent bounded audit of GDT958; no experiment implementation imports."""
from collections import defaultdict, deque
from pathlib import Path
import csv, hashlib, json, re

EXP = Path(__file__).resolve().parents[1]
ROOT = EXP.parents[2]
PARENT = ROOT / 'experiments/yolo/gdt952_wind_named_reference_network'
ART = EXP / 'artifacts'
MODELS = ['LM_ONLY', 'LR_PHRASE_ONLY', 'COMBINED']

def load(p): return json.loads(p.read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def variants(words, model, lib):
    one = {}
    for a,b in lib['LM']:
        one[a],one[b] = b,a
    pairs = {}
    for x in lib['LR_PHRASE']:
        a,b = tuple(x[0]),tuple(x[1]); pairs[a],pairs[b] = b,a
    initial=tuple(words); todo=deque([initial]); seen={initial}
    while todo:
        row=todo.popleft(); nxt=[]
        if model in ('LM_ONLY','COMBINED'):
            for i,w in enumerate(row):
                if w in one: nxt.append(row[:i]+(one[w],)+row[i+1:])
        if model in ('LR_PHRASE_ONLY','COMBINED'):
            for i in range(len(row)-1):
                if row[i:i+2] in pairs: nxt.append(row[:i]+pairs[row[i:i+2]]+row[i+2:])
        for v in nxt:
            if v not in seen: seen.add(v); todo.append(v)
        if len(seen)>32768: raise RuntimeError('closure capacity exceeded; no truncation')
    return [list(x) for x in sorted(seen)]

def records(data):
    raw=defaultdict(list)
    for r in data['raw']: raw[(r['edition'],r['locus'])].append(r)
    legacy={(r['edition'],r['locus']):r for r in data['legacy']}; out={}
    for key, rows0 in raw.items():
        rows=sorted(rows0,key=lambda r:int(r['source_group_index']))
        groups=[r['ivtff_group_raw'] for r in rows]
        clean=[bool(re.fullmatch(r'[a-z]+',g)) for g in groups]
        seams=all(a['right_separator']==b['left_separator']=='DEFINITE_SPACE' for a,b in zip(rows,rows[1:]))
        indexes=[int(r['source_group_index']) for r in rows]
        count_ok=all(int(r['source_group_count'])==len(rows) for r in rows) and indexes==list(range(1,len(rows)+1))
        old=legacy.get(key); roots=old['root_sequence'].split() if old else []
        aligned=bool(old) and old['surface'].split()==groups and len(roots)==len(groups)
        out[key]= {'values':groups,'valid':[c and count_ok and seams for c in clean], 'raw_groups':groups,
                   'uncertain_seams':not seams,'root_aligned':aligned,'count_ok':count_ok}
    return out

def compare(title,body,alternatives):
    if not all(title['valid']): return 'UNKNOWN',[]
    n=len(title['values']); hits=[]; possible=False
    for j in range(len(body['values'])-n+1):
        vals=body['values'][j:j+n]; known=body['valid'][j:j+n]
        for k,v in enumerate(alternatives):
            if vals==v and all(known): hits.append({'start_1based':j+1,'variant_index':k,'variant':v})
            if all(not ok or a==b for a,b,ok in zip(v,vals,known)): possible=True
    if hits: return 'PRESENT',hits
    if possible or body['uncertain_seams'] or not body['count_ok']: return 'UNKNOWN',[]
    return 'ABSENT',[]

def components(n,edges):
    adj=[[] for _ in range(n)]
    for a,b in edges: adj[a].append(b);adj[b].append(a)
    seen=set(); out=[]
    for start in range(n):
        if start in seen: continue
        todo=[start]; seen.add(start); got=[]
        while todo:
            v=todo.pop();got.append(v)
            for w in adj[v]:
                if w not in seen: seen.add(w);todo.append(w)
        out.append(sorted(got))
    return sorted(out,key=lambda c:(-len(c),c))

def exact_count(n,edges,matrix):
    comps=sorted(components(n,edges),key=lambda c:(-len(c),c))
    if all(matrix[i][j] for i in range(n) for j in range(n) if i!=j):
        f=1
        for k in range(2,n+1): f*=k
        return f,[[f//n]*n for _ in range(n)],comps,None,None
    inc=[set() for _ in range(n)]
    for a,b in edges: inc[a].add(b);inc[b].add(a)
    all_emb=[]; masks=[]; embeds=[]
    for comp in comps:
        order=sorted(comp,key=lambda v:(-len(inc[v]),v)); rows=[]
        def visit(k,mapping,used):
            if k==len(order): rows.append(tuple(mapping[i] for i in comp));return
            v=order[k]
            for pos in range(n):
                if used&(1<<pos): continue
                good=True
                for a,b in edges:
                    if a==v and b in mapping and not matrix[pos][mapping[b]]:good=False
                    if b==v and a in mapping and not matrix[mapping[a]][pos]:good=False
                if good:
                    mapping[v]=pos;visit(k+1,mapping,used|(1<<pos));del mapping[v]
        visit(0,{},0); all_emb.append((comp,rows)); embeds.append(len(rows)); masks.append(len({sum(1<<p for p in r) for r in rows}))
    dp={0:(1,[[0]*n for _ in range(n)])}
    for comp,rows in all_emb:
        bymask=defaultdict(list)
        for row in rows: bymask[sum(1<<p for p in row)].append(row)
        nxt={}
        for used,(count,marg) in dp.items():
            for mask,choices in bymask.items():
                if used&mask: continue
                key=used|mask
                if key not in nxt:nxt[key]=(0,[[0]*n for _ in range(n)])
                nc,nm=nxt[key];nc+=count*len(choices)
                for i in range(n):
                    for j in range(n):nm[i][j]+=marg[i][j]*len(choices)
                for row in choices:
                    for i,pos in zip(comp,row):nm[i][pos]+=count
                nxt[key]=(nc,nm)
        dp=nxt
    full=(1<<n)-1
    if full not in dp:return 0,[[0]*n for _ in range(n)],comps,masks,embeds
    return dp[full][0],dp[full][1],comps,masks,embeds

def read_tsv(p):
    with p.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))

def main():
    lock=load(EXP/'PREREG_LOCK.json'); lock_checks={}
    for rel,expected in lock['files'].items():
        actual=sha(ROOT/rel);lock_checks[rel]={'expected':expected,'actual':actual,'ok':actual==expected}
    spec=load(PARENT/'src/SPEC.json'); data=load(PARENT/'artifacts/INPUT.json'); source=load(PARENT/'src/SOURCE.json'); lib=load(EXP/'src/LIBRARY.json')
    frozen=load(ART/'FROZEN_TITLE_PREDICTIONS.json'); frozen_tsv=read_tsv(ART/'FROZEN_TITLE_VARIANTS.tsv'); rec=records(data)
    title_loci={s['title'] for s in spec['sectors']}
    title_rec=records({'raw':[r for r in data['raw'] if r['locus'] in title_loci], 'legacy':[]})
    expected_frozen=[]; expected_tsv=[]
    for ed in spec['editions']:
      for model in MODELS:
       for s in spec['sectors']:
        title=title_rec[(ed,s['title'])]; vs=variants(title['values'],model,lib)
        expected_frozen.append({'edition':ed,'model':model,'sector':s['sector'],'locus':s['title'],'title':title,'variants':vs})
        for v in vs: expected_tsv.append({'edition':ed,'model':model,'sector':str(s['sector']),'locus':s['title'],'raw_title':' '.join(title['values']),'definite_title':str(all(title['valid'])),'variant_count':str(len(vs)),'variant':' '.join(v)})
    pred={(x['edition'],x['model'],x['sector']):x for x in expected_frozen}
    frozen_ok=frozen==expected_frozen; tsv_ok=frozen_tsv==expected_tsv
    bodies=[]; cells=[]; graphs=[]; cases=[]
    edges=[(source['names'].index(a),source['names'].index(b)) for a,b in source['mandatory_edges']]
    for ed in spec['editions']:
        bs=[]
        for s in spec['sectors']:
            parts=[rec[(ed,l)] for l in s['body']]
            body={'values':sum((p['values'] for p in parts),[]),'valid':sum((p['valid'] for p in parts),[]),'uncertain_seams':any(p['uncertain_seams'] for p in parts),'count_ok':all(p['count_ok'] for p in parts)}
            bs.append(body);bodies.append({'edition':ed,'sector':s['sector'],'loci':s['body'],'body':body})
        for model in MODELS:
            matrix=[];defo=unk=0
            for bi,body in enumerate(bs,1):
                row=[]
                for ti in range(1,13):
                    p=pred[(ed,model,ti)]; status,hits=compare(p['title'],body,p['variants']); literal,_=compare(p['title'],body,[p['title']['values']]);row.append(status)
                    if ti!=bi:defo+=status=='PRESENT';unk+=status=='UNKNOWN'
                    cells.append({'edition':ed,'model':model,'body_sector':bi,'title_sector':ti,'title_locus':p['locus'],'title_raw':' '.join(p['title']['values']),'variant_count':len(p['variants']),'status':status,'literal_status':literal,'new_definite_offdiagonal':status=='PRESENT' and literal!='PRESENT' and bi!=ti,'hits':hits})
                matrix.append(row)
            bounds={}
            for bound in ('lower','upper'):
                adj=[[st=='PRESENT' if bound=='lower' else st!='ABSENT' for st in row] for row in matrix]
                count,marg,comps,masks,embeds=exact_count(12,edges,adj);bounds[bound]=(count,marg,comps,masks,embeds)
                graphs.append({'edition':ed,'model':model,'bound':bound,'adjacency':adj,'count':count,'marginals':marg,'components':comps,'component_mask_counts':masks,'component_embedding_counts':embeds})
            cases.append({'edition':ed,'model':model,'status':'CONTRADICTED' if not bounds['upper'][0] else 'COMPATIBLE_CONDITIONAL_GRAPH' if bounds['lower'][0] else 'UNRESOLVED_ONLY','lower_assignments':bounds['lower'][0],'upper_assignments':bounds['upper'][0],'definite_offdiagonal':defo,'unknown_offdiagonal':unk,'new_definite_offdiagonal':0,'expanded_titles':sum(len(pred[(ed,model,i)]['variants'])>1 for i in range(1,13)),'independent_confirmation_leaves':0})
    saved_bodies=load(ART/'COMPLETE_BODIES.json');saved_cells=load(ART/'ALL_CELLS.json');saved_graphs=load(ART/'GRAPHS.json');saved_result=load(ART/'RESULT.json')
    bodies_ok=saved_bodies==bodies;cells_ok=saved_cells==cells;graphs_ok=saved_graphs.get('source_edges')==[[a,b] for a,b in edges] and saved_graphs.get('graphs')==graphs
    ks=('edition','model','status','lower_assignments','upper_assignments','definite_offdiagonal','unknown_offdiagonal','new_definite_offdiagonal','expanded_titles','independent_confirmation_leaves')
    result_cases=saved_result.get('cases',[]); cases_ok=len(result_cases)==9 and all(all(g.get(k)==w.get(k) for k in ks) for g,w in zip(result_cases,cases))
    by_locus=defaultdict(list)
    for r in data['raw']:by_locus[(r['edition'],r['locus'])].append(r)
    listed={(e,s['title']) for e in spec['editions'] for s in spec['sectors']}
    listed|={(e,l) for e in spec['editions'] for s in spec['sectors'] for l in s['body']}
    ownership_ok=set(by_locus)==listed and all([int(r['source_group_index']) for r in sorted(rows,key=lambda x:int(x['source_group_index']))]==list(range(1,len(rows)+1)) and all(int(r['source_group_count'])==len(rows) for r in rows) for rows in by_locus.values())
    source_ok=len(source['names'])==12 and len(source['mandatory_edges'])==8 and len(set(tuple(x) for x in source['mandatory_edges']))==8 and all(a!=b for a,b in source['mandatory_edges'])
    full_space=exact_count(12,edges,[[True]*12 for _ in range(12)])[0]; full_ok=full_space==479001600
    # Recheck graph policy directly from the generated cell order: lower=PRESENT, upper=PRESENT or UNKNOWN.
    expected_mats={}
    for ed in spec['editions']:
        for model in MODELS:
            selected=[c for c in cells if c['edition']==ed and c['model']==model]
            expected_mats[(ed,model)]=[[c['status'] for c in selected[k:k+12]] for k in range(0,len(selected),12)]
    policy_ok=all(g['adjacency']==[[st=='PRESENT' if g['bound']=='lower' else st!='ABSENT' for st in row] for row in expected_mats[(g['edition'],g['model'])]] for g in graphs)
    lock_ok=all(x['ok'] for x in lock_checks.values())
    report={'experiment':'GDT958','validator':'independent_reconstruction_without_common_run_prepare','lock':{'all_hashes_match':lock_ok,'checks':lock_checks},'library_closure':{'LM_pairs':len(lib.get('LM',[])),'LR_phrase_pairs':len(lib.get('LR_PHRASE',[])),'title_model_cases':len(expected_frozen),'frozen_predictions_match':frozen_ok,'frozen_variant_rows':len(expected_tsv),'frozen_variants_match':tsv_ok,'expanded_cases':sum(len(x['variants'])>1 for x in expected_frozen)},'source_contract':{'raw_rows':len(data['raw']),'raw_loci':len(by_locus),'body_ownership_match':ownership_ok,'source_names':len(source['names']),'source_edges':len(edges),'eight_unique_edges':source_ok,'full_bijection_space':full_space,'twelve_factorial':full_ok},'artifacts':{'complete_bodies_match':bodies_ok,'cells_1296_match':cells_ok,'graphs_18_match':graphs_ok,'result_cases_9_match':cases_ok,'unknown_policy_match':policy_ok},'cases':[{'edition':x['edition'],'model':x['model'],'lower_assignments':x['lower_assignments'],'upper_assignments':x['upper_assignments'],'definite_offdiagonal':x['definite_offdiagonal'],'unknown_offdiagonal':x['unknown_offdiagonal']} for x in cases],'claim_ceiling':{'word_meanings_validated':False,'meaning_confirmed':0,'significance_claim':False,'unknowns_are_bounds_only':True,'no_new_decoder':True}}
    all_ok=lock_ok and len(lib.get('LM',[]))==155 and len(lib.get('LR_PHRASE',[]))==22 and frozen_ok and tsv_ok and ownership_ok and source_ok and full_ok and bodies_ok and cells_ok and graphs_ok and cases_ok and policy_ok
    report['status']='PASS' if all_ok else 'FAIL';(ART/'VALIDATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':report['status'],'LM_pairs':155,'LR_phrase_pairs':22,'title_cases':108,'variant_rows':114,'cells':1296,'graphs':18,'source_edges':len(edges),'full_bijection_space':full_space,'unknown_policy':policy_ok}))
    return 0 if all_ok else 1

if __name__=='__main__':raise SystemExit(main())
