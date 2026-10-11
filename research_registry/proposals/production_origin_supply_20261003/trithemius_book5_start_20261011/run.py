from pathlib import Path
import hashlib,json
B=Path(__file__).resolve().parent;R=B.parents[3]
def main():
 for p,h in json.loads((B/'LOCK.json').read_text())['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 t=json.loads((B.parent/'trithemius_book5_20261011/TABLE.json').read_text());o=json.loads((B/'OBSERVATIONS.json').read_text());a=t['source_alphabet'];source=o['prefix_probe']['source_visible'].lower().replace(' ','');target=o['prefix_probe']['cipher_visible'].lower().replace(' ','');trace=[]
 for i,c in enumerate(source):
  out=c if i==0 else t['columns_black'][str(i)][a.index(c)];trace.append({'position':i+1,'source':c,'alphabet':'ordinary' if i==0 else 'expanded_'+str(i),'written':out,'printed_cipher':target[i]})
 written=''.join(x['written'] for x in trace);out={'status':'ORDINARY_ALPHABET_SOURCE_SUPPORTED_PREFIX_AGREES_CONDITIONALLY','main_transposed_count':23,'ordinary_alphabets_added':1,'total_count':24,'final_page_additional_examples':2,'identity_position_explicit_in_caption':False,'source':source,'written':written,'printed_cipher':target,'prefix_matches':written==target,'trace':trace,'full_example_replayed':False,'native_data_used':False};(B/'RESULT.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
if __name__=='__main__':main()
