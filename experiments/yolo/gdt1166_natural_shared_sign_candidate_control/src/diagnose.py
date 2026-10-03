#!/usr/bin/env python3
"""Post-lock descriptive analysis only; never feeds any fitting or score."""
import collections,gzip,hashlib,json
from fractions import Fraction
from pathlib import Path
P=Path(__file__).resolve().parents[1]
def read(s):return json.loads((P/s).read_text())
def unpack(s):return json.loads(gzip.decompress((P/s).read_bytes()))
assert read('artifacts/SCORE_RELEASE.json')['status']=='SCORE_RELEASED'
result=read('artifacts/RESULT.json');pred=unpack('artifacts/PREDICTIONS.json.gz');occ=unpack('artifacts/OCCURRENCE_RESULTS.json.gz')
selection=read('artifacts/KEY_SELECTION.json');key=read('artifacts/OPAQUE_KEY_PRIVATE_TO_PREPARATION.json')
chars={s['atom_id']:s['character'] for s in key['symbols']};pm={tuple(p['atoms']):p for p in pred['types']}
refs=set(pred['reference_words']);groups=collections.defaultdict(list)
for r in occ:
    if r['bucket']=='K_KNOWN_NOVEL_TYPE':groups[tuple(r['atoms'])].append(r)
ceiling=sum((Fraction(sum(r['reference'] in refs for r in rows),len(rows)) for rows in groups.values()),Fraction())
contracts={}
for m,s in selection['selected'].items():
    contracts[m]={'marker_id':s['marker'],'actual_source_graphic':chars.get(s['marker']),
                  'actual_source_codepoint':f"U+{ord(chars[s['marker']]):04X}" if s['marker']>=0 else None,
                  'residual':s['residual'],'selected_panel':s['panel']}
bar=next(i for i,c in chars.items() if c=='\u0305')
bar_output={m:selection['alphabet'][s['key'][bar]] for m,s in selection['selected'].items()}
comparison=collections.Counter()
for atoms,rows in groups.items():
    c=pm[atoms]['models']['C']['top5'];v=pm[atoms]['models']['V']['top5']
    comparison['same_top5' if c==v else 'different_top5']+=1
    cg=Fraction(sum(r['reference'] in c for r in rows),len(rows));vg=Fraction(sum(r['reference'] in v for r in rows),len(rows))
    comparison['V_more_credit' if vg>cg else 'V_less_credit' if vg<cg else 'same_credit']+=1
out={'experiment':'GDT1166','phase':'POST_LOCK_DESCRIPTIVE_NOT_PREREGISTERED_ENDPOINT','registered_status_unchanged':result['status'],
     'source_marker_identities':contracts,'overline_atom_id':bar,'overline_fit_supported':bar in selection['fit_atoms'],'overline_literal_outputs':bar_output,
     'reference_oracle_macro_credit':str(ceiling),'reference_oracle_conservative_ceiling':float(ceiling/result['primary_denominator']),
     'C_V_primary_comparison':dict(comparison),'unknown_zero_policy_unchanged':True,
     'limitations':['Source-only diagnosis after gold access; no target meaning, new fit, rescue, significance or independently established search optimum.'],
     'inputs':{s:hashlib.sha256((P/s).read_bytes()).hexdigest() for s in ['artifacts/RESULT.json','artifacts/PREDICTIONS.json.gz','artifacts/OCCURRENCE_RESULTS.json.gz','artifacts/KEY_SELECTION.json','artifacts/OPAQUE_KEY_PRIVATE_TO_PREPARATION.json']}}
(P/'artifacts/DIAGNOSTIC.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out,ensure_ascii=False))
