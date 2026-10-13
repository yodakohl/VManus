#!/usr/bin/env python3
"""Post-result independent replay of the six unchanged external source packs.
No native input or experiment implementation is imported.
"""
import collections,datetime,gzip,hashlib,itertools,json
from pathlib import Path
B=Path(__file__).resolve().parents[1];ROOT=B.parents[2]
ALPHABET='bcdfghjklmnpqrstvwxyz ';VOWELS=set('aeiou')

def stripped_stream(raw):
 # Character scan keeps separators only between nonempty surviving words.
 word=[];started=False
 for char in raw+' ':
  if char.isspace():
   if word:
    if started:yield ' '
    yield from word;started=True;word=[]
  elif char not in VOWELS:word.append(char)

def count_lines(lines):
 triples=collections.Counter();kept=events=0
 for raw in lines:
  word=list(stripped_stream(raw))
  if not word:continue
  assert set(word)<=set(ALPHABET)
  padded=['^','^']+word
  triples.update(zip(padded,padded[1:],padded[2:]));kept+=1;events+=len(word)
 rows=collections.defaultdict(lambda:[0]*22);index={s:i for i,s in enumerate(ALPHABET)}
 for (a,b,c),n in triples.items():rows[(a,b)][index[c]]+=n
 return [{'context':list(c),'counts':v} for c,v in sorted(rows.items())],kept,events

def main():
 assert ''.join(stripped_stream(' aei  b a c '))=='b c'
 assert ''.join(stripped_stream('aeiou'))==''
 rows,n,e=count_lines(['a b','c','aeiou']);assert n==2 and e==2
 assert {tuple(r['context']) for r in rows}=={('^','^')}
 manifest_path=ROOT/'gdt001_language_pack_manifest.json';manifest=json.loads(manifest_path.read_text())['packs']
 artifact_path=B/'artifacts/MODEL_COUNTS.json.gz';expected=json.loads(gzip.decompress(artifact_path.read_bytes()))
 assert set(expected)==set(manifest)
 receipts={}
 for name,entry in sorted(manifest.items()):
  source=ROOT/'.gdt001/language_packs'/f'{name}.txt';raw=source.read_bytes();digest=hashlib.sha256(raw).hexdigest()
  assert digest==entry['prepared_sha256'] and len(raw)==entry['prepared_bytes'],name
  rows,lines,events=count_lines(raw.decode('utf-8').splitlines())
  reconstructed={'provenance':entry,'rows':rows,'source_lines':lines,'events':events}
  assert reconstructed==expected[name],name
  receipts[name]={'prepared_sha256':digest,'bytes':len(raw),'nonempty_stripped_lines':lines,'events':events,'contexts':len(rows),'all_counts_equal':True}
 receipt={'status':'PASS_INDEPENDENT_EXTERNAL_MODEL_REPLAY','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'stage':'Post-result auxiliary verification; sourcemodel inputs fixed before native1380run. This author had seen native result summary before this replay.','native_data_read':False,'pack_payload_published':False,'new_corpus_or_normalization':False,'method':'Independent character-level vowel/empty-word removal and batch trigram counting with twoBOS per originalnonemptyline. No primary/old193imports; all6preparedbytehashes and every integer modelcount reproduced.','controls':['Empty strippedwords create no spuriousseparator','Whitespacecollapsed only between retainedwords','BOSreset eachoriginalnonemptyline'],'packs':receipts,'input_hashes':{'gdt001_language_pack_manifest.json':hashlib.sha256(manifest_path.read_bytes()).hexdigest(),'experiments/yolo/gdt1380_consonantal_context_cost_bound/artifacts/MODEL_COUNTS.json.gz':hashlib.sha256(artifact_path.read_bytes()).hexdigest()},'validator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
 (B/'artifacts/SOURCE_MODEL_VALIDATION.json').write_text(json.dumps(receipt,indent=2)+'\n')
 print(json.dumps({'status':receipt['status'],'packs':{k:{'contexts':v['contexts'],'events':v['events']} for k,v in receipts.items()}}))
if __name__=='__main__':main()
