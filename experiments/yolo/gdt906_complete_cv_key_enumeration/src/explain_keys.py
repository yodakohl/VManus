#!/usr/bin/env python3
"""Publish all lexical observed keys, preserving full original word order."""
import argparse,json,sys
from pathlib import Path
import run
E=Path(__file__).resolve().parents[1]
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--cache-dir',type=Path,required=True);a=ap.parse_args();run.load_reference(a.cache_dir)
    plan=run.read(E/'artifacts/PLAN.json.gz');cases=run.read(E/'artifacts/CASES.json.gz');px={}
    for p in plan['paragraphs']:
        for g in p['groups']:
            for vi,v in enumerate(run.core.VOWELS):
                if g['inherent_bits']&(1<<vi):px[run.cid(p,g,v)]=(p,g)
    records=[]
    for r in cases:
        if not r['values']:continue
        p,g=px[r['case_id']];v=r['inherent'];codes=sorted({c for seg in g['segments'] for c in seg});parts=run.core.inventory(v)
        for values,flag in zip(r['values'],r['grammar_accepted']):
            observed={c:parts[i] for c,i in zip(codes,values)};decoded={}
            for w,seg in zip(p['words'],g['segments']):decoded[w]=run.core.decode_components(tuple(observed[c] for c in seg),v)
            plaintext=[decoded[w] for w in p['raw_words']];analyses=[run.REF['analyses'][w] for w in plaintext]
            assert run.grammar.accepts(run.REF['grammar'],analyses)==flag
            records.append(dict(case_id=r['case_id'],origin=r['origin'],page=p['page'],loci=p['loci'],inherent=v,mask=g['mask'],equivalent_masks=g['equivalent_masks'],observed_key=observed,raw_words=p['raw_words'],plaintext=plaintext,analyses=analyses,grammar_accepted=flag))
    artifact=dict(lexical_keys=len(records),grammar_accepted=sum(r['grammar_accepted'] for r in records),confirmed_meanings=0,records=records,claim_ceiling='Mechanical full-paragraph dictionary keys; grammar verdict is not a translation or established language identity. Unobserved code assignments are not identified.')
    run.write(E/'artifacts/LEXICAL_KEYS.json',artifact)
    lines=['# All complete lexical keys in GDT906','',str(len(records))+' keys. These are mechanical dictionary outputs, not translations.','']
    for n,r in enumerate(records,1):
        lines.extend(['## '+str(n)+': '+r['case_id'],'','Page/loci: '+r['page']+' / '+', '.join(r['loci'])+'. Grammar accepted: '+str(r['grammar_accepted'])+'.','','| Position | Raw group | Mechanical output |','|---:|---|---|'])
        lines.extend('| '+str(i)+' | `'+a+'` | `'+b+'` |' for i,(a,b) in enumerate(zip(r['raw_words'],r['plaintext']),1))
        lines.extend(['','Observed key: `'+json.dumps(r['observed_key'],sort_keys=True)+'`',''])
    (E/'artifacts/LEXICAL_KEYS.md').write_text('\n'.join(lines).rstrip()+'\n');print(json.dumps({k:v for k,v in artifact.items() if k!='records'}))
if __name__=='__main__':main()
