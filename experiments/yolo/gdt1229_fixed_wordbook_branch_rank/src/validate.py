#!/usr/bin/env python3
"""Separate raw-source projection, prefix-bucket inverse and native statistics."""
from pathlib import Path
from collections import Counter
from datetime import datetime,timezone
from functools import lru_cache
import csv,hashlib,html,io,json,math,random,re,subprocess
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
s=json.loads((D/'src/SPEC.json').read_text());r=json.loads((A/'RESULT.json').read_text());out=json.loads((A/'SOURCE_WRITING.json').read_text())
for p,h in json.loads((A/'REGISTRATION_LOCK.json').read_text())['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
oldspec=json.loads((ROOT/s['source_spec']).read_text());point=re.compile('[\u0591-\u05bd\u05bf\u05c1\u05c2\u05c4\u05c5\u05c7]');finals={'ך':'כ','ם':'מ','ן':'נ','ף':'פ','ץ':'צ'};sections=[]
for c,path in enumerate(oldspec['hebrew_files'],1):
    obj=json.loads((ROOT/path).read_text());assert obj['sections']==[str(c)] and not obj['warnings'];vs=obj['versions'];assert len(vs)==1 and vs[0]['versionTitle']=='Torat Emet 363'
    for j,raw in enumerate(vs[0]['text'],1):
        text=html.unescape(re.sub(r'</?small(?:\s[^>]*)?>','',raw));assert '<' not in text and '>' not in text
        text=point.sub('',text).replace('"','').replace("'",'');words=[''.join(finals.get(x,x) for x in w) for w in re.findall('[א-ת]+',text)];assert words
        sections.append({'ref':f'{c}:{j}','words':words})
source=[w for x in sections for w in x['words']];assert len(source)==6288 and len(sections)==71
assert sections==json.loads((ROOT/s['source_projection']).read_text())['source_sections']
# Unicode order of these base letters is the declared order; no final forms remain.
assert ''.join(sorted(s['source_alphabet']))==s['source_alphabet']
lex=sorted(set(source));assert lex==out['complete_public_wordbook'];signs=s['working_signs']
@lru_cache(None)
def choices(prefix):return sorted({w[len(prefix)] for w in lex if w.startswith(prefix) and len(w)>len(prefix)})
def source_ranks(word):return [choices(word[:i]).index(c)+1 for i,c in enumerate(word)]
def draw(rank):return ('cph',)*((rank-1)//20)+(signs[(rank-1)%20],)
rx=re.compile(r'c[ktpf]h|ch|sh|[aoeindqysrlmktpf]')
def parse(raw):
    result=tuple(rx.findall(raw));assert result and ''.join(result)==raw;return result
def integers(gs):
    ranks=[];value=0
    for g in gs:
        if g=='cph':value+=20
        else:assert g in signs[:20];ranks.append(value+signs.index(g)+1);value=0
    assert value==0;return ranks
def decode(gs):
    if gs[0]=='cfh':
        ranks=integers(gs[1:]);assert ranks and all(1<=i<=len(s['source_alphabet']) for i in ranks)
        word=''.join(s['source_alphabet'][i-1] for i in ranks);assert word not in lex;return word
    word=''
    for i in integers(gs):
        ch=choices(word);assert 1<=i<=len(ch);word+=ch[i-1]
    assert word in lex;return word
codes={w:sum((draw(i) for i in source_ranks(w)),()) for w in lex}
assert len(set(codes.values()))==len(lex)
for row in out['all_word_codes']:
    w=row['source'];assert row['ranks']==source_ranks(w) and tuple(row['drawings'])==codes[w] and row['output']==''.join(codes[w])
    assert row['source_occurrences']==source.count(w)
assert len(out['all_word_codes'])==len(lex)
# Independent inverse consumes only the serialized output, row structure and wordbook.
paragraphs=(A/'ENCODED.txt').read_text().rstrip('\n').split('\n\n');assert len(paragraphs)==71
physical=[];decoded=[];row_cells=[];continuations=0;blankcells=0
for paragraph,original in zip(paragraphs,sections):
    carry=();recovered=[]
    for line in paragraph.splitlines():
        groups=[parse(x) for x in line.split(' ')];cells=sum(map(len,groups))+len(groups)-1;assert cells<=24
        row_cells.append(cells);blankcells+=len(groups)-1
        for i,g in enumerate(groups):
            physical.append(g)
            if carry:assert i==0;g=carry+g;carry=()
            if g[-1]=='cfh':assert i==len(groups)-1;carry=g[:-1];assert carry;continuations+=1
            else:recovered.append(decode(g))
    assert not carry and recovered==original['words'];decoded.extend(recovered)
assert decoded==source;n=len(physical)
# Independently reconstruct canonical layout by legal integer cut offsets.
def layout(words):
    lines=[];row=[];used=0
    for w in words:
        units=[draw(x) for x in source_ranks(w)];g=list(codes[w])
        if len(g)>24:
            if row:lines.append(row);row=[];used=0
            while len(g)>24:
                ends=[];cursor=0
                for u in units:cursor+=len(u);ends.append(cursor)
                cut=max(x for x in ends if x<=23);count=ends.index(cut)+1
                lines.append([tuple(g[:cut]+['cfh'])]);g=g[cut:];units=units[count:]
            row=[tuple(g)];used=len(g)
        else:
            if row and used+len(g)+1>24:lines.append(row);row=[];used=0
            used+=len(g)+(1 if row else 0);row.append(tuple(g))
    if row:lines.append(row)
    return '\n'.join(' '.join(''.join(w) for w in row) for row in lines)
assert paragraphs==[layout(x['words']) for x in sections]
assert out['source_tokens']==len(source) and out['source_sections']==71 and out['wordbook_entries']==len(lex)
assert out['prefix_nodes_including_terminal_leaves']==len({w[:i] for w in lex for i in range(len(w)+1)})
assert out['lookup_nodes_with_children']==len({w[:i] for w in lex for i in range(len(w))})
assert out['maximum_source_length']==max(map(len,source)) and out['maximum_logical_drawing_length']==max(map(len,codes.values()))
assert out['physical_groups']==n==r['physical_groups'] and out['physical_rows']==len(row_cells) and out['physical_continuations']==continuations
assert out['physical_drawings']==sum(map(len,physical)) and out['physical_intergroup_blanks']==blankcells
assert out['glyph_counts']==dict(Counter(g for w in physical for g in w)) and out['word_final_counts']==dict(Counter(w[-1] for w in physical))
assert out['forced_unary_edge_tokens']==sum(len(choices(w[:i]))==1 for w in source for i in range(len(w)))
assert sorted(Counter(codes[w] for w in source).values())==sorted(Counter(source).values()) and out['logical_frequency_invariance'] is True
assert [row['source'] for row in out['first10_source_tokens']]==source[:10]
assert [row['source'] for row in out['ten_longest_types']]==sorted(lex,key=lambda w:(-len(w),w))[:10]
def entropy(c):
    total=sum(c.values());return math.log2(total)-sum(v*math.log2(v) for v in c.values())/total
def statistics(seq):
    wc=Counter(map(tuple,seq));size=sum(wc.values());letters=Counter();pairs=Counter()
    for word,c in wc.items():
        for g in word:letters[g]+=c
        for i in range(len(word)-1):pairs[word[i],word[i+1]]+=c
    prev=Counter()
    for (a,b),c in pairs.items():prev[a]+=c
    mean=sum(len(w)*c for w,c in wc.items())/size;second=sum(len(w)**2*c for w,c in wc.items())/size
    return {'mean_length':mean,'sd_length':math.sqrt(max(0,second-mean*mean)),'top10_share':sum(sorted(wc.values(),reverse=True)[:10])/size,'type_ratio':len(wc)/size,'glyph_entropy':entropy(letters),'conditional_entropy':entropy(pairs)-entropy(prev)}
def close(a,b):
    assert a.keys()==b.keys()
    for k in a:assert abs(a[k]-b[k])<1e-10,(k,a[k],b[k])
assert abs(statistics(['aba','aca'])['conditional_entropy']-.5)<1e-12
candidate=statistics(physical);close(candidate,r['candidate_metrics'])
allowed=json.loads((ROOT/s['scope_spec']).read_text())['allowed'];assert len(allowed)==len(set(allowed))==179 and all(not p.startswith('f84') and p!='f116v' for p in allowed)
def query(path,cols,receipt):
    cmd=['./vmanus-exp','query-tsv',path,'--selector','page']
    for p in allowed:cmd+=['--allow',p]
    cmd+=['--columns',cols];call=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True,check=True)
    assert hashlib.sha256(call.stdout.encode()).hexdigest()==receipt['output_sha256']
    return list(csv.DictReader(io.StringIO(call.stdout),delimiter='\t'))
receipts=json.loads((A/'RUN_RECEIPT.json').read_text())['guarded_projections'];rows=query(s['native_source'],'edition,page,locus,kind,source_group_index,ivtff_group_raw,left_separator,right_separator',receipts[0]);metadata=query(s['metadata_source'],'edition,page,locus,source_group_index,currier,section,hand',receipts[1])
def key(x):return x['edition'],x['locus'],int(x['source_group_index'])
meta={key(x):x for x in metadata};assert len(meta)==len(metadata)
prose=[x for x in rows if x['kind']=='P'];assert len({key(x) for x in prose})==len(prose);page_universe=sorted({x['page'] for x in prose});assert len(page_universe)==179
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
expected={(ed,'pooled','ALL') for ed in groups}|{(ed,f,v) for ed in groups for f in fields for v in fields[f]};cells={(c['reader'],c['field'],c['value']):c for c in r['cells']};assert len(cells)==len(r['cells']) and set(cells)==expected
joint={key:0 for key in cells};metric_values={key:{k:[] for k in s['metrics']} for key in cells};passes={key:Counter() for key in cells}
for ident,cell in cells.items():
    ed,f,v=ident;capacity=sum(f=='pooled' or x[1][f]==v for x in groups[ed]);assert capacity==cell['eligible_groups']
    assert cell['capacity']==('SCOREABLE' if capacity>=n else 'NO_CAPACITY') and len(cell['samples'])==(128 if capacity>=n else 0)
for seed in range(128):
    pages=page_universe.copy();random.Random(seed).shuffle(pages);rank={p:i for i,p in enumerate(pages)}
    ordered={ed:sorted(items,key=lambda x:(rank[x[0]['page']],x[0]['locus'],int(x[0]['source_group_index']))) for ed,items in groups.items()}
    for ident,cell in cells.items():
        if cell['capacity']!='SCOREABLE':continue
        ed,f,v=ident;selected=[x for x in ordered[ed] if f=='pooled' or x[1][f]==v][:n];actual=cell['samples'][seed];assert actual['seed']==seed and len(selected)==n
        assert hashlib.sha256(json.dumps([x[3] for x in selected],separators=(',',':')).encode()).hexdigest()==actual['sample_ids_sha256']
        values=statistics(x[2] for x in selected);close(values,actual['metrics'])
        for k in values:metric_values[ident][k].append(values[k])
        ok={k:abs(candidate[k]-values[k])<=(tol*values[k] if kind=='relative' else tol) for k,(kind,tol) in s['metrics'].items()}
        assert actual['within']==ok and actual['joint']==all(ok.values());joint[ident]+=all(ok.values());passes[ident].update({k:int(v) for k,v in ok.items()})
for ident,cell in cells.items():
    if cell['capacity']=='SCOREABLE':
        assert cell['joint_passes']==joint[ident] and cell['metric_passes']==dict(passes[ident])
        for k,v in metric_values[ident].items():assert abs(min(v)-cell['ranges'][k][0])<1e-10 and abs(max(v)-cell['ranges'][k][1])<1e-10
for ed in groups:
    keys=[key for key,cell in cells.items() if key[0]==ed and cell['capacity']=='SCOREABLE'];matches=sum(joint[k] for k in keys);decision='FIXED_WORDBOOK_SCREEN_EXCLUDED' if keys and not matches else 'SIX_INVARIANT_SCREEN_SURVIVES' if keys else 'NO_CAPACITY'
    assert r['decisions'][ed]=={'scoreable_cells':len(keys),'joint_matches':matches,'decision':decision}
status='FIXED_WORDBOOK_SCREEN_EXCLUDED_ALL_READINGS' if all(x['decision']=='FIXED_WORDBOOK_SCREEN_EXCLUDED' for x in r['decisions'].values()) else 'FIXED_WORDBOOK_MIXED_OR_SURVIVES';assert r['status']==status
v={'experiment':'GDT1229','status':'PASS','validated_utc':datetime.now(timezone.utc).isoformat(),'source_tokens':len(source),'physical_groups':n,'source_sections':71,'wordbook_entries':len(lex),'samples_rebuilt':sum(len(c['samples']) for c in cells.values()),'checks':['frozen inputs and code','raw source projection independent of upstream cache','prefix-bucket encoding and full serialized71paragraph inverse','canonical row layout and dictionary costs','selector-first native regex and metadata joins','all sample ID hashes and six separate statistics','all capacities tolerances summaries and decisions'],'claim':'Same-author independent computation; no semantic or historical confirmation.'}
(A/'VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v,indent=2))
