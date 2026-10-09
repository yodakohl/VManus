"""One fixed finite subject/predicate writer; no partition or key search."""
from pathlib import Path
from collections import Counter
from datetime import datetime,timezone
import hashlib,json,sys
D=Path(__file__).resolve().parents[1];R=D.parents[2];A=D/'artifacts'
BASE=R/'experiments/yolo/gdt1174_ten_scribes_forward_comparison'
sys.path.insert(0,str(BASE/'src'))
import scribes as s
import metrics as m


def digest(x): return hashlib.sha256(json.dumps(x,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
def save(n,x): (A/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def addresses(r):
    op,plant,part,state,medium,amount,duration=r
    return [plant*64+part*8+state,op*128+medium*16+amount*4+duration]
def recover(a,b):
    assert 0<=a<4096 and 0<=b<1024
    return [b//128,a//64,(a%64)//8,a%8,(b%128)//16,(b%16)//4,b%4]
def wrap(words):
    out=[];line=[];length=0
    for word in words:
        size=len(m.glyphs(word))
        if line and length+1+size>48:
            out.append(line);line=[];length=0
        length+=size+bool(line);line.append(word)
    if line: out.append(line)
    return out

def extra_checks(model,target):
    rules={'edit1_repeat':.01,'q_followed_o':.03,'q_count':.25*target['q_count'],
           'y_final':.05,'glyph_entropy':.15,'word_entropy':.30}
    return {k:dict(model=model[k],target=target[k],limit=lim,
        within=(model[k] is not None and target[k] is not None and abs(model[k]-target[k])<=lim))
        for k,lim in rules.items()}

def main():
    for p,h in json.loads((A/'REGISTRATION_LOCK.json').read_text())['files'].items():
        assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
    source=json.loads((BASE/'artifacts/SOURCE_MESSAGES.json').read_text())
    target=json.loads((BASE/'artifacts/RESULT.json').read_text())['targets']
    assert len(source)==256 and all(len(p)==20 for p in source)
    assert len(s.ROOTS)==len(s.ROOT_INV)==4096
    assert all(s.ROOT_INV[s.ROOTS[i]]==i for i in range(4096))
    for n in range(4096): assert addresses(recover(n,0))[0]==n
    for n in range(1024): assert addresses(recover(0,n))[1]==n
    teaching=[[3,0,0,1,1,0,2],[3,0,0,1,1,1,2],[3,1,0,1,1,1,2],[3,1,0,1,1,1,2]]
    assert [addresses(r) for r in teaching]==[[1,402],[1,406],[65,406],[65,406]]
    pages=[];receipts=[];all_lines=[]
    for no,page in enumerate(source):
        indexes=[n for record in page for n in addresses(record)]
        words=[s.ROOTS[n] for n in indexes]
        lines=wrap(words)
        read=[s.ROOT_INV[w] for line in lines for w in line]
        assert [recover(a,b) for a,b in zip(read[::2],read[1::2])]==page
        pages.append(indexes);all_lines+=lines
        receipts.append(dict(paragraph=no,records=len(page),groups=len(indexes),lines=len(lines),
            address_hash=digest(indexes),surface_hash=digest(words),line_hash=digest(lines)))
    sample=[n for page in pages for n in page][:8000]
    counts=Counter(sample);types=len(counts);top=sum(sorted(counts.values(),reverse=True)[:10])
    necessary={ed:dict(types=abs(types-t['types'])<=400,
        top10=abs(top-round(8000*t['top10_share']))<=400) for ed,t in target.items()}
    first_pass=all(all(c.values()) for c in necessary.values())
    result=dict(experiment='GDT1220',stage1_pass=first_pass,types=types,top10_count=top,
        type_ratio=types/8000,top10_share=top/8000,necessary_checks=necessary,
        full_source_records=5120,full_source_paragraphs=256,full_output_groups=10240,
        sample_groups=8000,sample_paragraphs=200,full_stage='NOT_RUN_NECESSARY_FAILURE',
        status='MATERIAL_PREDICATE_FREQUENCY_FAIL',native_meanings=0,independent_confirmation=0)
    if first_pass:
        model=m.measure(all_lines)
        comparisons={ed:m.compare(model,t) for ed,t in target.items()}
        extra={ed:extra_checks(model,t) for ed,t in target.items()}
        all_pass=all(c['joint_screen'] for c in comparisons.values()) and all(
            c['within'] for rows in extra.values() for c in rows.values())
        result.update(full_stage='EXECUTED',metrics=model,base_checks=comparisons,
            strengthened_checks=extra,full_pass=all_pass,
            status='MATERIAL_PREDICATE_FULL_SCREEN_PASS' if all_pass else 'MATERIAL_PREDICATE_FULL_SCREEN_FAIL')
    save('RESULT.json',result);save('FREQUENCIES.json',dict(sorted(counts.items())))
    save('PARAGRAPH_RECEIPTS.json',receipts)
    save('RUN_RECEIPT.json',dict(completed_utc=datetime.now(timezone.utc).isoformat(),
        material_inverse_values=4096,predicate_inverse_values=1024,
        manual_addresses=[addresses(r) for r in teaching],sample_address_hash=digest(sample)))
    summary={k:v for k,v in result.items() if k not in ('base_checks','strengthened_checks','metrics')}
    if first_pass:
        summary['metrics']={k:v for k,v in result['metrics'].items() if k not in ('glyph_counts','length_counts')}
        summary['failed_full_checks']={ed:[k for k,v in result['base_checks'][ed]['diagnostics'].items() if not v['within']]+['strong_'+k for k,v in result['strengthened_checks'][ed].items() if not v['within']] for ed in target}
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=='__main__': main()
