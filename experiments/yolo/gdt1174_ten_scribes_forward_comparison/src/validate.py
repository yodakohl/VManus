#!/usr/bin/env python3
"""Separate metric reconstruction, exhaustive finite roundtrip and layout checks.
Same author; encoder/decoder consistency is not semantic confirmation.
"""
import collections,csv,hashlib,json,math,random,re
from pathlib import Path
import scribes as s
import run
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
PAT=re.compile('|'.join(sorted(s.SIGNS,key=lambda v:(-len(v),v))))

def parse(word):
    parts=PAT.findall(word)
    return parts if ''.join(parts)==word else None
def H(c):
    total=sum(c.values())
    return math.log2(total)-sum(n*math.log2(n) for n in c.values())/total
def distance(a,b):
    old=list(range(len(b)+1))
    for i,x in enumerate(a,1):
        new=[i]
        for j,y in enumerate(b,1):new.append(min(new[-1]+1,old[j]+1,old[j-1]+(x!=y)))
        old=new
    return old[-1]
def near(a,b):return abs(a-b)<1e-10

def independent(segments):
    out=[];left=8000
    for seg in segments:
        if left<=0:break
        chosen=seg[:left];left-=len(chosen)
        if chosen:out.append(chosen)
    assert left==0
    words=[w for line in out for w in line];g=[parse(w) for w in words]
    assert all(g)
    lex=collections.Counter(words);letters=collections.Counter(x for w in g for x in w)
    lengths=collections.Counter(map(len,g));pairs=collections.Counter((a,b) for w in g for a,b in zip(w,w[1:]));first=collections.Counter()
    for (a,b),n in pairs.items():first[a]+=n
    mu=sum(map(len,g))/8000
    adjacent=[(a,b) for line in out for a,b in zip(line,line[1:])]
    beginnings=collections.Counter(w[0] for w in g);endings=collections.Counter(w[-1] for w in g)
    mixture={k:(beginnings[k]+endings[k])/16000 for k in beginnings.keys()|endings.keys()}
    edge_js=-sum(v*math.log2(v) for v in mixture.values())-(H(beginnings)+H(endings))/2
    return dict(tokens=8000,types=len(lex),type_ratio=len(lex)/8000,mean_length=mu,
                sd_length=math.sqrt(sum((len(w)-mu)**2 for w in g)/8000),
                top10_share=sum(sorted(lex.values(),reverse=True)[:10])/8000,
                word_entropy=H(lex),glyph_entropy=H(letters),conditional_entropy=H(pairs)-H(first),
                first_last_js=edge_js,
                adjacent_pairs=len(adjacent),exact_repeat=sum(a==b for a,b in adjacent)/len(adjacent),
                edit1_repeat=sum(distance(parse(a),parse(b))==1 for a,b in adjacent)/len(adjacent),
                glyph_counts=dict(letters),length_counts={str(k):v for k,v in lengths.items()})

def target_projection():
    path=run.SOURCE
    assert hashlib.sha256(path.read_bytes()).hexdigest()==run.SOURCE_HASH
    allowed=set(json.loads((ROOT/'experiments/yolo/gdt1170_repetition_context_neutral_copy/src/SPEC.json').read_text())['allowed'])
    lines=collections.defaultdict(list);scope=collections.defaultdict(collections.Counter)
    for row in csv.DictReader(path.open(),delimiter='\t'):
        assert row['page'] in allowed and not row['page'].startswith('f84') and row['page']!='f116v'
        if row['kind']=='P':lines[row['edition'],row['page'],row['locus']].append(row)
    pages=sorted(set(key[1] for key in lines));random.Random(1174).shuffle(pages);rank={p:i for i,p in enumerate(pages)}
    out=collections.defaultdict(list)
    for (ed,page,loc),items in sorted(lines.items(),key=lambda pair:(rank[pair[0][1]],pair[0][2],pair[0][0])):
        current=[];last_index=-10
        for r in sorted(items,key=lambda v:int(v['source_group_index'])):
            scope[ed]['all_prose_groups']+=1
            valid_edge=r['left_separator'] in {'LINE_START','DEFINITE_SPACE'} and r['right_separator'] in {'LINE_END','DEFINITE_SPACE'}
            good=valid_edge and bool(parse(r['ivtff_group_raw']))
            key='eligible_groups' if good else ('uncertain_or_drawing_boundary' if not valid_edge else 'outside_fixed_repertoire_or_unresolved')
            scope[ed][key]+=1
            index=int(r['source_group_index'])
            if not good or index!=last_index+1:
                if current:out[ed].append(current);current=[]
            if good:current.append(r['ivtff_group_raw']);last_index=index
            else:last_index=-10
        if current:out[ed].append(current)
    return out,{k:dict(v) for k,v in scope.items()}

def main():
    result=json.loads((E/'artifacts/RESULT.json').read_text());lock=json.loads((E/'artifacts/REGISTRATION_LOCK.json').read_text())
    for name,digest in lock['files'].items():assert hashlib.sha256((E/name).read_bytes()).hexdigest()==digest
    source=json.loads((E/'artifacts/SOURCE_MESSAGES.json').read_text());assert source==[[list(r) for r in page] for page in s.source()]
    metric_checks=0;roundtrip_records=0
    for model in range(1,11):
        text=(E/'artifacts'/f'SYSTEM_{model:02d}.txt').read_text()
        pages=[[line.split() for line in page.splitlines()] for page in text.strip().split('\n\n')]
        assert len(pages)==len(source)
        decoded=[s.decode(model,run.restore_rows(model,page)) for page in pages]
        assert [[list(r) for r in page] for page in decoded]==source
        roundtrip_records+=sum(map(len,decoded))
        assert sum(len(line) for page in pages for line in page)==result['roundtrips'][str(model)]['all_output_words']
        values=independent([line for page in pages for line in page])
        for key,value in values.items():
            expected=result['models'][str(model)][key]
            assert value==expected if isinstance(value,dict) else near(value,expected),(model,key,value,expected)
            metric_checks+=1
    projections,scope=target_projection();assert scope==result['scope']
    for ed,segments in projections.items():
        for key,value in independent(segments).items():
            expected=result['targets'][ed][key]
            assert value==expected if isinstance(value,dict) else near(value,expected),(ed,key,value,expected)
            metric_checks+=1
    # Exhaust all individual finite field values, with actual stateful streams.
    records=[]
    for f,cap in enumerate(s.CAPS):
        for v in range(cap):
            item=[3,1,1,0,2];item[f]=v;records.append(s.unpack(item))
    for model in range(1,11):assert s.decode(model,s.encode(model,records))==records
    # Change physical wrapping only; a reader must not require hidden row ends.
    for width in (7,23,71):
        for model in range(1,11):
            page=s.source(pages=1)[0]
            assert s.decode(model,run.restore_rows(model,run.wrap(s.encode(model,page),width)))==page
    # Independent gate arithmetic, including vector distances.
    tolerances={'mean_length':(.20,True),'sd_length':(.25,True),'top10_share':(.05,False),'type_ratio':(.05,False),'conditional_entropy':(.30,False),'exact_repeat':(.01,False),'edit1_repeat':(.03,False),'first_last_js':(.12,False)}
    gate_checks=0
    for model,values in result['models'].items():
        for ed,target in result['targets'].items():
            entry=result['comparison'][model][ed]
            for key,(tol,relative) in tolerances.items():
                expected=abs(values[key]-target[key])<=tol*(target[key] if relative else 1)
                assert expected==entry['diagnostics'][key]['within'];gate_checks+=1
            a=values['length_counts'];b=target['length_counts'];tv=sum(abs(a.get(k,0)-b.get(k,0)) for k in a.keys()|b.keys())/16000
            assert near(tv,entry['diagnostics']['length_tv']['difference'])
            a=values['glyph_counts'];b=target['glyph_counts'];sa=sum(a.values());sb=sum(b.values());mix={k:(a.get(k,0)/sa+b.get(k,0)/sb)/2 for k in a.keys()|b.keys()}
            js=-sum(v*math.log2(v) for v in mix.values())-(H(a)+H(b))/2
            assert near(js,entry['diagnostics']['glyph_js']['difference'])
            assert entry['passed']==sum(x['within'] for x in entry['diagnostics'].values())
            assert entry['joint_screen']==all(x['within'] for x in entry['diagnostics'].values())
    bounds={'1':1/3,'2':1/3,'3':1/3,'4':3/14,'5':1/3,'6':.8,'7':2/7,'8':.2,'9':2/9,'10':2/7}
    for model,bound in bounds.items():assert result['models'][model]['top10_share']>=bound-.002
    out={'status':'PASS','metric_reconstructions':metric_checks,'gate_arithmetic_checks':gate_checks,
         'saved_message_roundtrips':roundtrip_records,'exhaustive_field_roundtrips':len(records)*10,
         'layout_tests':30,'alphabet_valid':True,'scope_accounting_exact':True,
         'source_independent_top10_lower_bounds':bounds,
         'claim_ceiling':'Same-author technical verification, with separately coded metrics and source selection. No meaning or historical authorship validated.'}
    (E/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
