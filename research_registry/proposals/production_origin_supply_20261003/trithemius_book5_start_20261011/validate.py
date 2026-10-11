from pathlib import Path
import hashlib,json
B=Path(__file__).resolve().parent;R=B.parents[3]
def main():
 for p,h in json.loads((B/'LOCK.json').read_text())['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 r=json.loads((B/'RESULT.json').read_text());t=json.loads((B.parent/'trithemius_book5_20261011/TABLE.json').read_text());lookups=[dict(zip(t['source_alphabet'],t['source_alphabet']))]+[dict(zip(t['source_alphabet'],t['columns_black'][str(i)])) for i in range(1,6)];assert r['source']=='huncca' and r['printed_cipher']=='hxpfgf';assert len(r['trace'])==6
 for i,x in enumerate(r['trace']):assert x=={'position':i+1,'source':'huncca'[i],'alphabet':'ordinary' if i==0 else 'expanded_'+str(i),'written':lookups[i]['huncca'[i]],'printed_cipher':'hxpfgf'[i]}
 assert ''.join(lookups[i][c] for i,c in enumerate('huncca'))==r['written']=='hxpfgf' and r['prefix_matches'];assert r['main_transposed_count']+r['ordinary_alphabets_added']==r['total_count']==24 and r['final_page_additional_examples']==2;assert not r['identity_position_explicit_in_caption'] and not r['full_example_replayed'] and not r['native_data_used'];assert t['columns_black']['4'][t['source_alphabet'].index('r')]=='y' and t['columns_black']['4'][t['source_alphabet'].index('s')]=='x'
 out={'status':'PASS','literal_prefix_pairs':6,'previous_table_departures_retained':2,'scope':'Sourcehash and six conditional lookups only; doesnotprove initialphase instruction or completeauthorrecovery.'};(B/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
if __name__=='__main__':main()
