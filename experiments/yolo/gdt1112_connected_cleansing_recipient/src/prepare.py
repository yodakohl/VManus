"""Select complete admitted cached units without decoding or normalizing groups."""
import csv, hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parents[1]

def main():
    model=json.loads((HERE/'src/MODEL.json').read_text())
    for p,expected in model['input_hashes'].items():
        assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==expected
    allowed={r['page'] for r in csv.DictReader((ROOT/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')}
    assert len(allowed)==179 and not any(p.startswith('f84') or p=='f116v' for p in allowed)
    bt=json.loads((ROOT/'research_registry/proposals/laufenberg_f85r2_20260926/source_supply_20260929/BT_SOURCE.json').read_text())
    units=[]; sequences={}
    for u in bt['units']:
        first=u['lines'][0][0];assert first['page'] in allowed
        item={'id':u['id'],'edition':first['edition'],'page':first['page'],'leaf':first['page'].split('r')[0].split('v')[0],'native':u['native'],'origins':['BT:'+u['id']],'lines':[]}
        for line in u['lines']:
            assert all(r['page'] in allowed and r['page']==first['page'] for r in line)
            item['lines'].append({'locus':line[0]['locus'],'groups':[{'id':r['source_group_id'],'raw':r['ivtff_group_raw']} for r in line]})
        key=tuple(g['id'] for l in item['lines'] for g in l['groups']);assert key not in sequences
        sequences[key]=item;units.append(item)
    paragraphs=json.loads((ROOT/'experiments/yolo/gdt928_multi_anchor_complete_paragraphs/artifacts/PARAGRAPHS.json').read_text())
    den={};selected={}
    for ed in ('ZL3b','IT2a'):
        den[ed]=len(paragraphs[ed]);selected[ed]=0
        for p in paragraphs[ed]:
            assert p['page'] in allowed
            if not any('lkchey' in l['words'] for l in p['lines']):continue
            selected[ed]+=1
            item={'id':ed+'|928|'+p['id'],'edition':ed,'page':p['page'],'leaf':p['leaf'],'native':True,'origins':['GDT928:'+p['id']],'lines':[]}
            for l in p['lines']:
                assert len(l['words'])==len(l['source_ids'])
                item['lines'].append({'locus':l['locus'],'groups':[{'id':i,'raw':w} for i,w in zip(l['source_ids'],l['words'])]})
            key=tuple(g['id'] for l in item['lines'] for g in l['groups'])
            if key in sequences:
                old=sequences[key];assert old['native'] and old['lines']==item['lines'];old['origins']+=item['origins']
            else:sequences[key]=item;units.append(item)
    counts={ed:sum(g['raw']=='lkchey' for u in units if u['edition']==ed and u['native'] for l in u['lines'] for g in l['groups']) for ed in ('ZL3b','IT2a')}
    profiles=json.loads((ROOT/'research_registry/proposals/laufenberg_f85r2_20260926/source_supply_20260929/DD_WORD_PROFILES.json').read_text())
    actual=next(p for p in profiles['profiles'] if p['form']=='lkchey')
    assert counts=={ed:actual['editions'][ed]['count'] for ed in counts}=={'ZL3b':8,'IT2a':8}
    ids=[g['id'] for u in units for l in u['lines'] for g in l['groups']];assert len(ids)==len(set(ids))
    packet={'units':units,'source_hashes':model['input_hashes'],'selection':{'all_BT_units':len(bt['units']),'complete_source_paragraphs':den,'native_marker_paragraphs':selected,'native_marker_counts':counts,'RF_policy':'BT unmarked same-locus windows only; no native global test','no_new_target_admission':True,'historical_exposure':True,'independent_confirmation_capacity':0,'sealed':['f84','f84r']}}
    (HERE/'src/SOURCE.json').write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'units':len(units),'unique_groups':len(ids),'native_counts':counts,'marker_paragraphs':selected}))
if __name__=='__main__':main()
