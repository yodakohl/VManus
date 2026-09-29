#!/usr/bin/env python3
"""Render a frozen exploratory author account; neither parser nor decoder."""
import argparse,csv,hashlib,io,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
OWNED=HERE/'Y_COMPLETE_UNITS.json'
FORMAL=ROOT/'experiments/yolo/gdt1051_frozen_grammar_local_application/artifacts/RESULT.json'
MODEL=HERE/'BB_MODEL.json'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build():
    src=json.loads(OWNED.read_text()); formal=json.loads(FORMAL.read_text());model=json.loads(MODEL.read_text())
    assert src['groups']==288 and formal['raw_groups']==288
    for p in src['source_packets']:
        assert digest(ROOT/p['path'])==p['sha256']
    expected=[(u['edition'],u['locus'],i,g) for u in src['units'] for i,g in enumerate(u['groups'],1)]
    observed=[(g['edition'],g['locus'],g['index'],g['raw']) for g in formal['groups']]
    assert len(expected)==288 and expected==observed, 'whole-account input conservation'
    base=model['design']['base_values'];values=model['design']['whole_values']
    assert base=={'ok':'MOON','oko':'SUN'}
    rows=[];whole=partial=0
    for g in formal['groups']:
        f=g['wrapper_host'] or {}; w=f.get('wrapper','UNRESOLVED');h=f.get('page_host_before_local_frame','UNRESOLVED');r=f.get('right_family','UNRESOLVED')
        status='UNKNOWN'; light='UNKNOWN';interval='UNKNOWN';inner='UNKNOWN'
        if g['raw'] in values:
            if g['raw']=='oko':assert (w,h,r)==('NONE','oko','NONE')
            else:assert w=='NONE' and h in base and r=='aiin'
            light=values[g['raw']];interval='SUN' if g['raw']=='oko' else 'FIRST_PROPER_FIXED_ZODIAC_RETURN_INTERVAL('+base[h]+')'
            status='CONDITIONAL_WHOLE_VALUE_NOT_IDENTIFIED';whole+=1
        elif w in ('q','ch') and h in base and r=='aiin':
            inner='LIGHT_OF('+base[h]+')';status='INNER_C0_ONLY_WRAPPER_AND_WHOLE_UNKNOWN';partial+=1
        rows.append({'part':g['part'],'reader':g['edition'],'locus':g['locus'],'ordinal':g['index'],'raw':g['raw'],'left_separator':g['left_separator'],'right_separator':g['right_separator'],'wrapper':w,'host':h,'right_family':r,'BB_whole':light,'W_whole':interval,'BB_inner_only':inner,'status':status,'next_word_consumed':'NO'})
    out=io.StringIO();writer=csv.DictWriter(out,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');writer.writeheader();writer.writerows(rows)
    result={'status':'PARTIAL_C0_NOMINAL_AUTHORING_NO_MEANING_SELECTION','idea':'IDEA000798','raw_groups':288,'conditional_whole_positions':whole,'inner_only_positions_whole_unknown':partial,'wholly_unassigned_positions':288-whole-partial,'confirmed_words':0,'independent_confirmation_leaves':0,'semantic_validation':False,'source_inputs':{str(p.relative_to(ROOT)):digest(p) for p in (OWNED,FORMAL,MODEL)},'scope':'Complete existing rings and prose window; no other target acquisition. Readers are alternatives, not independent evidence.'}
    return out.getvalue(),json.dumps(result,ensure_ascii=False,indent=2)+'\n'
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');args=ap.parse_args();table,result=build()
    outputs={'BB_ACCOUNT.tsv':table,'BB_RESULT.json':result}
    if args.check:
        for name,s in outputs.items():assert (HERE/name).read_text()==s,name
        print('Whole-account and frozen-input conservation verified; semantic validation: false.')
    else:
        for name,s in outputs.items():(HERE/name).write_text(s)
        print(result)
if __name__=='__main__':main()
