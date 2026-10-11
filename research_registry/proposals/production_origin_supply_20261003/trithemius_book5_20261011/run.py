from pathlib import Path
import hashlib,json
B=Path(__file__).resolve().parent;R=B.parents[3]
def main():
 for p,h in json.loads((B/'LOCK.json').read_text())['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 t=json.loads((B/'TABLE.json').read_text());a=t['source_alphabet'];assert len(a)==len(set(a))==24;diff=[];perms=[]
 for label,col in t['columns_black'].items():
  k=int(label);assert len(col)==24;perms.append(set(col)==set(a))
  for i,(src,out) in enumerate(zip(a,col)):
   expected=a[(i+k)%24]
   if out!=expected:diff.append({'column':k,'source':src,'printed':out,'cyclic_expected':expected})
 plain='hunc';written=''.join(t['columns_black'][str(i+1)][a.index(c)] for i,c in enumerate(plain));actual=json.loads((B/'TRANSCRIPTION.json').read_text())['clavis_0027']['cipher_first_word'].lower()
 out={'status':'PARTIAL_TABLE_COLLATED_AUTHOR_START_UNRESOLVED','columns':5,'pairs':120,'columns_are_permutations':perms,'cyclic_matches':120-len(diff),'literal_departures':diff,'source_prefix_casefolded':plain,'literal_first_four_columns_output':written,'printed_cipher_prefix_casefolded':actual,'initial_literal_replay_matches':written==actual,'scope':'No full24alphabet collation, author-example decipherment, source correction or native test.'};(B/'RESULT.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
if __name__=='__main__':main()
