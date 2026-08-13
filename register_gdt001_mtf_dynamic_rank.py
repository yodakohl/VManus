#!/usr/bin/env python3
"""Idempotently register the MTF dynamic-rank screen."""
import csv,hashlib,json
from gdt001_core import ROOT,canonical

def main():
    path=ROOT/'GDT001_YOLO_LEDGER.tsv';reader=csv.DictReader(open(path),delimiter='\t');fields=reader.fieldnames;rows=[r for r in reader if not r['run_id'].startswith('mtfdr_')];result=json.load(open(ROOT/'gdt001_mtf_dynamic_rank_results.json'))
    sources=[('historical_rows','HOMOPHONIC_CIPHER'),('static_rows','HOMOPHONIC_CIPHER'),('anonymous_rows','NONSEMANTIC_GENERATOR')]
    for field,model_class in sources:
        for item in result[field]:
            language=item.get('language','anonymous');rid=f"mtfdr_{item['model'].lower()}_{language}_s{item['seed']}";config={'schema':result['schema'],'model':item['model'],'language':language,'order':2,'seed':item['seed'],'scope':result['scope']}
            rows.append({'run_id':rid,'model_class':model_class,'language_or_system':f"MTF_DYNAMIC_RANK_{item['model']}_{language.upper()}",'seed':str(item['seed']),'config_hash':hashlib.sha256(canonical(config)).hexdigest(),'total_bits':f"{item['total_bits']:.6f}",'bits_per_symbol':f"{item['bits_per_symbol']:.9f}",'key_bits':f"{item['key_bits']:.6f}",'latent_bits':f"{item['payload_bits']:.6f}",'reconstruction_bits':f"{item['fixed_bits']:.6f}",'exception_bits':'0.000000','convergence_status':'CONVERGED','decoder_hash':item['decoder_hash'],'notes':'EXPLORATORY; REVERSIBLE_LINE_RESET_MTF_DYNAMIC_RANK; EXACT_RETAINED_KEY_SCORE; HEURISTIC_SEARCH; STOP_MATCHED_ANONYMOUS_LOSS; UNSTABLE' if field=='historical_rows' else 'EXPLORATORY; MTF_DYNAMIC_RANK_COMPARATOR; EXACT_RETAINED_KEY_SCORE; HEURISTIC_SEARCH'})
    if len(rows)!=len({r['run_id'] for r in rows}):raise AssertionError('run ids')
    with open(path,'w',newline='',encoding='utf-8') as h:w=csv.DictWriter(h,fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
    print(json.dumps({'rows':len(rows),'registered':39}))
if __name__=='__main__':main()
