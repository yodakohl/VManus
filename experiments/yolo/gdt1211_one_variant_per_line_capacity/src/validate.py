#!/usr/bin/env python3
"""Separate source/target reconstruction and finite replacement-bound checks."""
from pathlib import Path
import csv, hashlib, io, itertools, json, random, re, subprocess
E=Path(__file__).resolve().parents[1]; ROOT=E.parents[2]; A=E/'artifacts'

def counts(xs):
    out={}
    for x in xs: out[x]=out.get(x,0)+1
    return out

def main():
    lock=json.loads((A/'REGISTRATION_LOCK.json').read_text())
    for rel,h in lock['files'].items(): assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==h,rel
    result=json.loads((A/'RESULT.json').read_text()); ids=json.loads((A/'TARGET_SAMPLE_IDS.json').read_text())
    receipt=json.loads((A/'RUN_RECEIPT.json').read_text())
    spec=json.loads((ROOT/'experiments/yolo/gdt1170_repetition_context_neutral_copy/src/SPEC.json').read_text())
    expected=['./vmanus-exp','query-tsv','experiments/yolo/gdt1170_repetition_context_neutral_copy/artifacts/GUARDED.tsv','--selector','page']
    for page in spec['allowed']: expected+=['--allow',page]
    expected+=['--columns','edition,page,locus,kind,source_group_index,source_group_count,ivtff_group_raw,left_separator,right_separator']
    assert receipt['guard_command']==expected
    call=subprocess.run(expected,cwd=ROOT,text=True,capture_output=True,check=True)
    assert hashlib.sha256(call.stdout.encode()).hexdigest()==receipt['guard_projection_sha256']
    rowmap={}; pages=set(); pattern=re.compile(r'(?:ckh|cth|cph|cfh|ch|sh|[aoeindqysrlmktpf])+')
    for r in csv.DictReader(io.StringIO(call.stdout),delimiter='\t'):
        if r['kind']!='P':continue
        pages.add(r['page'])
        ident=r['edition']+'|'+r['locus']+'|G'+r['source_group_index'].zfill(3)
        assert ident not in rowmap; rowmap[ident]=r
    order=sorted(pages);random.Random(1174).shuffle(order);rank={p:i for i,p in enumerate(order)}
    targets=json.loads((ROOT/'experiments/yolo/gdt1174_ten_scribes_forward_comparison/artifacts/RESULT.json').read_text())['targets']
    for ed in ('IT2a','RF1b','ZL3b'):
        accepted=[]
        for ident,r in rowmap.items():
            if r['edition']!=ed:continue
            if r['left_separator'] not in ('LINE_START','DEFINITE_SPACE') or r['right_separator'] not in ('LINE_END','DEFINITE_SPACE'):continue
            if pattern.fullmatch(r['ivtff_group_raw']): accepted.append((rank[r['page']],r['locus'],int(r['source_group_index']),ident))
        chosen=[t[3] for t in sorted(accepted)[:8000]]
        assert chosen==ids[ed] and len(set(chosen))==8000
        words=counts(rowmap[i]['ivtff_group_raw'] for i in chosen)
        linecounts=counts((rowmap[i]['page'],rowmap[i]['locus']) for i in chosen)
        t=result['native'][ed];old=targets[ed]
        assert len(words)==t['types']==old['types']
        assert sum(sorted(words.values(),reverse=True)[:10])==t['top10_count']==round(old['top10_share']*8000)
        assert len(linecounts)==t['touched_lines']
        assert t['line_membership']==[{'page':p,'locus':l,'sample_groups':v} for (p,l),v in sorted(linecounts.items())]
        assert t['type_min']==old['types']-400 and t['top10_max']==round(old['top10_share']*8000)+400
    source=json.loads((ROOT/'experiments/yolo/gdt1177_preposition_binding_transfer/artifacts/SOURCE_TEXTS.json').read_text())
    oldfreq=json.loads((ROOT/'experiments/yolo/gdt1202_whole_word_two_alias_capacity/artifacts/FREQUENCIES.json').read_text())
    cases=0; passed=True
    for book in ('b4','w1','bs1','gr1'):
        sample=[]
        for recipe in source[book]:
            for word in recipe['words']:
                if len(sample)<8000:sample.append(word)
        assert len(sample)==8000
        f=counts(sample);assert f=={r['word']:r['count'] for r in oldfreq[book]}
        d=len(f);s=sum(sorted(f.values(),reverse=True)[:10]);out=result['books'][book]
        assert out['source_types']==d and out['source_top10_count']==s
        for ed,t in result['native'].items():
            k=t['touched_lines'];c=out['conditions'][ed]
            assert c['K_max']==k and c['types_upper']==min(8000,d+k) and c['top10_lower']==max(0,s-k)
            assert c['K_necessary_lower']==max(0,t['type_min']-d,s-t['top10_max'])
            expected_type=d+k>=t['type_min'];expected_top=s-k<=t['top10_max']
            assert c['types_capacity']==expected_type and c['top10_capacity']==expected_top
            assert c['not_excluded']==(expected_type and expected_top)
            passed=passed and c['not_excluded'];cases+=1
    assert result['all_cases_not_excluded']==passed
    assert result['status']==('ONE_VARIANT_PER_LINE_NOT_EXCLUDED' if passed else 'ONE_VARIANT_PER_LINE_CAPACITY_EXCLUDED')
    # Every replacement pattern, including collisions/deleted old types and
    # fresh output types, for length1..5. Top-m is the same proof as top-ten.
    finite=0
    for n in range(1,6):
        for original in itertools.product(range(2),repeat=n):
            before=counts(original);b=sorted(before.values(),reverse=True)
            for output in itertools.product(range(4),repeat=n):
                after=counts(output);a=sorted(after.values(),reverse=True)
                k=sum(x!=y for x,y in zip(original,output))
                assert len(after)<=min(n,len(before)+k)
                for m in (1,2,3):assert sum(a[:m])>=max(0,sum(b[:m])-k)
                finite+=1
    validation={'status':'PASS','book_reader_cases':cases,'separate_target_parser':'full regex over exactly22fixed working signs; IDs/order and historical counts replayed','source_counts':'independent1177 recipe-token iteration equals every1202frequency entry','finite_replacement_examples':finite,'native_independent_confirmation':False,'scope':'Provenance, selection, arithmetic and finite bound checks; no width, causal or semantic validation.'}
    (A/'VALIDATION.json').write_text(json.dumps(validation,indent=2)+'\n');print(json.dumps(validation))
if __name__=='__main__':main()
