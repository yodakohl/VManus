#!/usr/bin/env python3
"""GDT1084 fixed source-STA four-pair assignment test."""
import csv
import hashlib
import io
import itertools
import json
import math
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / 'experiments/yolo/gdt1084_source_native_four_plant_bridge'
CAP = ROOT / 'experiments/semantic_assumptions/results/public_repeated_plant_source_native_capacity.json'
GROUPS = ROOT / 'experiments/semantic_assumptions/results/source_sta_family_consensus_groups.tsv'
METHOD = BASE / 'METHOD.md'
READINGS = {'ZL3b':'zl_sta_codes','IT2a':'it_sta_codes','RF1b':'rf_sta_codes'}
PAGES = ['f48v','f18v','f23r','f19r']
COLUMNS = 'locus,page,section,grammar_scope,strict_zero_alternative,currier,hand,zl_sta_codes,it_sta_codes,rf_sta_codes'
EXPECTED_METHOD = 'e4841b845838bea7f6149af16ce683a694ea329a687284f892a4ee0e746c4ab9'
EXPECTED_CAP = 'a16700eafc88653c3b95f8fcd840a4c86a185ca240a0e19123e880a46373cb2e'
EXPECTED_GROUPS = 'a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def guarded_rows():
    command = ['./vmanus-exp','query-tsv',str(GROUPS.relative_to(ROOT)),
               '--selector','page']
    for page in PAGES:
        command += ['--allow',page]
    command += ['--columns',COLUMNS,'--forbid-prefix','f84']
    result = subprocess.run(command,cwd=ROOT,text=True,capture_output=True,check=True)
    rows = list(csv.DictReader(io.StringIO(result.stdout),delimiter='\t'))
    assert {r['page'] for r in rows} == set(PAGES)
    assert all(not r['page'].startswith('f84') for r in rows)
    return rows, result.stderr.strip()


def contains(seq,motif):
    return any(seq[i:i+len(motif)] == motif for i in range(len(seq)-len(motif)+1))


def main():
    assert sha(METHOD) == EXPECTED_METHOD
    assert sha(CAP) == EXPECTED_CAP
    assert sha(GROUPS) == EXPECTED_GROUPS
    cap = json.loads(CAP.read_text())
    rel = cap['relations']
    assert [(r['label_locus'],r['target_page']) for r in rel] == list(zip(['f89v2.6','f102r2.21','f102r2.22','f102v1.17'],PAGES))
    rows,guard = guarded_rows()
    prose = [r for r in rows if r['section']=='H' and r['grammar_scope']=='CONFIRMED_PROSE' and r['strict_zero_alternative']=='1']
    out = {'experiment':'GDT1084','method_sha256':sha(METHOD),'capacity_sha256':sha(CAP),
           'groups_sha256':sha(GROUPS),'guard':guard,'selected_rows':len(rows),
           'admissible_prose_groups':{p:sum(r['page']==p for r in prose) for p in PAGES},
           'labels':[r['label_locus'] for r in rel],'pages':PAGES,'readings':{}}
    all_pass = True
    for reading,column in READINGS.items():
        page_groups = {p:[(r['locus'],tuple(r[column].split())) for r in prose if r['page']==p] for p in PAGES}
        matrix = []
        for relation in rel:
            lid = relation['label_locus']
            motifs = cap['label_inventory'][lid]['readings'][reading]['motifs']
            line=[]
            for page in PAGES:
                hits=[]
                for item in motifs:
                    motif=tuple(item['motif'].split())
                    df=item['page_document_frequency']['A_hand1']
                    score=item['width']*math.log(93/(df+1))
                    for locus,seq in page_groups[page]:
                        if contains(seq,motif):
                            hits.append({'score':score,'motif':item['motif'],'width':item['width'],'df':df,'locus':locus})
                best = sorted(hits,key=lambda x:(-x['score'],x['motif'],x['locus']))[0] if hits else None
                line.append({'score':best['score'] if best else 0.0,'best':best,'hit_count':len(hits)})
            matrix.append(line)
        scores=[]
        for permutation in itertools.permutations(range(4)):
            scores.append({'assignment':list(permutation),'total':sum(matrix[i][permutation[i]]['score'] for i in range(4))})
        actual=scores[0]  # identity permutation is first
        assert actual['assignment']==[0,1,2,3]
        greater=sum(s['total']>actual['total']+1e-12 for s in scores)
        ties=sum(abs(s['total']-actual['total'])<=1e-12 for s in scores)
        p=(greater+ties)/24
        own=[matrix[i][i] for i in range(4)]
        positive=sum(cell['score']>0 and cell['best']['df']<92 for cell in own)
        passed=(greater==0 and ties==1 and positive>=3)
        three_scores=[]
        for permutation in itertools.permutations((1,2,3)):
            three_scores.append(sum(matrix[i][page_j]['score'] for i,page_j in enumerate(permutation,start=1)))
        observed_three=three_scores[0]
        three_p=sum(s>=observed_three-1e-12 for s in three_scores)/6
        all_pass &= passed
        out['readings'][reading]={'matrix':matrix,'assignments':sorted(scores,key=lambda s:(-s['total'],s['assignment'])),
            'observed_total':actual['total'],'greater':greater,'ties':ties,'one_sided_p':p,
            'positive_own_pairs':positive,'pass':passed,
            'three_explicit_owner_observed':observed_three,'three_explicit_owner_p_descriptive':three_p}
    out['decision']='FOUR_PAIR_FORMAL_SIGNAL' if all_pass else 'NO_FOUR_PAIR_FORMAL_SIGNAL'
    (BASE/'artifacts/RESULT.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
    lines=['# GDT1084 result','',f"Decision: **{out['decision']}**. The four source-described pairs were fixed before target-prose access in this pass.",'',
           f"Guarded rows: {len(rows)}; admissible Herbal prose groups: {out['admissible_prose_groups']}.",'']
    for reading,data in out['readings'].items():
        lines += [f"## {reading}",'',f"Observed score {data['observed_total']:.6f}; assignments greater/tied: {data['greater']}/{data['ties']}; exact within-four assignment p={data['one_sided_p']:.6f}; own-pair hits {data['positive_own_pairs']}/4; fixed gate {'PASS' if data['pass'] else 'FAIL'}. Three explicit-owner pairs only: descriptive p={data['three_explicit_owner_p_descriptive']:.6f}.",'',
                  '| label / page | '+ ' | '.join(PAGES)+' |','|---|'+'---:|'*4]
        for i,label in enumerate(out['labels']):
            cells=[]
            for j,page in enumerate(PAGES):
                cell=data['matrix'][i][j];best=cell['best']
                cells.append(f"{cell['score']:.3f}"+(f" `{best['motif']}` df={best['df']} at {best['locus']}" if i==j and best else ''))
            lines.append('| '+label+' | '+' | '.join(cells)+' |')
        lines += ['']
    lines += ['The f89v2.6 ownership is ambiguous; the four-page orbit is an internal comparison, not a control of the entire historical search. ZL3b/IT2a/RF1b are alternate readings of one manuscript. Prior project exposure means no independent confirmation. No plant name, English word, sound, language, plaintext, or translation is established.','']
    (BASE/'REPORT.md').write_text('\n'.join(lines))
    print(json.dumps({'decision':out['decision'],'readings':{r:{k:v[k] for k in ('greater','ties','positive_own_pairs','pass')} for r,v in out['readings'].items()}},indent=2))

if __name__=='__main__':
    main()
