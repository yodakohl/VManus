#!/usr/bin/env python3
"""Idempotently register the frozen-line-state key screen."""
import csv,hashlib,json
from gdt001_core import ROOT,canonical

def main():
    path=ROOT/'GDT001_YOLO_LEDGER.tsv';reader=csv.DictReader(open(path),delimiter='\t');fields=reader.fieldnames;rows=[r for r in reader if not r['run_id'].startswith('frozenlinekey_')];result=json.load(open(ROOT/'gdt001_frozen_line_state_keys_results.json'))
    for item in result['rows']:
        config={'schema':result['schema'],'key_count':item['key_count'],'seed':item['seed'],'scope':result['scope'],'state_decoder_hash':item['decoder']['frozen_state_decoder_hash']};rows.append({'run_id':f"frozenlinekey_k{item['key_count']}_s{item['seed']}",'model_class':'HYBRID','language_or_system':f"FROZEN_LINE_STATE_K{item['key_count']}_MIDDLE_HIGH_GERMAN",'seed':str(item['seed']),'config_hash':hashlib.sha256(canonical(config)).hexdigest(),'total_bits':f"{item['total_bits']:.6f}",'bits_per_symbol':f"{item['bits_per_symbol']:.9f}",'key_bits':f"{item['key_bits']:.6f}",'latent_bits':f"{item['frozen_state_bits']+item['language_and_reverse_bits']+item['rare_side_bits']:.6f}",'reconstruction_bits':f"{item['fixed_bits']:.6f}",'exception_bits':'0.000000','convergence_status':'CONVERGED','decoder_hash':item['decoder_hash'],'notes':'EXPLORATORY; FROZEN_LATENTLINE_K2_STATE_PATH; ONE_OR_TWO_HOMOPHONIC_KEYS; EXACT_RETAINED_MAP_SCORE; HEURISTIC_SEARCH; MATCHED_ANONYMOUS_LOSS; UNSTABLE'})
    if len(rows)!=len({r['run_id'] for r in rows}):raise AssertionError('run ids')
    with open(path,'w',newline='',encoding='utf-8') as h:w=csv.DictWriter(h,fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
    print(json.dumps({'rows':len(rows),'registered':len(result['rows'])}))
if __name__=='__main__':main()
