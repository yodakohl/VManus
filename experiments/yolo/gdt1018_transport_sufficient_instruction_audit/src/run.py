from common import *
from population import jobs
import primary,subprocess,collections

def main():
    checklock();receipt=read(A/'PUBLIC_REGISTRATION.json')
    subprocess.run(['git','cat-file','-e',receipt['commit']+'^{commit}'],check=True,cwd=R)
    start=now();rows=[]
    for j in jobs():rows.append(dict(**j,result=primary.evaluate(j['parse'],j['variant'])))
    put('ROWS.json',rows)
    counts={scope:dict(collections.Counter(x['result']['status'] for x in rows if x['scope']==scope)) for scope in ['original','saved','lift']}
    put('EXECUTION_RECEIPT.json',dict(started_utc=start,finished_utc=now(),counts=counts));print(json.dumps(counts))
if __name__=='__main__':main()
