from pathlib import Path
import json,hashlib
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
def main():
 lock=json.loads((A/'REGISTRATION_LOCK.json').read_text())
 for p,d in lock['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==d,p
 obs=json.loads((A/'OBSERVATION.json').read_text());seal=json.loads((A/'OBSERVATION_SEAL.json').read_text())
 assert hashlib.sha256((A/'OBSERVATION.json').read_bytes()).hexdigest()==seal['observation_sha256']
 assert hashlib.sha256((D/'PREREGISTRATION.md').read_bytes()).hexdigest()==seal['registration_sha256']
 assert [x['locus'] for x in obs['targets']]==['f75v.22','f75v.32']
 classes=[x['seam'] for x in obs['targets']]
 contrast=all(x['located'] for x in obs['targets']) and set(classes)=={'SPACE_LIKE','INTERNAL_LIKE'}
 result={'status':'SOURCE_AWARE_QUALITATIVE_LOCAL_CONTRAST' if contrast else 'NO_CLEAR_LOCAL_CONTRAST','observations':[{k:t[k] for k in ['locus','located','seam']} for t in obs['targets']],'observer_count':1,'independent_physical_witnesses':1,'independent_confirmation_capacity':0,'meaning_assigned':False,'authorial_word_boundary_confirmed':False,'scope':'Reduction of one source-aware qualitative original-image judgment; software does not adjudicate handwriting.'}
 (A/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
