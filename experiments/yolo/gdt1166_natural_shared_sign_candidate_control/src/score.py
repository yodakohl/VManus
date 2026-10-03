#!/usr/bin/env python3
"""Frozen post-prediction source-control scorer. No target-language inference."""
import argparse, collections, csv, gzip, hashlib, json
from fractions import Fraction
from pathlib import Path
EXP=Path(__file__).resolve().parents[1]
MODELS=('L','C','V')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text())
def packed_read(p): return json.loads(gzip.decompress(p.read_bytes()))
def dump(p,x): p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def bindings(obj):
    for name,h in obj['bindings'].items(): assert sha(EXP/name)==h,name
def rates(groups, unknown, predictions):
    result={}
    for model in MODELS:
        one=five=Fraction(0)
        for atoms,occurrences in groups.items():
            top=predictions[atoms]['models'][model]['top5']
            one+=Fraction(sum(w['reference'] in top[:1] for w in occurrences),len(occurrences))
            five+=Fraction(sum(w['reference'] in top for w in occurrences),len(occurrences))
        denominator=len(groups)+len(unknown)
        result[model]={'top1_credit':str(one),'top5_credit':str(five),'denominator':denominator,
            'primary_top1':float(one/denominator) if denominator else None,
            'primary_top5':float(five/denominator) if denominator else None,
            'known_type_top5_diagnostic':float(five/len(groups)) if groups else None}
    return result

def selftest():
    def word(r): return {'reference':r}
    groups={(0,):[word('a'),word('b')],(1,):[word('c')]}
    pred={a:{'models':{m:{'top5':top} for m in MODELS}} for a,top in [((0,),['a']),((1,),['c'])]}
    r=rates(groups,[word(None)],pred)
    assert r['V']['top5_credit']=='3/2' and r['V']['primary_top5']==.5
    assert r['V']['known_type_top5_diagnostic']==.75
    assert rates({},[word(None)],{})['V']['primary_top5']==0
    assert rates({},[],{})['V']['primary_top5'] is None
    print('SCORER_SYNTHETIC_FIXTURES_PASS')

def score():
    release=read(EXP/'artifacts/SCORE_RELEASE.json'); assert release['status']=='SCORE_RELEASED'
    assert sha(EXP/'artifacts/PREDICTION_LOCK.json')==release['prediction_lock_sha256']
    lock=read(EXP/'artifacts/PREDICTION_LOCK.json'); assert lock['status']=='ALL_HELD_PREDICTIONS_LOCKED_BEFORE_GOLD'; bindings(lock)
    keylock=read(EXP/'artifacts/KEY_SELECTION_LOCK.json'); bindings(keylock)
    assert sha(EXP/'artifacts/KEY_SELECTION_LOCK.json')==lock['key_selection_lock_sha256']
    bindings(read(EXP/'artifacts/FIT_RELEASE.json'))
    prereg=read(EXP/'artifacts/PREREG_LOCK.json'); bindings(prereg)
    predictions=packed_read(EXP/'artifacts/PREDICTIONS.json.gz')
    train=read(EXP/'artifacts/TRAIN_INPUT.json')
    gold=read(EXP/'artifacts/SOURCE_GOLD_LEDGER.json')
    train_types={tuple(w) for r in train['records'] for w in r['words']}
    held={r['record_id']:r for r in gold['records'] if r['split']=='TEST'}
    assert len(held)==138 and len(train['records'])==130
    assert {r['record_id'] for r in predictions['held_records']}==set(held)
    for r in predictions['held_records']:
        assert r['words']==[w['atoms'] for w in held[r['record_id']]['words']],r['record_id']
    pmap={tuple(p['atoms']):p for p in predictions['types']}
    assert len(pmap)==len(predictions['types'])
    assert set(pmap)=={tuple(w['atoms']) for r in held.values() for w in r['words']}
    groups=collections.defaultdict(list); unknown=[]; occurrences=[]
    references=set(predictions['reference_words'])
    for r in held.values():
        for w in r['words']:
            atoms=tuple(w['atoms']); p=pmap[atoms]; novel=atoms not in train_types
            assert p['novel_vs_all_training']==novel
            ambiguous=w['input_unknown'] or w['expansion_unknown']
            assert w['input_unknown']==(-1 in atoms)
            bucket='OTHER_HELD'
            if w['abbreviated'] and ambiguous:
                unknown.append(w); bucket='U_UNKNOWN_ZERO'
            elif w['abbreviated'] and novel:
                assert isinstance(w['reference'],str)
                groups[atoms].append(w); bucket='K_KNOWN_NOVEL_TYPE'
            row={'occurrence_id':w['occurrence_id'],'record_id':r['record_id'],'atoms':list(atoms),
                 'reference':w['reference'],'abbreviated':w['abbreviated'],'input_unknown':w['input_unknown'],
                 'expansion_unknown':w['expansion_unknown'],'bucket':bucket,'reference_OOV':w['reference'] not in references,
                 'models':{}}
            for m in MODELS:
                top=p['models'][m]['top5']
                row['models'][m]={'top5':top,'top1_hit':not ambiguous and w['reference'] in top[:1],
                                  'top5_hit':not ambiguous and w['reference'] in top}
            occurrences.append(row)
    metrics=rates(groups,unknown,pmap); denom=len(groups)+len(unknown)
    exact={m:Fraction(metrics[m]['top5_credit'])/denom if denom else Fraction(0) for m in MODELS}
    capacity=len(groups)>=20
    passed=capacity and exact['V']>=Fraction(1,2) and exact['V']-exact['L']>=Fraction(1,10) and exact['V']-exact['C']>=Fraction(1,10)
    result={'experiment':'GDT1166','status':'PASS_SOURCE_CANDIDATE_CONTROL' if passed else ('FAIL_SOURCE_CANDIDATE_CONTROL' if capacity else 'NO_CAPACITY'),
        'K_known_novel_abbreviated_types':len(groups),'U_unknown_abbreviated_occurrences':len(unknown),
        'primary_denominator':denom,'held_records':len(held),'held_occurrences':len(occurrences),'held_types':len(pmap),
        'metrics':metrics,'capacity_met':capacity,'V_minus_L':float(exact['V']-exact['L']),
        'V_minus_C':float(exact['V']-exact['C']),
        'known_primary_reference_OOV_occurrences':sum(w['reference'] not in references for ws in groups.values() for w in ws),
        'claim_ceiling':'Historical source candidate-generation control only. No Voynich translation, no significance or calibrated probability claim.',
        'prediction_lock_sha256':release['prediction_lock_sha256']}
    primary_occ=[r for r in occurrences if r['bucket']!='OTHER_HELD']
    result['occurrence_weighted_diagnostic']={m:{'count':len(primary_occ),'top1':sum(r['models'][m]['top1_hit'] for r in primary_occ)/len(primary_occ) if primary_occ else None,'top5':sum(r['models'][m]['top5_hit'] for r in primary_occ)/len(primary_occ) if primary_occ else None} for m in MODELS}
    result['unsupported_fit_primary_types']=sum(pmap[a]['contains_unsupported_fit_atom'] for a in groups)
    result['empty_candidate_primary_types']={m:sum(not pmap[a]['models'][m]['top5'] for a in groups) for m in MODELS}
    result['unsupported_fit_held_occurrences']=sum(pmap[tuple(r['atoms'])]['contains_unsupported_fit_atom'] for r in occurrences)
    result['selected_contracts']=read(EXP/'artifacts/KEY_SELECTION.json')['selected']
    rows=[]
    for atoms,ws in sorted(groups.items()):
        row={'unit':'K','id':json.dumps(atoms),'occurrences':len(ws),'gold_references':json.dumps(dict(collections.Counter(w['reference'] for w in ws)),ensure_ascii=False)}
        for m in MODELS:
            top=pmap[atoms]['models'][m]['top5'];row[m+'_top5']=json.dumps(top,ensure_ascii=False)
            row[m+'_top5_credit']=str(Fraction(sum(w['reference'] in top for w in ws),len(ws)))
        rows.append(row)
    for w in unknown:
        row={'unit':'U','id':w['occurrence_id'],'occurrences':1,'gold_references':json.dumps(w['reference'],ensure_ascii=False)}
        for m in MODELS:
            row[m+'_top5']=json.dumps(pmap[tuple(w['atoms'])]['models'][m]['top5'],ensure_ascii=False);row[m+'_top5_credit']='0'
        rows.append(row)
    fields=['unit','id','occurrences','gold_references']+[x for m in MODELS for x in [m+'_top5',m+'_top5_credit']]
    with (EXP/'artifacts/CANDIDATE_TABLE.tsv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields,delimiter='\t');writer.writeheader();writer.writerows(rows)
    (EXP/'artifacts/OCCURRENCE_RESULTS.json.gz').write_bytes(gzip.compress((json.dumps(occurrences,ensure_ascii=False,separators=(',',':'))+'\n').encode(),mtime=0))
    dump(EXP/'artifacts/RESULT.json',result);print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--selftest',action='store_true');args=parser.parse_args()
    selftest() if args.selftest else score()
