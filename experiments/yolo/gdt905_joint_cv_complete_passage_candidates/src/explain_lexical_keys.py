#!/usr/bin/env python3
"""Recover assignments already counted in COMPLETE cases; no extended search.
Post-result explanatory replay. Rejected keys remain rejected by the fixed CFG.
"""
import argparse,gzip,json,pickle,time
from pathlib import Path
import run
E=run.E
def main():
    p=argparse.ArgumentParser();p.add_argument('--cache-dir',type=Path,required=True);p.add_argument('--check',action='store_true');a=p.parse_args()
    run.check_lock();ref=run.reference(a.cache_dir,True)
    raw=E/'artifacts/CANDIDATES.json';data=raw.read_bytes() if raw.exists() else gzip.decompress(raw.with_suffix('.json.gz').read_bytes())
    records=json.loads(data);target={(ed,r['paragraph_id']):r for ed,r in run.selected(run.read('TARGET.json'))}
    wanted=[(r,c) for r in records for c in r['cases'] if c['status']=='COMPLETE' and c['stats']['complete_assignments']]
    indexes={};out=[]
    for record,case in wanted:
        v=case['inherent'];mask=case['mask'];r=target[record['edition'],record['paragraph_id']]
        if v not in indexes:
            with (a.cache_dir/('patterns_'+v+'.pkl')).open('rb') as f:indexes[v]=pickle.load(f)
        singles={c for i,c in enumerate(run.ALPHABET) if mask&(1<<i)};words=sorted(set(r['words']))
        segs=[run.core.segment(w,singles) for w in words];word_segs=dict(zip(words,segs))
        codes=sorted({c for seq in segs for c in seq});ids={c:i for i,c in enumerate(codes)}
        parts=run.core.inventory(v);part_ids={p:i for i,p in enumerate(parts)};tables=[];keys=[]
        for word,seg in zip(words,segs):
            unique=list(dict.fromkeys(seg));first=[seg.index(c) for c in unique]
            rows={tuple(part_ids[cs[i]] for i in first) for _,cs in indexes[v][run.core.pattern(seg)]}
            tables.append(dict(vars=[ids[c] for c in unique],rows=sorted(rows)))
        def accept(values):
            observed={c:parts[values[ids[c]]] for c in codes}
            decoded={w:run.core.decode_components(tuple(observed[c] for c in seg),v) for w,seg in word_segs.items()}
            plaintext=[decoded[w] for w in r['words']];analyses=[ref['analyses'][w] for w in plaintext]
            accepted=run.grammar.accepts(ref['grammar'],analyses)
            keys.append(dict(inherent=v,mask=mask,observed_key=observed,complete_key=run.completion(observed,mask,v),plaintext=plaintext,analyses=analyses,grammar_accepted=accepted))
            return accepted
        solved=run.csp.solve_tables(tables,len(codes),27,time.monotonic()+15,accept=accept)
        assert solved['status']=='COMPLETE'
        for k,value in case['stats'].items():
            if k!='elapsed_seconds':assert solved['stats'][k]==value,(r['paragraph_id'],k,solved['stats'][k],value)
        assert len(keys)==case['stats']['complete_assignments']
        out.append(dict(edition=record['edition'],paragraph_id=r['paragraph_id'],page=r['page'],loci=r['loci'],written_groups=r['words'],deterministic_trace_counts_exact=True,keys=keys))
    result=dict(status='EXPLANATORY_REPLAY_ONLY',cases=len(out),keys=sum(len(x['keys']) for x in out),records=out,claim_ceiling='Exact assignments already encountered in completed cases. Grammar-rejected keys are not admitted readings; no new search, held data or meaning.')
    if a.check:assert run.read('LEXICAL_KEY_EXPLANATION.json')==result
    else:run.write('LEXICAL_KEY_EXPLANATION.json',result)
    lines=['# Vollständige mechanische Schlüssel, an der Grammatik gescheitert','',
           'Diese Wortfolgen sind **keine Übersetzungen**. Sie setzen alle Gruppen',
           'des jeweiligen Absatzes unter einem festen Schlüssel in Einträge der',
           'Referenzwortliste um. Beide unten beschriebenen ursprünglichen Fälle',
           'scheitern an der festgelegten Grammatik. Es gibt keine deutsche Glosse.',
           'Die vollständigen 27-Komponenten-Schlüssel stehen im begleitenden JSON;',
           'unbeobachtete Ergänzungswerte sind willkürliche Repräsentanten.','']
    for row in out:
        for key in row['keys']:
            lines += [f"## {row['edition']} · {row['page']} · {row['paragraph_id']} · Maske {key['mask']}",'',
                      f"Inhärenter Vokal: `{key['inherent']}`. Feste Grammatik akzeptiert: `{key['grammar_accepted']}`.",'',
                      '| Stelle | Geschriebene Gruppe | Mechanische Ausgabe |','|---|---|---|']
            lines += [f'| {i} · {loc} | `{written}` | `{plain}` |' for i,(loc,written,plain) in enumerate(zip(row['loci'],row['written_groups'],key['plaintext']),1)]
            lines += ['','Beobachtete Zuordnung:','', '| Schriftbaustein | Hypothetische CV-Komponente |','|---|---|']
            lines += [f'| `{code}` | `{component}` |' for code,component in sorted(key['observed_key'].items())]
            lines.append('')
    rendered='\n'.join(lines).rstrip()+'\n';reader=E/'artifacts/LEXICAL_KEYS.md'
    if a.check:assert reader.read_text()==rendered
    else:reader.write_text(rendered)
    print(run.enc(dict(cases=result['cases'],keys=result['keys'],recovered=[dict(edition=x['edition'],paragraph=x['paragraph_id'],plaintext=k['plaintext'],grammar_accepted=k['grammar_accepted']) for x in out for k in x['keys']])))
if __name__=='__main__':main()
