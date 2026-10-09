import hashlib,json,re
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def main():
    lock=json.loads((B/'src/REGISTRATION_LOCK.json').read_text())
    for p,h in lock['hashes'].items():assert hashlib.sha256((B/p).read_bytes()).hexdigest()==h
    spec=json.loads((B/'src/SPEC.json').read_text())
    for x in spec['inputs']:assert hashlib.sha256((R/x['path']).read_bytes()).hexdigest()==x['sha256']
    data=json.loads((R/spec['source']).read_text());proposal=json.loads((R/spec['proposal']).read_text())
    units=proposal['design']['output_inventory'];parser=re.compile('(?:'+'|'.join(sorted(units,key=lambda x:(-len(x),x)))+')+')
    allow=set()
    command=data['guard_command']
    for i,x in enumerate(command[:-1]):
        if x=='--allow':allow.add(command[i+1])
    lines={};ids=set();row_count=0
    for panel in data['panels']:
        for line in panel['lines']:
            key=(line['edition'],line['locus']);assert key not in lines
            assert line['locus'] in allow and not line['page'].startswith('f84') and line['page']!='f116v'
            assert len(line['groups'])==int(line['group_count'])
            for g in line['groups']:
                assert g['source_group_id'] not in ids;ids.add(g['source_group_id']);row_count+=1
            lines[key]=line
    assert row_count==570
    outputs={};witness_lines={}
    for reader in spec['readers']:
        candidates=[]
        for (edition,locus),line in sorted(lines.items()):
            if edition!=reader or line['kind']!='P':continue
            gs=sorted(line['groups'],key=lambda g:int(g['source_group_index']))
            for j in range(len(gs)-3):
                rows=gs[j:j+4];indices=[int(g['source_group_index']) for g in rows]
                if indices!=list(range(indices[0],indices[0]+4)):continue
                if not all(g['left_separator']==g['right_separator']=='DEFINITE_SPACE' for g in rows):continue
                if not all(parser.fullmatch(g['ivtff_group_raw']) for g in rows):continue
                candidates.append({'locus':locus,'first_index':indices[0],'folio':int(re.match(r'f(\d+)',line['page']).group(1)),'forms':[g['ivtff_group_raw'] for g in rows],'rows':rows})
        candidates.sort(key=lambda c:(c['locus'],c['first_index']))
        chosen=[];used=set();folios=set()
        for c in candidates:
            forms=set(c['forms'])
            if not forms.isdisjoint(used) or c['folio'] in folios:continue
            chosen.append(c);used.update(forms);folios.add(c['folio'])
            if len(chosen)==6:break
        outputs[reader]={'eligible_windows':len(candidates),'certificate_windows':len(chosen),'distinct_forms':len(used),'folios':sorted(folios),'status':'FIVE_CONTROL_FORMS_INSUFFICIENT' if len(chosen)==6 else 'NO_CERTIFICATE','certificate':chosen,'candidates':candidates}
        witness_lines[reader]=[lines[(reader,c['locus'])] for c in chosen]
    # All ordinary cyclic clause positions have at most three noncontrol groups.
    base=['a','b','c','END']*3;fixtures=0
    for i,v in enumerate(base):
        if v=='END':continue
        for breaks in range(1,4):
            replacement=['FRAG']
            for _ in range(breaks):replacement+=['CONT','CONT','FRAG']
            seq=base[:i]+replacement+base[i+1:]
            assert all(any(x in {'END','CONT'} for x in seq[j:j+4]) for j in range(len(seq)-3));fixtures+=1
    result={'status':'ALL_READERS_FIVE_CONTROL_FORMS_INSUFFICIENT' if all(v['certificate_windows']==6 for v in outputs.values()) else 'PARTIAL_OR_NO_CERTIFICATE','source_rows':row_count,'source_loci':len(allow),'readers':outputs,'continuation_fixtures':fixtures,'scope':'Conditional fixed control-word architecture; no source meaning, significance or new physical observation.'}
    (B/'artifacts/RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    (B/'artifacts/WITNESS_LINES.json').write_text(json.dumps(witness_lines,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'readers':{r:{k:v for k,v in x.items() if k not in ('certificate','candidates')} for r,x in outputs.items()}},indent=2))
if __name__=='__main__':main()
