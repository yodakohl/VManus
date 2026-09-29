"""Prepare all fixed case/domain predictions without intersecting target domains."""
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import re

E = Path(__file__).resolve().parents[1]
ROOT = E.parents[2]


def read(p):
    data=p.read_bytes()
    return json.loads(gzip.decompress(data) if p.suffix=='.gz' else data)


def main():
    assert not (E/'artifacts/RESULT.json').exists()
    source=read(ROOT/'experiments/yolo/gdt963_dioscorides_complete_content_code/src/SOURCE.json')
    counts={r['id']:Counter(r['atoms']) for r in source['records']}
    atoms=sorted(a for a in set().union(*counts.values()) if sum(c[a]>=2 for c in counts.values())>=2)
    assert len(atoms)==13
    cases=read(ROOT/'experiments/yolo/gdt1096_dioscorides_finite_recurrent_domains/artifacts/CASES.json')
    certs=read(ROOT/'experiments/yolo/gdt1096_dioscorides_finite_recurrent_domains/artifacts/CERTIFICATES.json.gz')
    roles=[]
    for rid in counts:
        role=[]
        for i,r in enumerate(cases):
            if r['edition']=='IT2a' and r['record']==rid and r['status']=='NECESSARY_DOMAINS_NONEMPTY':
                assert not r['page'].startswith('f84') and r['page']!='f116v'
                role.append(dict(index=i,page=r['page'],leaf=re.match(r'f\d+',r['page']).group(),
                                 domains={a:certs[str(i)]['final_domains'][a] for a in atoms if counts[rid][a]>=2}))
        roles.append(role)
    assert [len(r) for r in roles]==[7,92,100,99]
    participation={a:{r:c[a] for r,c in counts.items() if c[a]>=2} for a in atoms}
    data=dict(scope='Unchanged all-case finite domain projection; no target intersections computed in preparation',
              atoms=atoms,role_names=list(counts),roles=roles,participation=participation,
              shared_recurrent_occurrences=sum(sum(v.values()) for v in participation.values()))
    raw=(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n').encode()
    (E/'artifacts/INPUT_DOMAINS.json.gz').write_bytes(gzip.compress(raw,mtime=0))
    table=['index\tedition\tpage\trecord\tparent_status\tprediction']
    for i,r in enumerate(cases):
        prediction='shared domain intersections nonempty on four distinct leaves' if any(c['index']==i for role in roles for c in role) else 'parent status inherited; not new domain tuple member'
        table.append('\t'.join(str(v) for v in (i,r['edition'],r['page'],r['record'],r['status'],prediction)))
    (E/'artifacts/CASE_PREDICTIONS.tsv').write_text('\n'.join(table)+'\n')
    print(json.dumps(dict(prepared_cases=len(cases),role_counts=[len(r) for r in roles],shared_atoms=len(atoms),shared_occurrences=data['shared_recurrent_occurrences'],target_intersections_computed=0)))


if __name__=='__main__':
    main()
