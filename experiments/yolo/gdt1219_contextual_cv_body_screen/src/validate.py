"""Separate full replay; imports no runner or codec. Same author, not blinded."""
from pathlib import Path
from collections import Counter
from fractions import Fraction
import hashlib
import json
import math
import re

D=Path(__file__).resolve().parents[1]
R=D.parents[2]
A=D/'artifacts'
VS='aeiouy'
CS='bcdfghjklmnpqrstvwxz'
DIRECT=dict(zip('bcdfghklmnpqrstvxz',range(18)))
DIRECT['@']=18
ALL=['',*VS]
TOKEN=re.compile(r'[bcdfghjklmnpqrstvwxz][aeiouy]?|[aeiouy]|.',re.DOTALL)


def sha(b): return hashlib.sha256(b).hexdigest()
def sequence_hash(x): return sha(json.dumps(x,ensure_ascii=False,separators=(',',':')).encode())


def units(w):
    for item in TOKEN.findall(w):
        if item[0] in CS:
            yield item[0],item[1:]
        elif item in VS:
            yield '@',item
        else:
            yield '#',item


def fit(source):
    bins={(s,b):Counter() for s in VS for b in [*CS,'@']}
    for book in ('b4','w1'):
        for recipe in source[book]:
            memory='a'
            for w in recipe['words']:
                for b,v in units(w):
                    if b!='#':
                        bins[memory,b][v]+=1
                        memory=v or memory
    table={s:{} for s in VS};counts={s:{} for s in VS}
    for (s,b),ct in bins.items():
        options=ALL[1:] if b=='@' else ALL
        table[s][b]=min(options,key=lambda x:(-ct[x],ALL.index(x)))
        counts[s][b]=dict(ct)
    return table,counts


def forward(words,table,extras,start='a'):
    memory=start;groups=[]
    for w in words:
        assert w
        g=[]
        for b,v in units(w):
            if b=='#':
                n=extras.index(v);g += [19,1,3,n//19,n%19]
            else:
                default=table[memory][b]
                order=[default]+[c for c in ALL if c!=default]
                code=order.index(v)
                mark=[] if code==0 else [20 if code<=3 else 21]*((code-1)%3+1)
                if b in ('j','w'):
                    base=[19,1,0 if b=='j' else 2]
                else:
                    base=[DIRECT[b]]
                if b=='@' and not g and mark:
                    base=[]
                g += base+mark
                memory=v or memory
        assert g;groups.append(g)
    return groups


def backward(groups,table,extras,start='a'):
    inv={v:k for k,v in DIRECT.items()}
    memory=start;words=[]
    for g in groups:
        if not g or any(type(n)!=int or not 0<=n<22 for n in g):
            raise ValueError('glyph/group')
        w='';p=0
        while p<len(g):
            x=g[p]
            if p==0 and x>=20:
                b='@'
            elif x==19:
                if p+2>=len(g) or g[p+1]!=1:
                    raise ValueError('q guard')
                tag=g[p+2]
                if tag==3:
                    if p+4>=len(g) or not all(0<=n<19 for n in g[p+3:p+5]):
                        raise ValueError('literal digits')
                    n=19*g[p+3]+g[p+4]
                    if n>=len(extras): raise ValueError('literal range')
                    w+=extras[n];p+=5;continue
                if tag not in (0,2): raise ValueError('body escape')
                b='j' if tag==0 else 'w';p+=3
            else:
                if x not in inv: raise ValueError('body')
                b=inv[x];p+=1
            run=[]
            while p<len(g) and g[p]>=20:
                run.append(g[p]);p+=1
            if len(run)>3 or len(set(run))>1:
                raise ValueError('modifier')
            code=0 if not run else len(run)+(3 if run[0]==21 else 0)
            default=table[memory][b]
            value=([default]+[v for v in ALL if v!=default])[code]
            if b=='@' and not value: raise ValueError('empty carrier')
            w+=('' if b=='@' else b)+value
            memory=value or memory
        words.append(w)
    if forward(words,table,extras,start)!=groups:
        raise ValueError('noncanonical')
    return words


def moments(lengths):
    n=sum(lengths.values())
    avg=Fraction(sum(int(k)*v for k,v in lengths.items()),n)
    variance=Fraction(sum(int(k)**2*v for k,v in lengths.items()),n)-avg**2
    return avg,variance


def main():
    lock=json.loads((A/'REGISTRATION_LOCK.json').read_text())
    for p,h in lock['files'].items(): assert sha((R/p).read_bytes())==h,p
    contract=json.loads((R/'research_registry/proposals/production_origin_supply_20261003/HAND_WRITER_CONTEXT_CV_CONTRACT_20261006.json').read_text())
    extras=contract['input']['additional_characters']
    assert len(extras)==56 and len(set(extras))==56
    source=json.loads((R/'experiments/yolo/gdt1177_preposition_binding_transfer/artifacts/SOURCE_TEXTS.json').read_text())
    targets=json.loads((R/'experiments/yolo/gdt1174_ten_scribes_forward_comparison/artifacts/RESULT.json').read_text())['targets']
    result=json.loads((A/'RESULT.json').read_text())
    recorded=json.loads((A/'RECIPE_RECEIPTS.json').read_text())
    saved_table=json.loads((A/'DEFAULT_TABLE.json').read_text())
    table,counts=fit(source)
    assert table==saved_table['table'] and counts==saved_table['event_counts']
    assert saved_table['rows']==126 and saved_table['trained_books']==['b4','w1']
    fallback={s:{b:('a' if b=='@' else '') for b in [*CS,'@']} for s in VS}
    expected=[[7,20,20,4,20,20],[7,20,20,4,20,20],[13,20,7,17,19,1,3,0,14]]
    assert forward(['lege','lege','salz.'],fallback,extras)==expected
    assert backward(expected,fallback,extras)==['lege','lege','salz.']
    cases=[*'abcdefghijklmnopqrstuvwxyz',*extras,'nara','aei','aa','bb','jawa','a7a',
           'xylophon','bcdfghjklmnpqrstvwxz','überÄ.','abcdefghijklmnopqrstuvwxyz'*4]
    fixtures=0
    for tab in (table,fallback):
        for s in VS:
            for w in cases:
                g=forward([w,w,w],tab,extras,s)
                assert backward(g,tab,extras,s)==[w,w,w] and g[1]==g[2]
                fixtures+=1
    bad=[[],[19],[19,0],[19,1],[19,1,5],[19,1,3,18,18],[0,20,21],
         [0,20,20,20,20],[18,20],[18,20,20],[19,1,3,0],[22]]
    for g in bad:
        try: backward([g],fallback,extras)
        except ValueError: pass
        else: raise AssertionError('bad group accepted')
    receipts=[];decision=[];checks_done=0
    for book in ('b4','w1','bs1','gr1'):
        sample=[];remaining=8000
        for recipe in source[book]:
            g=forward(recipe['words'],table,extras)
            assert backward(g,table,extras)==recipe['words']
            receipts.append(dict(book=book,id=recipe['id'],words=len(g),
                source_characters=sum(len(w) for w in recipe['words']),
                written_signs=sum(len(w) for w in g),encoded_sha256=sequence_hash(g)))
            if remaining:
                part=g[:remaining];sample.append(part);remaining-=len(part)
        assert remaining==0
        flat=[tuple(g) for line in sample for g in line]
        c=Counter(flat);lengths=Counter(map(len,flat));mu,var=moments(lengths)
        pairs=sum(max(0,len(seg)-1) for seg in sample)
        repeats=sum(seg[i]==seg[i-1] for seg in sample for i in range(1,len(seg)))
        top=sum(sorted(c.values(),reverse=True)[:10])
        m=dict(tokens=len(flat),types=len(c),type_ratio=len(c)/8000,top10_count=top,top10_share=top/8000,
            adjacent_pairs=pairs,exact_repeat_count=repeats,exact_repeat=repeats/pairs,
            mean_length=float(mu),sd_length=math.sqrt(var),
            length_counts={str(k):v for k,v in sorted(lengths.items())},
            frequency_counts={str(k):v for k,v in sorted(Counter(c.values()).items())},
            sample_sequence_hash=sequence_hash(sample))
        assert m==result['books'][book]['metrics']
        book_pass=[]
        for ed,t in targets.items():
            tm,tv=moments(t['length_counts'])
            tr=round(t['exact_repeat']*t['adjacent_pairs']);tt=round(t['top10_share']*8000)
            checks=dict(type_ratio=abs(len(c)-t['types'])<=400,top10_share=abs(top-tt)<=400,
                exact_repeat=abs(Fraction(repeats,pairs)-Fraction(tr,t['adjacent_pairs']))<=Fraction(1,100),
                mean_length=4*tm<=5*mu<=6*tm,
                sd_length=9*tv<=16*var<=25*tv)
            passed=all(checks.values());book_pass.append(passed)
            assert dict(checks=checks,passed=passed)==result['books'][book]['reader_conditions'][ed]
            checks_done+=len(checks)
        assert all(book_pass)==result['books'][book]['passed'];decision.extend(book_pass)
    assert receipts==recorded and len(receipts)==1054
    assert sum(r['words'] for r in receipts)==result['complete_source_words']==80931
    assert sum(r['source_characters'] for r in receipts)==result['source_characters']
    assert sum(r['written_signs'] for r in receipts)==result['emitted_working_signs']
    assert result['complete_recipe_roundtrips']==1054 and result['all_books_pass']==all(decision)
    assert result['status']==('CONTEXT_CV_NECESSARY_SCREEN_PASS' if all(decision) else 'CONTEXT_CV_NECESSARY_SCREEN_FAIL')
    run=json.loads((A/'RUN_RECEIPT.json').read_text())
    assert run['fixtures']==dict(roundtrip_fixtures=fixtures,bad_groups=len(bad),manual_example=expected)
    receipt=dict(status='PASS',experiment='GDT1219',default_cells=126,recipe_inverses=1054,
        source_words=80931,necessary_conditions=checks_done,fixture_roundtrips=fixtures,
        invalid_groups_rejected=len(bad),same_author=True,imports_runner_or_writer=False,
        independent_holdout=False,native_values=0,scientific_status=result['status'])
    (A/'VALIDATION.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))


if __name__=='__main__': main()
