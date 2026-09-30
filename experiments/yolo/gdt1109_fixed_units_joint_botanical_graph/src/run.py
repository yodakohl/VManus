#!/usr/bin/env python3
"""Fixed605 carrier adapter and complete13-role enumeration; no new parser."""
import csv,gzip,hashlib,io,itertools,json,re,sys,multiprocessing,time
from collections import defaultdict,Counter
from pathlib import Path
from graph import search
BASE=Path(__file__).resolve().parents[1];ROOT=BASE.parents[2]
sys.path.insert(0,str(ROOT/'experiments/yolo/gdt605_multisymbol_unit_alphabet/src'))
from separator_crossing import collapse,apply_bpe
SOURCE=ROOT/'experiments/yolo/gdt1106_frozen_domain_transfer/artifacts/SOURCE.tsv.gz'
MERGES=ROOT/'experiments/yolo/gdt605_multisymbol_unit_alphabet/artifacts/gdt605_bpe_merges.tsv'
def check_lock():
    for path,digest in json.loads((BASE/'PREREG_LOCK.json').read_text())['sha256'].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest,path

def source_pages():
    merges=[(r['left'],r['right'],r['merged'],int(r['train_occurrences'])) for r in csv.DictReader(MERGES.open(),delimiter='\t')]
    assert len(merges)==64
    lines=defaultdict(list)
    for r in csv.DictReader(io.StringIO(gzip.decompress(SOURCE.read_bytes()).decode()),delimiter='\t'):
        if r['section']!='H':continue
        assert r['kind']=='P' and not r['page'].startswith('f84') and r['page']!='f116v'
        lines[(r['edition'],r['page'],r['locus'])].append(r)
    pages=defaultdict(list)
    for (edition,page,locus),rows in sorted(lines.items()):
        assert [int(r['source_group_index']) for r in rows]==list(range(1,len(rows)+1))
        assert all(int(r['source_group_count'])==len(rows) for r in rows)
        chunks=[];pending=[]
        for row in rows:
            pending.append(row)
            if row['right_separator']=='UNCERTAIN_SMALL_SPACE':continue
            pure=all(re.fullmatch('[a-z]+',r['ivtff_group_raw']) for r in pending)
            raw=''.join(r['ivtff_group_raw'] for r in pending)
            units=list(apply_bpe(collapse(raw),merges)) if pure else None
            if units is not None:assert ''.join(units)==collapse(raw)
            chunks.append({'ids':[r['source_group_id'] for r in pending],'raw_groups':[r['ivtff_group_raw'] for r in pending],
                'start_index':int(pending[0]['source_group_index']),'end_index':int(pending[-1]['source_group_index']),
                'units':units,'source_rows':pending})
            pending=[]
        assert not pending
        pages[(edition,page)].append({'locus':locus,'chunks':chunks,'source_group_count':len(rows)})
    assert len(pages)==357 and sum(l['source_group_count'] for v in pages.values() for l in v)==32000
    return pages

def worker(task):
    edition,page,lines,spec=task
    out=search(lines,spec)
    case={'edition':edition,'page':page,'physical_leaf':page.split('r')[0].split('v')[0],
        'source_groups':sum(l['source_group_count'] for l in lines),'full_lines':len(lines),
        'hard_chunks':sum(len(l['chunks']) for l in lines),
        'unknown_chunks':sum(c['units'] is None for l in lines for c in l['chunks']),
        'three_unit_carriers':out['literal_triples'],'five_unit_carriers':out['literal_fives'],
        'stage_counts':out['stage_counts'],'full_bindings':len(out['solutions'])}
    return case,[{'edition':edition,'page':page,**s} for s in out['solutions']]

def main():
    check_lock();pages=source_pages();spec=json.loads((BASE/'src/MODEL.json').read_text())
    carriers=[{'edition':ed,'page':page,'lines':ls} for (ed,page),ls in sorted(pages.items())]
    (BASE/'artifacts/CARRIERS.json.gz').write_bytes(gzip.compress(json.dumps(carriers,sort_keys=True).encode(),mtime=0))
    cases=[];witnesses=[];start=time.monotonic()
    with multiprocessing.Pool(8) as pool:
        for case,found in pool.imap(worker,[(ed,page,ls,spec) for (ed,page),ls in sorted(pages.items())]):
            cases.append(case);witnesses.extend(found)
            if len(cases)%100==0:print('complete cases',len(cases),'full codes',len(witnesses),flush=True)
            if time.monotonic()-start>180:
                raise RuntimeError('Runtime cap reached; enumeration INCOMPLETE, no absence/selection claim')
    assert len(cases)==357
    (BASE/'artifacts/CASES.json').write_text(json.dumps(cases,indent=2)+'\n')
    (BASE/'artifacts/WITNESSES.json.gz').write_bytes(gzip.compress(json.dumps(witnesses,sort_keys=True).encode(),mtime=0))
    columns=['candidate','edition','page','comparison_orientation','induce_orientation','use_orientation',*spec['atom_roles']]
    with (BASE/'artifacts/CANDIDATE_TABLE.tsv').open('w') as f:
        w=csv.DictWriter(f,columns,delimiter='\t',lineterminator='\n');w.writeheader()
        for i,s in enumerate(witnesses):w.writerow({'candidate':i,'edition':s['edition'],'page':s['page'],**{k:s[k] for k in columns[3:6]},**s['values']})
    counts=Counter((s['comparison_orientation'],s['induce_orientation'],s['use_orientation']) for s in witnesses)
    with (BASE/'artifacts/CONTRACT_TABLE.tsv').open('w') as f:
        f.write('comparison\tinduce\tuse\tfull_bindings\n')
        for c,i,u in itertools.product(range(6),range(6),range(120)):f.write(f'{c}\t{i}\t{u}\t{counts[c,i,u]}\n')
    result={'status':'C0_UNIT_GRAPH_BINDINGS_RETAINED' if witnesses else 'NO_FIXED_COMPLETE_CHUNK_UNIT_GRAPH',
        'all_page_reader_cases':len(cases),'source_groups':32000,'contracts':4320,'full_bindings':len(witnesses),
        'hard_chunks':sum(c['hard_chunks'] for c in cases),'unknown_chunks':sum(c['unknown_chunks'] for c in cases),
        'three_unit_carriers':sum(c['three_unit_carriers'] for c in cases),'five_unit_carriers':sum(c['five_unit_carriers'] for c in cases),
        'stage_counts':{k:sum(c['stage_counts'].get(k,0) for c in cases) for k in ('induce_forks','linked_use_forks','head_leaf_comparison_links')},
        'confirmed_words':0,'independent_meaning_confirmation_leaves':0,'significance':None,'reserved_pages_opened':[],
        'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'ceiling':'C0 role code in final-unit complete chunks, not decoded lexemes or semantic morphemes'}
    (BASE/'artifacts/RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
if __name__=='__main__':main()
