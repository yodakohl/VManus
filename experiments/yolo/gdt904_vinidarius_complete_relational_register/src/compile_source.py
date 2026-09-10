#!/usr/bin/env python3
"""Complete, source-only literal interval trace; no target reader."""
import collections, hashlib, html, json, re
from pathlib import Path
E=Path(__file__).resolve().parents[1]; ROOT=E.parents[2]
S=ROOT/'research_registry/proposals/vinidarius_source_checkpoint'
EXCLUDED_A={'SOURCE_ORDINAL_NOT_SEMANTIC','TOOL_OR_MEDIUM_OUTSIDE_DECLARED_CATEGORIES','EXPLICIT_CONDITION_MARKER'}
NUM={'Roman_I':'1','I':'1','unus':'1','duo':'2','Roman_III':'3','III':'3','decem':'10','Roman_L':'50','L':'50'}

def enc(x): return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def coordinates(raw,base):
    result=[]; pos=0
    for m in re.finditer(r'&(?:#[0-9]+|#x[0-9a-fA-F]+|[a-zA-Z][a-zA-Z0-9]+);',raw):
        result.extend((base+i,base+i+1) for i in range(pos,m.start()))
        result.extend([(base+m.start(),base+m.end())]*len(html.unescape(m.group())))
        pos=m.end()
    result.extend((base+i,base+i+1) for i in range(pos,len(raw)))
    assert len(result)==len(html.unescape(raw))
    return result

def compile_source():
    a=json.loads((S/'SOURCE_TYPED_A.json').read_text()); m=json.loads((S/'SOURCE_TYPED_M.json').read_text())
    amap={}
    for r in a['records']+[dict(id='PANTRY_POSTLUDE',source='pantry',segments=[a['common_pantry_closing']])]:
        for seg in r['segments']:
            mp=coordinates(seg['raw'],seg['html_span'][0])
            assert html.unescape(seg['raw'])==seg['text']
            for q in seg['mentions']+seg['omitted_tokens']:
                lo,hi=q['span']; assert seg['text'][lo:hi]==q['surface']
                key=(r['source'],mp[lo][0],mp[hi-1][1]); assert key not in amap
                amap[key]=q
    out=[]; totals=collections.Counter(); all_atoms=set()
    for r in m['records']+[m['pantry_postlude']]:
        tokens=[]
        for origin in ['mentions','unresolved_tokens','omitted_tokens']:
            for original in r[origin]:
                q=dict(original); lo,hi=q['span']; assert r['text'][lo:hi]==q['surface']
                segs=[s for s in r['source_segments'] if s['record_text_span'][0]<=lo and hi<=s['record_text_span'][1]]
                assert len(segs)==1
                seg=segs[0]; offset=seg['record_text_span'][0]
                mp=coordinates(seg['source_html'],seg['html_character_span'][0]); key=(seg['document'],mp[lo-offset][0],mp[hi-offset-1][1])
                aq=amap[key]; assert aq['surface']==q['surface']
                totals[origin]+=1
                emit=origin!='omitted_tokens' or (aq.get('category','OMITTED') not in EXCLUDED_A|{'OMITTED'})
                # The internal subsection numeral is metadata, like all h4 ordinals.
                if r['id']=='R01' and q['surface']=='2': emit=False
                # Together-adverb, not the explicit hemina una numeral in R23.
                if r['id']=='R01' and q['surface'].lower()=='una': emit=False
                chosen=q if origin=='mentions' else aq if origin=='omitted_tokens' else q
                lemma=chosen.get('lemma'); surface=q['surface'].lower()
                if surface in {'friges','frigantur','frigis'}: lemma='frigo'
                if surface=='fiat': lemma='fio'
                if surface=='supersit': lemma='supersum'
                # M already separates amulum/amulo and addo/adicio; preserve it.
                if origin=='unresolved_tokens':
                    lemma={'spica':'spica','tritura':'tritura','conditum':'conditus',
                           'friges':'frigo','frigantur':'frigo'}.get(surface)
                atom=('LEX:'+lemma) if lemma else ('LITERAL:'+surface)
                if chosen.get('category')=='NUMERAL' and lemma in NUM: atom='NUMBER:'+NUM[lemma]
                token=dict(span=q['span'],surface=q['surface'],source_coordinate=list(key),m_origin=origin,
                           m_category=q.get('category'),a_category=aq.get('category'),
                           emitted=emit,atom=atom if emit else None,
                           role_alternatives=q.get('possible_categories',q.get('category_alternatives',[])),
                           reason='retained substantive literal token' if emit else 'declared function/equipment/metadata omission')
                tokens.append(token)
                if emit: all_atoms.add(atom)
        tokens.sort(key=lambda q:q['span']); assert len({tuple(q['span']) for q in tokens})==len(tokens)
        assert len(tokens)==r['annotation_word_tokens']
        # Exact word-token coverage, including the malformed internal ordinal.
        assert [(z.start(),z.end()) for z in re.finditer(r'[A-Za-z]+|[0-9]+',r['text'])]==[tuple(q['span']) for q in tokens]
        intervals=[]
        for s in r['explicit_spans']:
            lo,hi=s['span']; assert r['text'][lo:hi]==s['surface']
            members=[i for i,q in enumerate(tokens) if lo<=q['span'][0] and q['span'][1]<=hi]
            intervals.append(dict(kind=s['kind'],span=s['span'],surface=s['surface'],token_members=members))
        assert len({(s['kind'],*s['span']) for s in intervals})==len(intervals)
        for x in intervals:
            for y in intervals:
                assert not(x['span'][0]<y['span'][0]<x['span'][1]<y['span'][1])
        # Type ties alphabetic on OPEN and reverse on CLOSE, outer before inner.
        events=[]
        for s in intervals:
            lo,hi=s['span']; events += [(lo,1,-hi,s['kind'],'OPEN:'+s['kind']), (hi,0,-lo,s['kind'],'CLOSE:'+s['kind'])]
        for q in tokens:
            if q['emitted']: events.append((q['span'][0],2,0,'',q['atom']))
        opens=sorted([x for x in events if x[1]==1],key=lambda x:(x[0],x[2],x[3]))
        ranks={(x[0],-x[2],x[3]):i for i,x in enumerate(opens)}
        def event_key(x):
            if x[1]==0:return (x[0],0,-ranks[(-x[2],x[0],x[3])])
            if x[1]==1:return (x[0],1,ranks[(x[0],-x[2],x[3])])
            return (x[0],2,0)
        trace=[x[4] for x in sorted(events,key=event_key)]
        lexical=[q['atom'] for q in tokens if q['emitted']]
        assert [x for x in trace if not x.startswith(('OPEN:','CLOSE:'))]==lexical
        out.append(dict(id=r['id'],text=r['text'],tokens=tokens,intervals=intervals,lexical=lexical,trace=trace))
    assert len(out)==38 and sum(len(r['tokens']) for r in out)==1217
    return dict(schema='GDT904_COMPLETE_LITERAL_INTERVAL_SOURCE_V1',source_bindings={str((S/n).relative_to(ROOT)):sha(S/n) for n in ['SOURCE_TYPED_A.json','SOURCE_TYPED_M.json','COMPILER_RECONCILIATION_M.json','FULL_TRACE_CONTRACT_REVIEW.json']},
                records=out,totals=dict(totals),lexical_atoms=len(all_atoms),
                claim_ceiling='Complete declared literal projection, not a full dependency parse or executed recipe. Scope markers are model syntax, not observed source words.')

if __name__=='__main__':
    result=compile_source(); (E/'artifacts/SOURCE.json').write_text(enc(result))
    print(enc(dict(records=len(result['records']),lexical_atoms=result['lexical_atoms'],totals=result['totals'],lengths={r['id']:len(r['lexical']) for r in result['records']})))
