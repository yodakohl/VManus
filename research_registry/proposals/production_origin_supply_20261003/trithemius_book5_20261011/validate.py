from pathlib import Path
import hashlib,json
B=Path(__file__).resolve().parent;R=B.parents[3]
def main():
 for p,h in json.loads((B/'LOCK.json').read_text())['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 t=json.loads((B/'TABLE.json').read_text());r=json.loads((B/'RESULT.json').read_text());a=t['source_alphabet'];assert ''.join(a)=='abcdefghiklmnopqrstuxyzw';lookup={};n=0;diff=[]
 for j in range(1,6):
  col=t['columns_black'][str(j)];inverse={c:a[i] for i,c in enumerate(col)};assert len(inverse)==24
  expected=a[j:]+a[:j]
  for i,src in enumerate(a):
   out=col[i];lookup[j,src]=out;assert inverse[out]==src;n+=1
   if out!=expected[i]:diff.append({'column':j,'source':src,'printed':out,'cyclic_expected':expected[i]})
 assert diff==r['literal_departures']==[{'column':4,'source':'r','printed':'y','cyclic_expected':'x'},{'column':4,'source':'s','printed':'x','cyclic_expected':'y'}];assert n==r['pairs']==120 and r['cyclic_matches']==118 and r['columns_are_permutations']==[True]*5
 assert ''.join(lookup[i+1,c] for i,c in enumerate('hunc'))==r['literal_first_four_columns_output']=='iyqg';assert r['printed_cipher_prefix_casefolded']=='hxpf' and not r['initial_literal_replay_matches'];assert r['status']=='PARTIAL_TABLE_COLLATED_AUTHOR_START_UNRESOLVED'
 out={'status':'PASS','literal_pairs_checked':120,'inverse_pairs_checked':120,'cyclic_departures_retained':2,'author_start_mismatch_retained':True,'scope':'Arithmetic/provenance only. Manual readings remain informed visual judgments; source phase not repaired, no full historical/nativereplay.'};(B/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
if __name__=='__main__':main()
