from pathlib import Path
from datetime import datetime,timezone
import json,gzip,hashlib
from engine import enumerate_cases
D=Path(__file__).resolve().parents[1];A=D/'artifacts'


def main():
    assert not(A/'RESULT.json').exists()
    lock=json.loads((A/'REGISTRATION_LOCK.json').read_text())
    for p,h in lock['files'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h,p
    S=json.loads((D/'src/SPEC.json').read_text());source=json.loads(gzip.decompress(Path(S['source']).read_bytes()));R={'experiment':'GDT1235','started_utc':datetime.now(timezone.utc).isoformat(),'readers':{}}
    for reader in S['readers']:
        rows=source[reader];W={tuple(r['units'])for r in rows};cert=enumerate_cases(W,S['signs'],S['runtime_seconds_per_reader'])
        (A/f'CERTIFICATE_{reader}.json.gz').write_bytes(gzip.compress(json.dumps(cert,separators=(',',':')).encode(),mtime=0));R['readers'][reader]={'groups':len(rows),'types':len(W),'status':cert['status'],'summary':cert.get('summary')}
    R['status']='COMPLETE_NECESSARY_BOUNDS'if all(v['status']=='COMPLETE'for v in R['readers'].values())else'UNKNOWN_INCOMPLETE';R['completed_utc']=datetime.now(timezone.utc).isoformat();(A/'RESULT.json').write_text(json.dumps(R,indent=2)+'\n')
    print({'status':R['status'],'completed_utc':R['completed_utc'],'readers':{k:{'bound':v['summary']['necessary_nontrivial_bound'],'sets':v['summary']['proper_sets'],'UD':v['summary']['ud_subcodes'],'forced':v['summary']['forced_singletons_from_short_code_condition']}if v['summary']else v for k,v in R['readers'].items()}})


if __name__=='__main__':main()
