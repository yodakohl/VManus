from pathlib import Path
import csv,hashlib,io,json,re,subprocess
P=Path(__file__).resolve().parent;R=P.parents[2]
def main():
    contract=json.loads((P/'PAIR_WEAVE_HAND_CONTRACT_20261011.json').read_text())
    source=json.loads((P/'PAIR_WEAVE_HAND_SOURCE_20261011.json').read_text());result=json.loads((P/'PAIR_WEAVE_HAND_RESULT_20261011.json').read_text())
    assert hashlib.sha256((R/contract['scope']['source']).read_bytes()).hexdigest()==contract['scope']['source_sha256']
    assert hashlib.sha256((P/'PAIR_WEAVE_HAND_SOURCE_20261011.json').read_bytes()).hexdigest()==result['source_sha256']
    cols=['source_group_id','edition','page','locus','kind','source_row_index','source_group_index','source_group_count','paragraph_start','paragraph_end','left_separator','right_separator','ivtff_group_raw']
    command=['./vmanus-exp','query-tsv',contract['scope']['source'],'--selector','locus']
    for loc in contract['scope']['selectors']:command+=['--allow',loc]
    command+=['--columns',','.join(cols)]
    queried=subprocess.run(command,cwd=R,text=True,capture_output=True,check=True)
    rows=list(csv.DictReader(io.StringIO(queried.stdout),delimiter='\t'));assert rows==source['rows']
    token=re.compile('ckh|cth|cph|cfh|ch|sh|[aoeindqysrlmktpf]')
    def parse(x):
        y=token.findall(x);return y if ''.join(y)==x else None
    def positions(m,n):
        k=min(m,n)
        return [2*i if i<k else i+k for i in range(m)],[2*i+1 if i<k else i+k for i in range(n)]
    def inverse(a,b):
        z=a+b;ix,iy=positions(len(a),len(b));assert sorted(ix+iy)==list(range(len(z)))
        return [[z[i] for i in ix],[z[i] for i in iy]]
    paired=0
    for ed,out in result['paragraph'].items():
        block=sorted([r for r in rows if r['edition']==ed and r['locus'] in ['f103r.43','f103r.44']],key=lambda r:(int(r['source_row_index']),int(r['source_group_index'])))
        assert len(block)==out['raw_groups']==16
        for loc in ['f103r.43','f103r.44']:
            line=[r for r in block if r['locus']==loc];assert [int(r['source_group_index']) for r in line]==list(range(1,int(line[0]['source_group_count'])+1))
        assert all(r['kind']=='P' for r in block)
        boundary=(block[0]['paragraph_start']=='1' and block[-1]['paragraph_end']=='1' and all(r['paragraph_end']=='0' for r in block if r['locus']=='f103r.43') and all(r['paragraph_start']=='0' for r in block if r['locus']=='f103r.44'))
        literal=all(parse(r['ivtff_group_raw']) is not None for r in block)
        clear=all(r[k] in ('DEFINITE_SPACE','LINE_START','LINE_END') for r in block for k in ('left_separator','right_separator'))
        if not (boundary and literal and clear):
            assert out['status']=='UNSCORABLE_NO_REPAIR' and out['pairs']==[];continue
        assert out['status']=='SYMBOLIC_INVERSE_ONLY' and len(out['pairs'])==8 and out['odd_final_literal'] is None
        for i,pair in enumerate(out['pairs']):
            rr=block[2*i:2*i+2];a,b=[parse(r['ivtff_group_raw']) for r in rr]
            assert pair['output_ids']==[r['source_group_id'] for r in rr]
            assert pair['output_raw']==[r['ivtff_group_raw'] for r in rr]
            assert pair['output_units']==[a,b] and pair['lengths']==[len(a),len(b)]
            assert pair['pre_key_source_units']==inverse(a,b);paired+=1
    for ed,items in result['old_triple_obligations'].items():
        assert len(items)==1
        for t in items:
            rr=[next(r for r in rows if r['source_group_id']==ident) for ident in t['ids']]
            assert all(r['edition']==ed and r['locus']=='f79v.19' and r['ivtff_group_raw']=='qokedy' for r in rr)
            assert [int(r['source_group_index']) for r in rr]==list(range(int(rr[0]['source_group_index']),int(rr[0]['source_group_index'])+3))
            assert all(r[k]=='DEFINITE_SPACE' for r in rr for k in ['left_separator','right_separator'])
            x=parse('qokedy');answer=inverse(x,x)
            assert t['working_units']==x and t['either_phase_pre_key_source_pair']==answer
            assert answer==[list('qkdqkd'),list('oeyoey')]
            assert t['phase_0_aligned_positions']==[0,1] and t['phase_1_aligned_positions']==[1,2]
    out={'status':'PASS','source_rows':len(rows),'paragraph_pair_records_checked':paired,'whole_paragraphs':'ZL3b/IT2a same16groups; one physical passage','RF1b':'UNSCORABLE_NO_REPAIR','triple':'one physical triple in three alternate readings; either parity forces two source squares','scope':'Source and reversible symbolic permutation only, not meaning, key recovery or evidence that this mechanism was used.'}
    (P/'PAIR_WEAVE_HAND_VALIDATION_20261011.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
