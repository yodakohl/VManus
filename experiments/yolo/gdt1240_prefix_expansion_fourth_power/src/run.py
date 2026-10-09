#!/usr/bin/env python3
"""Fixed-source necessary envelope; no key search or native meaning."""
from pathlib import Path
from collections import defaultdict
from datetime import datetime,timezone
from itertools import product
import gzip,hashlib,json,sys
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'

def load(p):
    data=p.read_bytes()
    return json.loads(gzip.decompress(data)if p.suffix=='.gz'else data)

def save(name,obj):
    (A/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')

def powers(word):
    out=[]
    for period in range(1,(len(word)-2)//4+1):
        for start in range(1,len(word)-4*period):
            unit=word[start:start+period]
            if word[start:start+4*period]==unit*4:
                out.append({'start':start,'period':period,'X':word[:start],
                            'U':unit,'Y':word[start+4*period:]})
    return out

def fixtures():
    cases={'baaaac':[(1,1)],'aaaa':[],'abababab':[],
           'xababababy':[(1,2)],'zabcabcabcabct':[(1,3)],
           'aaaaab':[(1,1)],'baaaaa':[(1,1)]}
    for w,expected in cases.items():
        assert [(x['start'],x['period'])for x in powers(w)]==expected
    assert any(x['U']=='aa'for x in powers('zaaaaaaaay'))
    count=0
    for n in range(13):
        for letters in product('ab',repeat=n):
            w=''.join(letters);other=[]
            for left in range(1,n):
                for right in range(left+4,n):
                    size=right-left
                    if size%4:continue
                    step=size//4
                    if all(w[j]==w[j+step]for j in range(left,right-step)):
                        other.append((left,step))
            assert sorted((r['start'],r['period'])for r in powers(w))==sorted(other)
            count+=1
    return {'status':'PASS','exhaustive_binary_words':count,'max_length':12,
            'named_cases':cases,'nonprimitive_power_retained':True}

def proof_packet(spec,native):
    out={}
    for ed in spec['readers']:
        groups=native[ed];by_units=defaultdict(list)
        for g in groups:by_units[tuple(g['units'])].append(g)
        cert=load(ROOT/spec['weighted_proof_dir']/('CERTIFICATE_'+ed+'_pages.json.gz'))
        words=cert['universe'];events=cert['events'];nodes={};roots={}
        def visit(eid):
            if eid in nodes:return
            wi,support,parents=events[eid];word=words[wi]
            if parents:
                for p in parents:
                    assert p<eid;visit(p)
                u,v=[nodes[p]['units']for p in parents]
                assert v==u+word
                assert support==min(nodes[p]['support']for p in parents)
                row={'event_id':eid,'units':word,'support':support,'parents':parents}
            else:
                gs=by_units[tuple(word)];assert gs
                assert support==len({g['page']for g in gs})
                row={'event_id':eid,'units':word,'support':support,'parents':None,
                     'source_ids':[g['id']for g in gs],'occurrences':len(gs),
                     'pages':sorted({g['page']for g in gs})}
            nodes[eid]=row
        for glyph in spec['required_singletons']:
            wi=words.index([glyph]);eid=cert['final_event'][wi]
            visit(eid);assert nodes[eid]['units']==[glyph]
            roots[glyph]=eid
        witnesses=by_units[tuple(spec['native_witness_units'])]
        assert witnesses and all(g['ivtff_group_raw']==spec['native_witness']for g in witnesses)
        out[ed]={'singleton_root_events':roots,'proof_events':[nodes[i]for i in sorted(nodes)],
                 'whole_witness_occurrences':witnesses,'witness_count':len(witnesses),
                 'witness_distinct_selectors':len({g['page']for g in witnesses}),
                 'singleton_selector_support':{g:nodes[e]['support']for g,e in roots.items()}}
    return out

def main():
    if '--fixtures'in sys.argv:
        print(json.dumps(fixtures()));return
    assert not(A/'RESULT.json').exists()
    start=datetime.now(timezone.utc).isoformat();spec=load(D/'src/SPEC.json')
    for p,h in load(A/'REGISTRATION_LOCK.json')['files'].items():
        assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    save('FIXTURES.json',fixtures())
    native=load(ROOT/spec['native_groups']);save('NATIVE_PROOF.json',proof_packet(spec,native))
    recipes=load(ROOT/spec['recipe_source']);hebrew=load(ROOT/spec['hebrew_source'])
    result={};all_hits={}
    for collection in spec['collections']:
        records=hebrew['source_sections']if collection=='deot'else recipes[collection]
        hits=[];tokens=0;types=set();maximum=0
        for ordinal,row in enumerate(records):
            ref=row['ref']if collection=='deot'else row['id']
            for i,w in enumerate(row['words']):
                tokens+=1;types.add(w);maximum=max(maximum,len(w));fs=powers(w)
                if fs:hits.append({'record_index':ordinal,'record_id':ref,'word_index':i,
                                   'word':w,'factorizations':fs})
        all_hits[collection]=hits
        result[collection]={'records':len(records),'source_tokens':tokens,'source_types':len(types),
                            'maximum_word_codepoints':maximum,'supporting_tokens':len(hits),
                            'supporting_types':len({h['word']for h in hits}),
                            'factorizations':sum(len(h['factorizations'])for h in hits),
                            'status':'SOURCE_ENVELOPE_EXCLUDED'if not hits else'NECESSARY_ENVELOPE_INCONCLUSIVE'}
    save('SOURCE_POWER_WITNESSES.json',all_hits)
    status='ALL_FIVE_SOURCE_EXPANSION_ENVELOPES_EXCLUDED'if all(not h for h in all_hits.values())else'MIXED_OR_INCONCLUSIVE_EXPANSION_ENVELOPES'
    save('RESULT.json',{'experiment':'GDT1240','status':status,'sources':result,
                       'claim_ceiling':spec['claim_ceiling']})
    save('RUN_RECEIPT.json',{'started_utc':start,'finished_utc':datetime.now(timezone.utc).isoformat(),
                            'new_native_queries':0,'new_images':0,'tables_fitted':0})
    print(json.dumps({'status':status,'sources':result},indent=2))

if __name__=='__main__':main()
