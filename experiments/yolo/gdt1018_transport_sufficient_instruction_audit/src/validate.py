from common import *
from population import jobs
import independent,collections

def main():
    checklock();source=jobs();rows=read(A/'ROWS.json');assert len(source)==len(rows)==677
    checks=[]
    for j,r in zip(source,rows,strict=True):
        assert all(r[k]==v for k,v in j.items())
        a=r['result'];b=independent.evaluate(j['parse'],j['variant'])
        assert a['status']==b['status'],(j['id'],a,b)
        assert b['old_existential'],j['id']
        assert (a['successful_paths'],a['failed_prefixes'])==(b['successful_paths'],b['failed_prefixes']),(j['id'],a,b)
        checks.append(dict(id=j['id'],scope=j['scope'],result=b))
    put('INDEPENDENT.json',checks)
    result=dict(status='PASS',checked=len(checks),scope_counts=dict(collections.Counter(j['scope'] for j in checks)),completed_utc=now(),scope='Independent implementation of new prefix quantifier over frozen independent old executor; not independent meaning.')
    put('VALIDATION.json',result);print(json.dumps(result))
if __name__=='__main__':main()
