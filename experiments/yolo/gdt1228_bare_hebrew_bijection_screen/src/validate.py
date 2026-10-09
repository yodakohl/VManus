#!/usr/bin/env python3
"""Separate regex extraction, moment variance and joint-minus-marginal entropy."""
from pathlib import Path
from collections import Counter
from datetime import datetime,timezone
import csv,hashlib,html,io,json,math,random,re,subprocess
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
s=json.loads((D/'src/SPEC.json').read_text());r=json.loads((A/'RESULT.json').read_text())
for p,h in json.loads((A/'REGISTRATION_LOCK.json').read_text())['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
# Explicit pointed-Hebrew mark range, independently from Unicode-category removal.
point=re.compile('[\u0591-\u05bd\u05bf\u05c1\u05c2\u05c4\u05c5\u05c7]')
finals={'ך':'כ','ם':'מ','ן':'נ','ף':'פ','ץ':'צ'};sections=[]
for c,path in enumerate(s['hebrew_files'],1):
    o=json.loads((ROOT/path).read_text());assert o['sections']==[str(c)] and not o['warnings']
    v=o['versions'];assert len(v)==1 and v[0]['versionTitle']=='Torat Emet 363'
    for j,raw in enumerate(v[0]['text'],1):
        text=html.unescape(re.sub(r'</?small(?:\s[^>]*)?>','',raw));assert '<' not in text and '>' not in text
        text=point.sub('',text).replace('"','').replace("'",'')
        tokens=[''.join(finals.get(x,x) for x in w) for w in re.findall('[א-ת]+',text)]
        assert tokens;sections.append({'ref':f'{c}:{j}','words':tokens})
words=[w for x in sections for w in x['words']];n=len(words)
assert len(sections)==71 and n>=500 and n==r['source_tokens']
assert json.loads((A/'SOURCE_PROJECTION.json').read_text())['source_sections']==sections

def entropy(c):
    total=sum(c.values())
    return math.log2(total)-sum(v*math.log2(v) for v in c.values())/total

def statistics(seq):
    word_counts=Counter(map(tuple,seq));size=sum(word_counts.values())
    sums=sum(len(w)*c for w,c in word_counts.items());squares=sum(len(w)**2*c for w,c in word_counts.items())
    p=Counter()
    for word,c in word_counts.items():
        for i in range(len(word)-1):p[(word[i],word[i+1])]+=c
    previous=Counter()
    for (a,b),c in p.items():previous[a]+=c
    mean=sums/size
    return {'mean_length':mean,'sd_length':math.sqrt(max(0,squares/size-mean*mean)),'conditional_entropy':entropy(p)-entropy(previous)}

def assert_values(a,b):
    assert a.keys()==b.keys()
    for k in a:assert abs(a[k]-b[k])<1e-10,(k,a[k],b[k])
assert_values(statistics(['aba','aca']),{'mean_length':3.,'sd_length':0.,'conditional_entropy':.5})
candidates={'logical':statistics(words),'reversed':statistics([w[::-1] for w in words])}
for o in candidates:assert_values(candidates[o],r['candidate_metrics'][o])
allowed=json.loads((ROOT/s['scope_spec']).read_text())['allowed']
assert len(allowed)==len(set(allowed))==179 and all(not p.startswith('f84') and p!='f116v' for p in allowed)

def query(path,cols,receipt):
    cmd=['./vmanus-exp','query-tsv',path,'--selector','page']
    for p in allowed:cmd+=['--allow',p]
    cmd+=['--columns',cols]
    call=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True,check=True)
    assert hashlib.sha256(call.stdout.encode()).hexdigest()==receipt['output_sha256']
    return list(csv.DictReader(io.StringIO(call.stdout),delimiter='\t'))
receipts=json.loads((A/'RUN_RECEIPT.json').read_text())['guarded_projections']
rows=query(s['native_source'],'edition,page,locus,kind,source_group_index,ivtff_group_raw,left_separator,right_separator',receipts[0])
metadata=query(s['metadata_source'],'edition,page,locus,source_group_index,currier,section,hand',receipts[1])
def key(x):return x['edition'],x['locus'],int(x['source_group_index'])
meta={key(x):x for x in metadata};assert len(meta)==len(metadata)
prose=[x for x in rows if x['kind']=='P'];assert len({key(x) for x in prose})==len(prose)
page_universe=sorted({x['page'] for x in prose});assert len(page_universe)==179
rx=re.compile(r'c[ktpf]h|ch|sh|[aoeindqysrlmktpf]')
groups={ed:[] for ed in ('IT2a','RF1b','ZL3b')};fields={f:set() for f in ('currier','section','hand')}
for row in prose:
    md=meta[key(row)];assert md['page']==row['page']
    for f in fields:fields[f].add(md[f])
    units=rx.findall(row['ivtff_group_raw'])
    if not units or ''.join(units)!=row['ivtff_group_raw']:continue
    if row['left_separator'] not in {'DEFINITE_SPACE','LINE_START'} or row['right_separator'] not in {'DEFINITE_SPACE','LINE_END'}:continue
    ident='{}|{}|G{:03d}'.format(row['edition'],row['locus'],int(row['source_group_index']))
    groups[row['edition']].append((row,md,tuple(units),ident))
assert {ed:len(v) for ed,v in groups.items()}==r['eligible_groups']
expected={(ed,'pooled','ALL') for ed in groups}|{(ed,f,v) for ed in groups for f in fields for v in fields[f]}
cells={(c['reader'],c['field'],c['value']):c for c in r['cells']};assert len(cells)==len(r['cells']) and set(cells)==expected
joint={key:{o:0 for o in candidates} for key in cells};metric_values={key:{k:[] for k in s['metrics']} for key in cells}
for ident,cell in cells.items():
    ed,f,v=ident;capacity=sum(f=='pooled' or x[1][f]==v for x in groups[ed])
    assert capacity==cell['eligible_groups']
    assert cell['capacity']==('SCOREABLE' if capacity>=n else 'NO_CAPACITY')
    assert len(cell['samples'])==(128 if capacity>=n else 0)
for seed in range(128):
    pages=page_universe.copy();random.Random(seed).shuffle(pages);rank={p:i for i,p in enumerate(pages)}
    ordered={ed:sorted(items,key=lambda x:(rank[x[0]['page']],x[0]['locus'],int(x[0]['source_group_index']))) for ed,items in groups.items()}
    for ident,cell in cells.items():
        if cell['capacity']!='SCOREABLE':continue
        ed,f,v=ident;selected=[x for x in ordered[ed] if f=='pooled' or x[1][f]==v][:n]
        actual=cell['samples'][seed];assert actual['seed']==seed and len(selected)==n
        ids=[x[3] for x in selected]
        assert hashlib.sha256(json.dumps(ids,separators=(',',':')).encode()).hexdigest()==actual['sample_ids_sha256']
        assert ids[-1]==actual['last_id']
        values=statistics(x[2] for x in selected);assert_values(values,actual['metrics'])
        for k in values:metric_values[ident][k].append(values[k])
        for o,model in candidates.items():
            ok={k:abs(model[k]-values[k])<=(tol*values[k] if kind=='relative' else tol) for k,(kind,tol) in s['metrics'].items()}
            assert actual['comparisons'][o]=={'within':ok,'joint':all(ok.values())}
            joint[ident][o]+=int(all(ok.values()))
for ident,cell in cells.items():
    if cell['capacity']=='SCOREABLE':
        assert cell['joint_passes']==joint[ident]
        for k,v in metric_values[ident].items():
            assert abs(min(v)-cell['ranges'][k][0])<1e-10 and abs(max(v)-cell['ranges'][k][1])<1e-10
for ed in groups:
    keys=[key for key,cell in cells.items() if key[0]==ed and cell['capacity']=='SCOREABLE']
    passes={o:sum(joint[k][o] for k in keys) for o in candidates}
    decision='DIRECT_BIJECTION_SCREEN_EXCLUDED' if keys and not any(passes.values()) else 'COARSE_SCREEN_SURVIVES' if keys else 'NO_CAPACITY'
    assert r['decisions'][ed]=={'scoreable_cells':len(keys),'joint_matches':passes,'decision':decision}
status='DIRECT_BIJECTION_SCREEN_EXCLUDED_ALL_READINGS' if all(x['decision']=='DIRECT_BIJECTION_SCREEN_EXCLUDED' for x in r['decisions'].values()) else 'DIRECT_BIJECTION_SCREEN_MIXED_OR_SURVIVES'
assert r['status']==status
v={'experiment':'GDT1228','status':'PASS','validated_utc':datetime.now(timezone.utc).isoformat(),'source_tokens':n,'source_sections':71,'scoreable_cells':sum(c['capacity']=='SCOREABLE' for c in cells.values()),'samples_rebuilt':sum(len(c['samples']) for c in cells.values()),'checks':['frozen inputs and code','independent literal source projection','independent regex native units and metadata joins','all ordered sample ID hashes','moment variance and joint-minus-marginal entropy','all tolerances, capacities and decisions'],'claim':'Same-author independent computation; no semantic confirmation.'}
(A/'VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v,indent=2))
