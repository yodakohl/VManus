import hashlib,json,re
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
spec=json.loads((B/'src/SPEC.json').read_text());res=json.loads((B/'artifacts/RESULT.json').read_text());data=json.loads((R/spec['source']).read_text());raw=json.loads((R/spec['proposal']).read_text());units=set(raw['design']['output_inventory'])
for x in spec['inputs']:assert hashlib.sha256((R/x['path']).read_bytes()).hexdigest()==x['sha256']
lines={};count=0
for panel in data['panels']:
 for line in panel['lines']:
  assert (line['edition'],line['locus']) not in lines
  assert not line['page'].startswith('f84') and line['page']!='f116v'
  lines[(line['edition'],line['locus'])]=line;count+=len(line['groups'])
assert count==res['source_rows']==570
# Character-offset DP, not runner regex tokenization.
def valid(s):
    reachable={0}
    for i in range(len(s)):
        if i in reachable:
            reachable.update(i+len(u) for u in units if s.startswith(u,i))
    return bool(s) and len(s) in reachable
witness=json.loads((B/'artifacts/WITNESS_LINES.json').read_text())
for reader in spec['readers']:
    candidates=[]
    for (edition,locus),line in lines.items():
        if edition!=reader or line['kind']!='P':continue
        byindex={int(g['source_group_index']):g for g in line['groups']}
        for start in sorted(byindex):
            if any(k not in byindex for k in range(start,start+4)):continue
            rows=[byindex[k] for k in range(start,start+4)]
            if any(g['left_separator']!='DEFINITE_SPACE' or g['right_separator']!='DEFINITE_SPACE' or not valid(g['ivtff_group_raw']) for g in rows):continue
            candidates.append({'locus':locus,'first_index':start,'folio':int(re.match(r'f(\d+)',line['page']).group(1)),'forms':[g['ivtff_group_raw'] for g in rows],'rows':rows})
    candidates.sort(key=lambda c:(c['locus'],c['first_index']));out=res['readers'][reader]
    assert candidates==out['candidates'] and len(candidates)==out['eligible_windows']
    selected=[]
    for c in candidates:
        if any(c['folio']==d['folio'] or set(c['forms'])&set(d['forms']) for d in selected):continue
        selected.append(c)
        if len(selected)==6:break
    assert selected==out['certificate'] and len(selected)==out['certificate_windows']
    assert witness[reader]==[lines[(reader,c['locus'])] for c in selected]
    assert out['distinct_forms']==len({s for c in selected for s in c['forms']})
    assert out['folios']==sorted(c['folio'] for c in selected)
    assert out['status']==('FIVE_CONTROL_FORMS_INSUFFICIENT' if len(selected)==6 else 'NO_CERTIFICATE')
    for i,c in enumerate(selected):
        for d in selected[i+1:]:assert c['folio']!=d['folio'] and set(c['forms']).isdisjoint(d['forms'])
assert res['status']==('ALL_READERS_FIVE_CONTROL_FORMS_INSUFFICIENT' if all(x['certificate_windows']==6 for x in res['readers'].values()) else 'PARTIAL_OR_NO_CERTIFICATE')
for p,h in json.loads((B/'src/REGISTRATION_LOCK.json').read_text())['hashes'].items():assert hashlib.sha256((B/p).read_bytes()).hexdigest()==h
out={'status':'PASS','checks':['source/proposal/proof hashes','all570savedrawgroups','independent exact-index windows','DP working-unit eligibility','all definite internal/exterior seams','frozen greedy selection','separate-reader pairwise form disjointness','distinct physical folios','complete source lines','registration binding'],'ceiling':'Finite transcription-bound certificate; no paleography, semantic or statistical confirmation.'}
(B/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
