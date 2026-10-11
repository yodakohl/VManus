from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parent
CLEAR={'DEFINITE_SPACE','LINE_START','LINE_END'}
def encode_pair(u,v):
    k=min(len(u),len(v));z=[x for pair in zip(u[:k],v[:k]) for x in pair]+u[k:]+v[k:]
    return z[:len(u)],z[len(u):]
def decode_pair(a,b):
    m,n=len(a),len(b);k=min(m,n);z=a+b;u=z[:2*k:2];v=z[1:2*k:2]
    if m>n:u+=z[2*k:]
    elif n>m:v+=z[2*k:]
    return u,v

def main():
    contract=json.loads((P/'PAIR_WEAVE_HAND_CONTRACT_20261011.json').read_text())
    proposal=P/'PAIRED_WORD_INTERLEAVING_LENGTH_CHANNEL_RAW_20261011.json'
    assert hashlib.sha256(proposal.read_bytes()).hexdigest()==contract['proposal_sha256']
    signs=json.loads(proposal.read_text())['design']['working_inventory'];order=sorted(signs,key=lambda x:(-len(x),x))
    def units(raw):
        out=[];i=0
        while i<len(raw):
            token=next((x for x in order if raw.startswith(x,i)),None)
            if token is None:return None
            out.append(token);i+=len(token)
        return out
    source=json.loads((P/'PAIR_WEAVE_HAND_SOURCE_20261011.json').read_text());rows=source['rows']
    assert {r['locus'] for r in rows}==set(contract['scope']['selectors'])
    assert all(r['kind']=='P' and not r['page'].startswith('f84') for r in rows)
    results={};triples={}
    for ed in contract['scope']['editions']:
        block=[r for r in rows if r['edition']==ed and r['locus'].startswith('f103r.')]
        block.sort(key=lambda r:(int(r['source_row_index']),int(r['source_group_index'])))
        errors=[]
        for locus in ['f103r.43','f103r.44']:
            rr=[r for r in block if r['locus']==locus]
            if not rr or [int(r['source_group_index']) for r in rr]!=list(range(1,int(rr[0]['source_group_count'])+1)):errors.append('incomplete_'+locus)
        if not block or block[0]['paragraph_start']!='1' or block[-1]['paragraph_end']!='1':errors.append('paragraph_boundary_unverified')
        if any(r['paragraph_end']!='0' for r in block if r['locus']=='f103r.43') or any(r['paragraph_start']!='0' for r in block if r['locus']=='f103r.44'):errors.append('internal_boundary_flags')
        parsed=[units(r['ivtff_group_raw']) for r in block]
        if any(x is None for x in parsed):errors.append('nonliteral_working_unit_parse')
        if any(r['left_separator'] not in CLEAR or r['right_separator'] not in CLEAR for r in block):errors.append('uncertain_group_boundary')
        pairs=[]
        if not errors:
            for i in range(0,len(block)-1,2):
                a,b=parsed[i:i+2];u,v=decode_pair(a,b);assert encode_pair(u,v)==(a,b)
                pairs.append({'output_ids':[r['source_group_id'] for r in block[i:i+2]],'output_raw':[r['ivtff_group_raw'] for r in block[i:i+2]],'output_units':[a,b],'pre_key_source_units':[u,v],'lengths':[len(a),len(b)]})
        results[ed]={'status':'SYMBOLIC_INVERSE_ONLY' if not errors else 'UNSCORABLE_NO_REPAIR','errors':errors,'raw_groups':len(block),'pairs':pairs,'odd_final_literal':parsed[-1] if not errors and len(block)%2 else None}
        line=sorted([r for r in rows if r['edition']==ed and r['locus']=='f79v.19'],key=lambda r:int(r['source_group_index']))
        found=[]
        for j in range(len(line)-2):
            rr=line[j:j+3]
            if not all(r['ivtff_group_raw']=='qokedy' for r in rr):continue
            assert [int(r['source_group_index']) for r in rr]==list(range(int(rr[0]['source_group_index']),int(rr[0]['source_group_index'])+3))
            if not all(r['left_separator'] in CLEAR and r['right_separator'] in CLEAR for r in rr):continue
            assert rr[0]['right_separator']==rr[1]['left_separator']==rr[1]['right_separator']==rr[2]['left_separator']=='DEFINITE_SPACE'
            x=units('qokedy');u,v=decode_pair(x,x);assert u==u[:3]*2 and v==v[:3]*2
            found.append({'ids':[r['source_group_id'] for r in rr],'raw':['qokedy']*3,'working_units':x,'phase_0_aligned_positions':[0,1],'phase_1_aligned_positions':[1,2],'either_phase_pre_key_source_pair':[u,v],'premise':'No hidden source-paragraph boundary inside this same-line triple; neither RF nor other paragraph parity is inferred.'})
        triples[ed]=found
    assert encode_pair(list('ABC'),list('DEFG'))==(list('ADB'),list('ECFG'))
    out={'phase':'exploratory symbolic hand reconstruction; not empirical model support','source_sha256':hashlib.sha256((P/'PAIR_WEAVE_HAND_SOURCE_20261011.json').read_bytes()).hexdigest(),'paragraph':results,'old_triple_obligations':triples,'meaning':'All pre-key units are unknown source-symbol stand-ins. No original letters, words, language, fit or semantic values recovered.'}
    (P/'PAIR_WEAVE_HAND_RESULT_20261011.json').write_text(json.dumps(out,indent=2)+'\n')
    for ed,d in results.items():
        print(ed,d['status'],d['errors'])
        if ed=='ZL3b':
            for pair in d['pairs']:print(' | '.join(pair['output_raw']),' => ', ' | '.join(' '.join(u) for u in pair['pre_key_source_units']))
    print('triple witnesses',{ed:len(x) for ed,x in triples.items()})
if __name__=='__main__':main()
