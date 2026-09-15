"""Intake only the 28 frozen loci, through the selector-first guard."""
from pathlib import Path
import csv, hashlib, io, json, subprocess

E = Path(__file__).resolve().parents[1]
R = E.parents[2]

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    lock = json.loads((E/'PREREG_LOCK.json').read_text())
    for p,h in lock['files'].items():
        assert sha(E/p)==h, p
    for p,h in lock['source_files'].items():
        assert sha(R/p)==h, p
    spec=json.loads((E/'src/SPEC.json').read_text())
    data={};receipts=[]
    for name,source in spec['sources'].items():
        cmd=['./vmanus-exp','query-tsv',source['path'],'--selector','locus']
        for locus in spec['loci']:
            cmd+=['--allow',locus]
        cmd+=['--columns',','.join(source['columns']),'--forbid-prefix','f84','--forbid-prefix','f84r']
        p=subprocess.run(cmd,cwd=R,text=True,capture_output=True,check=True)
        stats=[json.loads(x[12:]) for x in p.stderr.splitlines() if x.startswith('GUARD_STATS ')]
        assert len(stats)==1 and stats[0]['selected']>0
        data[name]=list(csv.DictReader(io.StringIO(p.stdout),delimiter='\t'))
        assert {x['locus'] for x in data[name]}==set(spec['loci'])
        receipts.append({'name':name,'command':cmd,'guard':stats[0]})
    text=json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n'
    dest=E/'artifacts/INPUT.json'
    if dest.exists(): assert dest.read_text()==text
    else: dest.write_text(text)
    (E/'artifacts/INTAKE.json').write_text(json.dumps({'source_receipts':receipts,'input_sha256':sha(dest),'prior_project_exposure':True,'reserve_access':False},indent=2)+'\n')
    print(json.dumps({'intake_counts':{k:len(v) for k,v in data.items()},'input_sha256':sha(dest)}))

if __name__=='__main__': main()
