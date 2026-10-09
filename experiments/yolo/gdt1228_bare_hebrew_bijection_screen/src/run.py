#!/usr/bin/env python3
"""Three relabeling invariants of one fixed full-source projection."""
from pathlib import Path
from collections import Counter,defaultdict
from html.parser import HTMLParser
from datetime import datetime,timezone
import csv,hashlib,io,json,math,random,re,subprocess,unicodedata
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def digest(ids):return hashlib.sha256(json.dumps(ids,separators=(',',':')).encode()).hexdigest()
class Text(HTMLParser):
    def __init__(self):super().__init__();self.parts=[]
    def handle_starttag(self,t,attrs):assert t=='small',t
    def handle_endtag(self,t):assert t=='small',t
    def handle_data(self,t):self.parts.append(t)
def source(spec):
    sections=[];fold=str.maketrans('ךםןףץ','כמנפצ')
    for chapter,path in enumerate(spec['hebrew_files'],1):
        o=json.loads((ROOT/path).read_text());assert not o['warnings'] and o['sections']==[str(chapter)]
        vs=o['versions'];assert len(vs)==1 and vs[0]['versionTitle']=='Torat Emet 363'
        for part,raw in enumerate(vs[0]['text'],1):
            h=Text();h.feed(raw);h.close();text=''.join(h.parts);assert text.strip()
            for c in text:
                assert '\u05d0'<=c<='\u05ea' or unicodedata.category(c).startswith('M') or c.isspace() or c in '\"\'(),.:?[]',repr(c)
            stripped=''.join(c for c in text if not unicodedata.category(c).startswith('M') and c not in '\"\'')
            words=[w.translate(fold) for w in re.findall('[\u05d0-\u05ea]+',stripped)]
            assert words
            sections.append({'ref':f'{chapter}:{part}','words':words})
    assert len(sections)==71
    words=[w for row in sections for w in row['words']];assert len(words)>=500
    assert set(''.join(words))<=set('אבגדהוזחטיכלמנסעפצקרשת')
    return sections,words

def measured(sequences):
    lengths=Counter();pairs=Counter();n=0
    for word,c in Counter(tuple(x) for x in sequences).items():
        lengths[len(word)]+=c;n+=c
        for edge in zip(word,word[1:]):pairs[edge]+=c
    avg=sum(k*c for k,c in lengths.items())/n
    sd=math.sqrt(sum(c*(k-avg)**2 for k,c in lengths.items())/n)
    left=Counter()
    for (a,b),c in pairs.items():left[a]+=c
    total=sum(pairs.values());assert total
    h=-sum(c/total*math.log2(c/left[a]) for (a,b),c in pairs.items())
    return {'mean_length':avg,'sd_length':sd,'conditional_entropy':h}

def guarded(path,columns,allowed):
    cmd=['./vmanus-exp','query-tsv',path,'--selector','page']
    for p in allowed:cmd+=['--allow',p]
    cmd+=['--columns',','.join(columns)]
    call=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True,check=True)
    return list(csv.DictReader(io.StringIO(call.stdout),delimiter='\t')),{'command':cmd,'receipt':call.stderr.strip(),'output_sha256':hashlib.sha256(call.stdout.encode()).hexdigest()}

def main():
    assert not (A/'RESULT.json').exists()
    started=datetime.now(timezone.utc).isoformat();s=json.loads((D/'src/SPEC.json').read_text())
    for p,h in json.loads((A/'REGISTRATION_LOCK.json').read_text())['files'].items():assert sha(ROOT/p)==h,p
    # Hand-computable fixtures: no native or historical source input.
    assert measured(['aba','aca'])=={'mean_length':3.0,'sd_length':0.0,'conditional_entropy':0.5}
    v=measured(['aba','ab']);assert v=={'mean_length':2.5,'sd_length':0.5,'conditional_entropy':0.0}
    sections,words=source(s);n=len(words)
    candidates={'logical':measured(words),'reversed':measured([w[::-1] for w in words])}
    (A/'SOURCE_PROJECTION.json').write_text(json.dumps({'source_sections':sections,'tokens':n,'claim':'Bare digital-edition projection only; printed marks and editorial brackets are not recoverable from this stream.'},ensure_ascii=False,indent=2)+'\n')
    allowed=json.loads((ROOT/s['scope_spec']).read_text())['allowed']
    assert len(allowed)==len(set(allowed))==179 and not any(p.startswith('f84') or p=='f116v' for p in allowed)
    rows,receipt1=guarded(s['native_source'],['edition','page','locus','kind','source_group_index','ivtff_group_raw','left_separator','right_separator'],allowed)
    meta,receipt2=guarded(s['metadata_source'],['edition','page','locus','source_group_index','currier','section','hand'],allowed)
    def key(r):return r['edition'],r['locus'],int(r['source_group_index'])
    metadata={key(r):r for r in meta};assert len(metadata)==len(meta)
    prose=[r for r in rows if r['kind']=='P'];assert len({key(r) for r in prose})==len(prose)
    pages=sorted({r['page'] for r in prose});assert len(pages)==179
    order=sorted(s['working_signs'],key=lambda x:(-len(x),x));cache={}
    def parse(word):
        if word not in cache:
            gs=[];i=0
            while i<len(word):
                g=next((x for x in order if word.startswith(x,i)),None)
                if g is None:gs=[];break
                gs.append(g);i+=len(g)
            cache[word]=tuple(gs)
        return cache[word]
    values={field:set() for field in ('currier','section','hand')};eligible=defaultdict(list)
    for row in prose:
        m=metadata[key(row)];assert m['page']==row['page']
        for field in values:row[field]=m[field];values[field].add(m[field])
        units=parse(row['ivtff_group_raw'])
        if units and row['left_separator'] in ('DEFINITE_SPACE','LINE_START') and row['right_separator'] in ('DEFINITE_SPACE','LINE_END'):
            row['units']=units;row['id']=f"{row['edition']}|{row['locus']}|G{int(row['source_group_index']):03d}";eligible[row['edition']].append(row)
    assert set(eligible)=={'IT2a','RF1b','ZL3b'}
    cells=[]
    for ed,items in sorted(eligible.items()):
        for field,value in [('pooled','ALL')]+[(f,v) for f in values for v in sorted(values[f])]:
            count=sum(field=='pooled' or r[field]==value for r in items)
            cells.append({'reader':ed,'field':field,'value':value,'eligible_groups':count,'capacity':'SCOREABLE' if count>=n else 'NO_CAPACITY','samples':[]})
    for seed in range(128):
        po=pages.copy();random.Random(seed).shuffle(po);rank={p:i for i,p in enumerate(po)}
        sorted_rows={ed:sorted(items,key=lambda r:(rank[r['page']],r['locus'],int(r['source_group_index']))) for ed,items in eligible.items()}
        for cell in cells:
            if cell['capacity']!='SCOREABLE':continue
            chosen=[r for r in sorted_rows[cell['reader']] if cell['field']=='pooled' or r[cell['field']]==cell['value']][:n]
            assert len(chosen)==n
            native=measured(r['units'] for r in chosen);comparisons={}
            for orientation,candidate in candidates.items():
                within={k:abs(candidate[k]-native[k])<=(tol*native[k] if kind=='relative' else tol) for k,(kind,tol) in s['metrics'].items()}
                comparisons[orientation]={'within':within,'joint':all(within.values())}
            cell['samples'].append({'seed':seed,'metrics':native,'comparisons':comparisons,'sample_ids_sha256':digest([r['id'] for r in chosen]),'last_id':chosen[-1]['id']})
    for cell in cells:
        if cell['capacity']=='SCOREABLE':
            cell['joint_passes']={o:sum(x['comparisons'][o]['joint'] for x in cell['samples']) for o in candidates}
            cell['ranges']={k:[min(x['metrics'][k] for x in cell['samples']),max(x['metrics'][k] for x in cell['samples'])] for k in s['metrics']}
    decisions={}
    for ed in sorted(eligible):
        own=[c for c in cells if c['reader']==ed and c['capacity']=='SCOREABLE']
        by={o:sum(c['joint_passes'][o] for c in own) for o in candidates}
        decisions[ed]={'scoreable_cells':len(own),'joint_matches':by,'decision':'DIRECT_BIJECTION_SCREEN_EXCLUDED' if own and not any(by.values()) else 'COARSE_SCREEN_SURVIVES' if own else 'NO_CAPACITY'}
    status='DIRECT_BIJECTION_SCREEN_EXCLUDED_ALL_READINGS' if all(x['decision']=='DIRECT_BIJECTION_SCREEN_EXCLUDED' for x in decisions.values()) else 'DIRECT_BIJECTION_SCREEN_MIXED_OR_SURVIVES'
    result={'experiment':'GDT1228','status':status,'source_tokens':n,'source_sections':len(sections),'candidate_metrics':candidates,'eligible_groups':{ed:len(v) for ed,v in sorted(eligible.items())},'decisions':decisions,'cells':cells,'claim_ceiling':s['limits']}
    (A/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    (A/'RUN_RECEIPT.json').write_text(json.dumps({'started_utc':started,'finished_utc':datetime.now(timezone.utc).isoformat(),'guarded_projections':[receipt1,receipt2]},indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['status','source_tokens','source_sections','candidate_metrics','eligible_groups','decisions']},indent=2))
if __name__=='__main__':main()
