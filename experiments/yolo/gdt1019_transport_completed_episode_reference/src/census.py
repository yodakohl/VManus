from common import *
from certificate import inspect_certificate
import itertools,collections,subprocess

def main():
    checklock();receipt=read(A/'PUBLIC_REGISTRATION.json');subprocess.run(['git','cat-file','-e',receipt['commit']+'^{commit}'],check=True,cwd=R)
    s,g=inputs();settings=[dict(zip(g['variants'],v)) for v in itertools.product(*g['variants'].values())];out=[]
    for o in read(A/'ORIGINAL_CANDIDATES.json'):
        for vi in o['valid_variants']:
            a=replay(o['parse'],settings[vi],s);b=replay(o['parse'],settings[vi],s,True);assert a==b
            out.append(dict(id=o['id']+'_V'+str(vi),original=o['id'],variant_index=vi,status=a['status'],certificate=a['certificate'],old_existential=a['old_existential']))
    put('ORIGINAL_CERTIFICATES.json',out);assert len(out)==156
    rows=[]
    for source,ck,pk,ik in [('GDT1013','source_cases','source_saved_primary','source_saved_independent'),('GDT1014','source_wrapper_cases','source_wrapper_primary','source_wrapper_independent')]:
        cases=read(R/s[ck]);p=read(R/s[pk]);q=read(R/s[ik])
        for case,one,two in zip(cases,p,q,strict=True):
            assert case['id']==one['id']==two['id']
            for engine,r in [('primary',one),('independent',two['independent'])]:
                if r['status']!='sat':continue
                parse=r['witness']['parse'];a=inspect_certificate(parse);b=inspect_certificate(parse,True);assert a==b
                rows.append(dict(source=source,case=case['id'],engine=engine,context=case['context'],certificate=a,status='CERTIFICATE_VALID' if a['valid'] else 'CERTIFICATE_CONTRADICTED',old_full_world_status='published_verified_positive'))
    assert len(rows)==125
    put('SAVED_CERTIFICATES.json',rows)
    result=dict(original_settings=len(out),original_counts=dict(collections.Counter(x['status'] for x in out)),saved_maps=len(rows),saved_counts=dict(collections.Counter(x['status'] for x in rows)),full_search_gate=all(r['status']=='COHERENT' for r in out),completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    put('PRECURSOR.json',result);print(json.dumps(result))
if __name__=='__main__':main()
