#!/usr/bin/env python3
import collections,csv,hashlib,json,random,datetime
from pathlib import Path
import scribes as s
import metrics as m
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
SOURCE=ROOT/'experiments/yolo/gdt1170_repetition_context_neutral_copy/artifacts/GUARDED.tsv'
SOURCE_HASH='ccff1909c3dbca720b28f11711278853e3befa99e6f444a0335249d6d6db01be'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(name,obj):(E/'artifacts'/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')

def wrap(rows,width=48):
    lines=[];line=[];length=0
    for row in rows:
        for w in row:
            size=len(m.glyphs(w))
            if line and length+1+size>width:lines.append(line);line=[];length=0
            length+=size+bool(line);line.append(w)
    if line:lines.append(line)
    return lines

def restore_rows(model,lines):
    flat=[w for row in lines for w in row]
    if model in (8,10):
        rows=[];row=[]
        for w in flat:
            row.append(w)
            if w==s.CLOSE:rows.append(row);row=[]
        assert not row;return rows
    size={1:5,2:5,3:5,4:7,5:5,6:5,7:5,9:9}[model]
    assert len(flat)%size==0
    return [flat[i:i+size] for i in range(0,len(flat),size)]

def target():
    assert sha(SOURCE)==SOURCE_HASH
    spec=json.loads((ROOT/'experiments/yolo/gdt1170_repetition_context_neutral_copy/src/SPEC.json').read_text())
    allowed=set(spec['allowed']);by=collections.defaultdict(list);counts=collections.defaultdict(collections.Counter)
    for r in csv.DictReader(SOURCE.open(),delimiter='\t'):
        assert r['page'] in allowed and not r['page'].startswith('f84') and r['page']!='f116v'
        if r['kind']=='P':by[r['edition'],r['page'],r['locus']].append(r)
    segments=collections.defaultdict(list)
    pages=sorted({page for _,page,_ in by});random.Random(1174).shuffle(pages);rank={p:i for i,p in enumerate(pages)}
    for (ed,page,loc),rows in sorted(by.items(),key=lambda kv:(rank[kv[0][1]],kv[0][2],kv[0][0])):
        rows.sort(key=lambda r:int(r['source_group_index']));segment=[];prev=None
        for r in rows:
            counts[ed]['all_prose_groups']+=1
            boundary=r['left_separator'] in ('DEFINITE_SPACE','LINE_START') and r['right_separator'] in ('DEFINITE_SPACE','LINE_END')
            parsed=m.glyphs(r['ivtff_group_raw'])
            if not boundary:counts[ed]['uncertain_or_drawing_boundary']+=1
            elif not parsed:counts[ed]['outside_fixed_repertoire_or_unresolved']+=1
            else:counts[ed]['eligible_groups']+=1
            linked=prev is not None and int(r['source_group_index'])==int(prev['source_group_index'])+1 and prev['right_separator']==r['left_separator']=='DEFINITE_SPACE'
            if not boundary or not parsed or (segment and not linked):
                if segment:segments[ed].append(segment);segment=[]
            if boundary and parsed:segment.append(r['ivtff_group_raw'])
            prev=r
        if segment:segments[ed].append(segment)
    return {ed:m.measure(seg) for ed,seg in sorted(segments.items())},{ed:dict(c) for ed,c in counts.items()}

def main():
    lock=json.loads((E/'artifacts/REGISTRATION_LOCK.json').read_text())
    for p,h in lock['files'].items():assert sha(E/p)==h,('modified registered file',p)
    records=s.source();examples=[(3,0,0,1,1,0,2),(3,0,0,1,1,1,2),(3,1,0,1,1,1,2),(3,1,0,1,1,1,2)]
    synthetic={};example_output={};roundtrips={}
    save('SOURCE_MESSAGES.json',records)
    for model in range(1,11):
        pages=[wrap(s.encode(model,r)) for r in records]
        restored=[s.decode(model,restore_rows(model,lines)) for lines in pages]
        assert restored==records
        assert all(m.glyphs(w) for page in pages for line in page for w in line)
        (E/'artifacts'/f'SYSTEM_{model:02d}.txt').write_text('\n\n'.join('\n'.join(' '.join(line) for line in page) for page in pages)+'\n')
        synthetic[model]=m.measure([line for page in pages for line in page])
        erows=s.encode(model,examples)
        assert s.decode(model,erows)==examples
        example_output[model]={'name':s.NAMES[model],'written_records':[' '.join(w) for w in erows],
                               'decoded':[s.explanation(r) for r in examples]}
        roundtrips[model]={'pages':len(records),'messages':sum(map(len,records)),
                           'all_exact':True,'alphabet_only':True,'all_output_words':sum(len(line) for page in pages for line in page)}
    targets,scope=target()
    result={'status':'DESCRIPTIVE_CONSTRUCTION_SCREEN','target_source_sha256':SOURCE_HASH,
            'sample_tokens':8000,'scope':scope,'targets':targets,'models':synthetic,'roundtrips':roundtrips,
            'comparison':{model:{ed:m.compare(model_metrics,t) for ed,t in targets.items()} for model,model_metrics in synthetic.items()},
            'confirmed_words':0,'independent_confirmation':False,
            'completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    save('EXAMPLES.json',example_output);save('RESULT.json',result)
    print(json.dumps({'scope':scope,'targets':{ed:{k:t[k] for k in ('mean_length','type_ratio','top10_share','conditional_entropy','exact_repeat','edit1_repeat')} for ed,t in targets.items()},
                      'models':{i:{'name':s.NAMES[i],'screen_counts':{ed:r['passed'] for ed,r in result['comparison'][i].items()},'joint':all(r['joint_screen'] for r in result['comparison'][i].values())} for i in synthetic}},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
