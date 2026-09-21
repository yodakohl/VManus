from common import *
import model,subprocess

def main():
    checklock();registration=read(A/'PUBLIC_REGISTRATION.json');subprocess.run(['git','cat-file','-e',registration['commit']+'^{commit}'],check=True,cwd=R)
    spec,source=inputs();words=[w for l in source['projected_lines'] for w in l['raw'].split()];assert len(words)==33
    start=now();rows=[]
    for case in spec['candidates']:rows.append(dict(candidate=case['id'],pairing=case['pairing'],result=model.evaluate(words,spec,case['pairing'])))
    raw=[w for line in source['diplomatic_record']['lines'] for w in line['words']]
    scope=model.evaluate(raw,spec,'direct');assert scope['status']=='SOURCE_FORMS_UNBOUND'
    put('ROWS.json',rows);put('DIPLOMATIC_SCOPE.json',scope);put('EXECUTION_RECEIPT.json',dict(started_utc=start,completed_utc=now(),public_registration=registration['commit']))
    print(json.dumps({r['candidate']:r['result']['status'] for r in rows}))
if __name__=='__main__':main()
