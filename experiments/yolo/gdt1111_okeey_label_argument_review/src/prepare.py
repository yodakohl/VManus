"""Prepare an exposed, admission-bound packet; no decoder or normalization."""
import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.word_profiles import COLUMNS, ensure_cache, receipt, profile

def main():
    conn = ensure_cache()
    rows = [dict(r) for r in conn.execute('''SELECT * FROM groups
        WHERE (page='f76r' AND CAST(substr(locus,instr(locus,'.')+1) AS INTEGER) BETWEEN 1 AND 38)
        OR (page='f75v' AND locus='f75v.51')
        ORDER BY edition,page,CAST(substr(locus,instr(locus,'.')+1) AS INTEGER),source_group_index''')]
    with (HERE/'src/SOURCE.tsv').open('w',newline='') as out:
        writer=csv.DictWriter(out,fieldnames=COLUMNS,delimiter='\t',lineterminator='\n')
        writer.writeheader(); writer.writerows(rows)
    profiles={}
    for form in ('qokeey','okeey'):
        p=profile(conn,form,limit=1)
        profiles[form]=p['editions']
    provenance=receipt(conn)
    conn.close()
    sha=lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    model={
        'phase':'postexposure_exploratory_review',
        'scope':{'f76r':{'first':1,'last':38,'P_lines':29,'L_lines':9},'f75v':['f75v.51']},
        'forms':['qokeey','okeey'],
        'candidates':{
            'D':{'qokeey':{'gloss':'drink','role':'operation','obligations':['drinker','drinkable']},'okeey':{'gloss':'draught/dose','role':'nominal','obligations':['referent']}},
            'F':{'qokeey':{'gloss':'flows','role':'predicate','obligations':['flowing_material']},'okeey':{'gloss':'fluid','role':'nominal','obligations':['referent']}}
        },
        'rule':'Only direct exact P adjacency qokeey/okeey supplies a stipulated drinkable/flowing_material candidate; no identity or truth claim. All other participants remain unbound. All other forms UNKNOWN; no carry, prefix export or aliases.',
        'source_sha256':sha(HERE/'src/SOURCE.tsv'),
        'guard_receipt':provenance,
        'profiles':profiles,
        'prior_exposure':'All targets previously exposed; new native review occurred before this packet and model. No prospective pre-view prediction.',
        'independent_meaning_capacity':0,
        'sealed':['f84','f84r'],'reserve_access':False
    }
    (HERE/'src/MODEL.json').write_text(json.dumps(model,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({'prepared_groups':len(rows),'scope':model['scope']}))

if __name__=='__main__': main()
