#!/usr/bin/env python3
"""One fixed complete spelling-book notation; no fitting or key search."""
from pathlib import Path
from collections import Counter,defaultdict
from datetime import datetime,timezone
import csv,hashlib,io,json,math,random,subprocess
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def digest(x):return hashlib.sha256(json.dumps(x,separators=(',',':')).encode()).hexdigest()
def save(n,x):(A/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def entropy(c):
    n=sum(c.values());return -sum(v/n*math.log2(v/n) for v in c.values()) if n else 0.
def measure(words):
    wc=Counter(tuple(w) for w in words);n=sum(wc.values());length=Counter();glyph=Counter();pairs=Counter()
    for w,c in wc.items():
        length[len(w)]+=c
        for g in w:glyph[g]+=c
        for pair in zip(w,w[1:]):pairs[pair]+=c
    prev=Counter()
    for (x,y),c in pairs.items():prev[x]+=c
    avg=sum(k*v for k,v in length.items())/n;total=sum(pairs.values());assert total
    return {'mean_length':avg,'sd_length':math.sqrt(sum(v*(k-avg)**2 for k,v in length.items())/n),'top10_share':sum(sorted(wc.values(),reverse=True)[:10])/n,'type_ratio':len(wc)/n,'glyph_entropy':entropy(glyph),'conditional_entropy':-sum(v/total*math.log2(v/prev[x]) for (x,y),v in pairs.items())}
class Writer:
    def __init__(self,sigma,lex,signs):
        assert 1<=len(sigma)<=440 and len(set(sigma))==len(sigma)
        self.sigma=sigma;self.lex=set(lex);self.signs=signs;self.tree={};self.term=set(lex)
        order={c:i for i,c in enumerate(sigma)};buckets=defaultdict(set)
        for w in self.lex:
            assert w and set(w)<=set(sigma)
            for i,c in enumerate(w):buckets[w[:i]].add(c)
        self.tree={p:sorted(cs,key=order.get) for p,cs in buckets.items()}
    def integer(self,r):
        assert r>0;k,j=divmod(r-1,20);return [self.signs[20]]*k+[self.signs[j]]
    def units(self,w):
        assert w and set(w)<=set(self.sigma)
        if w not in self.lex:return [[self.signs[21]]]+[self.integer(self.sigma.index(c)+1) for c in w]
        p='';out=[]
        for c in w:
            out.append(self.integer(self.tree[p].index(c)+1));p+=c
        assert p in self.term;return out
    def code(self,w):return tuple(g for unit in self.units(w) for g in unit)
    def paragraph(self,words):
        rows=[];current=[];used=0
        for w in words:
            units=self.units(w);flat=[g for u in units for g in u]
            if len(flat)<=24:
                if current and used+1+len(flat)>24:rows.append(current);current=[];used=0
                current.append(tuple(flat));used+=len(flat)+(1 if len(current)>1 else 0);continue
            if current:rows.append(current);current=[];used=0
            while sum(map(len,units))>24:
                count=0;size=0
                while count<len(units) and size+len(units[count])<=23:size+=len(units[count]);count+=1
                assert count and not(count==1 and units[0]==[self.signs[21]])
                prefix=[g for u in units[:count] for g in u]+[self.signs[21]];rows.append([tuple(prefix)]);units=units[count:]
            final=tuple(g for u in units for g in u);assert final and len(final)<=24
            current=[final];used=len(final)
        if current:rows.append(current)
        return rows

def guarded(path,cols,allows):
    cmd=['./vmanus-exp','query-tsv',path,'--selector','page']
    for p in allows:cmd+=['--allow',p]
    cmd+=['--columns',','.join(cols)]
    run=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True,check=True)
    return list(csv.DictReader(io.StringIO(run.stdout),delimiter='\t')),{'command':cmd,'receipt':run.stderr.strip(),'output_sha256':hashlib.sha256(run.stdout.encode()).hexdigest()}

def main():
    assert not(A/'RESULT.json').exists();began=datetime.now(timezone.utc).isoformat();s=json.loads((D/'src/SPEC.json').read_text())
    for p,h in json.loads((A/'REGISTRATION_LOCK.json').read_text())['files'].items():assert sha(ROOT/p)==h,p
    sections=json.loads((ROOT/s['source_projection']).read_text())['source_sections'];words=[w for row in sections for w in row['words']]
    assert len(words)==6288 and len(sections)==71
    order={c:i for i,c in enumerate(s['source_alphabet'])};lex=sorted(set(words),key=lambda w:tuple(order[c] for c in w));wr=Writer(s['source_alphabet'],lex,s['working_signs'])
    # Tiny public examples check ranks and the actual24cell continuation contract.
    fixture=Writer('abcdefghijklmnopqrstuvwxyz.,',['add','and','drink','drinks','is','not','oil','salt','then','wait','warm','water','.',','],s['working_signs'])
    assert ''.join(fixture.code('warm'))=='yaoa' and ''.join(fixture.code('drink'))=='oaaaa'
    assert fixture.integer(21)==['cph','a'] and fixture.integer(40)==['cph','cth'] and fixture.integer(41)==['cph','cph','a']
    pp=fixture.paragraph(['uncharacteristically,']);assert [sum(map(len,r))+len(r)-1 for r in pp]==[24,2]
    codes={w:wr.code(w) for w in lex};assert len(set(codes.values()))==len(lex)
    encoded=[wr.paragraph(row['words']) for row in sections]
    physical=[w for para in encoded for row in para for w in row];n=len(physical)
    (A/'ENCODED.txt').write_text('\n\n'.join('\n'.join(' '.join(''.join(w) for w in row) for row in para) for para in encoded)+'\n')
    frequencies=Counter(words);glyphs=Counter(g for w in physical for g in w);finals=Counter(w[-1] for w in physical)
    logical=[codes[w] for w in words];logicalfreq=Counter(logical)
    assert sorted(logicalfreq.values())==sorted(frequencies.values())
    longest=sorted(lex,key=lambda w:(-len(w),tuple(order[c] for c in w)))[:10]
    def trace(w):return {'source':w,'output':''.join(codes[w]),'drawings':list(codes[w]),'ranks':[wr.tree[w[:i]].index(c)+1 for i,c in enumerate(w)],'source_occurrences':frequencies[w]}
    source_info={'source_tokens':len(words),'source_sections':len(sections),'wordbook_entries':len(lex),'prefix_nodes_including_terminal_leaves':len(set(w[:i] for w in lex for i in range(len(w)+1))),'lookup_nodes_with_children':len(wr.tree),'complete_public_wordbook':lex,'all_word_codes':[trace(w) for w in lex],'first10_source_tokens':[trace(w) for w in words[:10]],'ten_longest_types':[trace(w) for w in longest],'maximum_source_length':max(map(len,words)),'maximum_logical_drawing_length':max(map(len,logical)),'physical_groups':n,'physical_rows':sum(map(len,encoded)),'physical_continuations':sum(w[-1]=='cfh' for w in physical),'physical_drawings':sum(map(len,physical)),'physical_intergroup_blanks':sum(len(row)-1 for para in encoded for row in para),'glyph_counts':dict(sorted(glyphs.items())),'word_final_counts':dict(sorted(finals.items())),'logical_frequency_invariance':True,'forced_unary_edge_tokens':sum(frequencies[w]*sum(len(wr.tree[w[:i]])==1 for i in range(len(w))) for w in lex),'claim_ceiling':s['limits']}
    save('SOURCE_WRITING.json',source_info);candidate=measure(physical)
    allowed=json.loads((ROOT/s['scope_spec']).read_text())['allowed'];assert len(allowed)==len(set(allowed))==179 and not any(p.startswith('f84') or p=='f116v' for p in allowed)
    raw,receipt1=guarded(s['native_source'],['edition','page','locus','kind','source_group_index','ivtff_group_raw','left_separator','right_separator'],allowed)
    meta,receipt2=guarded(s['metadata_source'],['edition','page','locus','source_group_index','currier','section','hand'],allowed)
    def key(r):return r['edition'],r['locus'],int(r['source_group_index'])
    metadata={key(r):r for r in meta};assert len(metadata)==len(meta)
    prose=[r for r in raw if r['kind']=='P'];assert len({key(r) for r in prose})==len(prose)
    pages=sorted({r['page'] for r in prose});assert len(pages)==179
    signorder=sorted(s['working_signs'],key=lambda x:(-len(x),x));cache={}
    def parse(raw):
        if raw not in cache:
            seq=[];i=0
            while i<len(raw):
                g=next((x for x in signorder if raw.startswith(x,i)),None)
                if g is None:seq=[];break
                seq.append(g);i+=len(g)
            cache[raw]=tuple(seq)
        return cache[raw]
    values={k:set() for k in ['currier','section','hand']};eligible=defaultdict(list)
    for r in prose:
        m=metadata[key(r)];assert m['page']==r['page']
        for k in values:r[k]=m[k];values[k].add(m[k])
        units=parse(r['ivtff_group_raw'])
        if units and r['left_separator'] in ['DEFINITE_SPACE','LINE_START'] and r['right_separator'] in ['DEFINITE_SPACE','LINE_END']:
            r['units']=units;r['id']=f"{r['edition']}|{r['locus']}|G{int(r['source_group_index']):03d}";eligible[r['edition']].append(r)
    assert set(eligible)=={'IT2a','RF1b','ZL3b'};cells=[]
    for ed,rows in sorted(eligible.items()):
        for field,value in [('pooled','ALL')]+[(k,v) for k in values for v in sorted(values[k])]:
            count=sum(field=='pooled' or r[field]==value for r in rows)
            cells.append({'reader':ed,'field':field,'value':value,'eligible_groups':count,'capacity':'SCOREABLE' if count>=n else 'NO_CAPACITY','samples':[]})
    for seed in range(128):
        po=pages.copy();random.Random(seed).shuffle(po);rank={p:i for i,p in enumerate(po)}
        ordered={ed:sorted(rows,key=lambda r:(rank[r['page']],r['locus'],int(r['source_group_index']))) for ed,rows in eligible.items()}
        for cell in cells:
            if cell['capacity']!='SCOREABLE':continue
            selected=[r for r in ordered[cell['reader']] if cell['field']=='pooled' or r[cell['field']]==cell['value']][:n];assert len(selected)==n
            met=measure(r['units'] for r in selected);within={k:abs(candidate[k]-met[k])<=(v*met[k] if kind=='relative' else v) for k,(kind,v) in s['metrics'].items()}
            cell['samples'].append({'seed':seed,'metrics':met,'within':within,'joint':all(within.values()),'sample_ids_sha256':digest([r['id'] for r in selected])})
    for cell in cells:
        if cell['capacity']=='SCOREABLE':
            cell['joint_passes']=sum(r['joint'] for r in cell['samples']);cell['metric_passes']={k:sum(r['within'][k] for r in cell['samples']) for k in s['metrics']};cell['ranges']={k:[min(r['metrics'][k] for r in cell['samples']),max(r['metrics'][k] for r in cell['samples'])] for k in s['metrics']}
    decisions={}
    for ed in sorted(eligible):
        own=[c for c in cells if c['reader']==ed and c['capacity']=='SCOREABLE'];matches=sum(c['joint_passes'] for c in own)
        decisions[ed]={'scoreable_cells':len(own),'joint_matches':matches,'decision':'FIXED_WORDBOOK_SCREEN_EXCLUDED' if own and not matches else 'SIX_INVARIANT_SCREEN_SURVIVES' if own else 'NO_CAPACITY'}
    status='FIXED_WORDBOOK_SCREEN_EXCLUDED_ALL_READINGS' if all(d['decision']=='FIXED_WORDBOOK_SCREEN_EXCLUDED' for d in decisions.values()) else 'FIXED_WORDBOOK_MIXED_OR_SURVIVES'
    result={'experiment':'GDT1229','status':status,'source_tokens':len(words),'physical_groups':n,'candidate_metrics':candidate,'eligible_groups':{ed:len(rows) for ed,rows in eligible.items()},'decisions':decisions,'cells':cells,'claim_ceiling':s['limits']}
    save('RESULT.json',result);save('RUN_RECEIPT.json',{'started_utc':began,'finished_utc':datetime.now(timezone.utc).isoformat(),'guarded_projections':[receipt1,receipt2]})
    print(json.dumps({k:result[k] for k in ['status','source_tokens','physical_groups','candidate_metrics','decisions']},indent=2))
if __name__=='__main__':main()
