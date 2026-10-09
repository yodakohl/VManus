"""Post-result mathematical consequences; no native payload or new target count."""
import hashlib,itertools,json,datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
BASE=Path(__file__).resolve().parent
EXP=ROOT/'experiments/yolo/gdt1269_space_free_pair_table_capacity'
def pairs(s,phase,h=None):
    result=set();i=phase
    while i<len(s):
        if h is not None and s[i]==h:i+=1
        elif i+1<len(s):result.add((s[i],s[i+1]));i+=2
        else:break
    return result
def required(s,h=None):return pairs(s,0,h)&pairs(s,1,h)
def main():
    manifest=json.loads((EXP/'experiment.json').read_text())
    src=EXP/'artifacts/RESULT.json';entry=next(x for x in manifest['outputs'] if x['path']==str(src.relative_to(ROOT)))
    assert hashlib.sha256(src.read_bytes()).hexdigest()==entry['sha256']
    old=json.loads(src.read_text());assert old['pair_entry_cap']==32 and old['status']=='ALL_SMALL_PAIR_TABLES_EXCLUDED'
    bounds={r['reader']:min(c['mandatory_pair_count'] for c in r['cases']) for r in old['reports']}
    assert bounds=={'IT2a':70,'ZL3b':72}
    assert all(min(c['mandatory_pair_count'] for c in r['cases'] if c['marker'] is not None)>64 for r in old['reports'])
    checked=0
    for n in range(9):
        for s in itertools.product('ab',repeat=n):
            for phase in (0,1):
                assert pairs(s[::-1],phase)=={(b,a) for a,b in pairs(s,phase^(n%2))}
            assert required(s[::-1])=={(b,a) for a,b in required(s)};checked+=1
    assert required('abha','h')==set()
    assert required('ahba','h')=={('b','a')}
    result={'status':'POST_RESULT_ALIAS_AND_NONE_REVERSAL_CONSEQUENCES','recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'original_decision_retained':old['status'],'new_native_count':False,'new_native_access':False,'new_experiment_or_preregistration_claim':False,'inherited_lower_bounds':bounds,'alias_consequence':{'pair_coded_source_units_at_most':32,'fixed_pair_spellings_per_unit_at_most':2,'maximum_pair_dictionary':64,'excluded_each_reader':{r:L>64 for r,L in bounds.items()},'proof':'The union of at most32sets of at most2pairs has size at most64. Shared spellings can only reduce the union. Any selection policy between these same pairs leaves this bound unchanged.','scope':'Any extra pair-coded letters, names, punctuation, controls or literal escapes count toward the same total inventory. Only the single optional h code remains separately allowed under1269. The choice may vary arbitrarily; the fixed union of spellings may not.'},'none_reversal':{'applies_only_to':'NO_SINGLETON all-two-unit code family; reversal of entire snippets/stream only, not separate words or physical lines','proof':'For a snippet of length n, reversing it and every pair sends phase p to p xor(n mod2). Therefore pair reversal maps P0 intersect P1 bijectively to the reversed snippet intersection; it commutes with union across snippets and preserves the bound.','synthetic_binary_strings_checked':checked,'bounds_unchanged':bounds,'marker_counterexample':{'marker':'h','forward':'abha','forward_required':[],'reverse':'ahba','reverse_required':[['b','a']],'scope':'No reversal conclusion for the singleton-control family. Reversal changes prefix-style no-pair-starts-h to a suffix-style condition.'}},'source_free_review':'bounded_idea_supply independently confirmed the union bound, phase-parity reversal and h-family limitation by messages before this arithmetic/synthetic check; no native counts by reviewer.','limits':['Original1269registered32-entry decision unchanged;64-entry exclusion is an explicit later algebraic consequence, not a rerun or a fitted capacity repair.','Does not exclude all homophony, changing contextual codebooks, more code entries, variable widths or different working units.','Does not identify32sounds,70/72native letters, a language or any word meaning.','1202concerned up to2WHOLE-WORD aliases on4fixedsources, not these pair-coded source units; its result is separate.','No proof that every viable cipher must have3spellings per letter; the conditional bound cannot choose a surviving architecture.'],'bindings':{str(src.relative_to(ROOT)):entry['sha256'],str((EXP/'REPORT.md').relative_to(ROOT)):hashlib.sha256((EXP/'REPORT.md').read_bytes()).hexdigest(),str(Path(__file__).relative_to(ROOT)):hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}}
    (BASE/'PAIR_SCOPE_20261007.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'bounds':bounds,'alias_cap':64,'binary_reversal_controls':checked,'marker_reversal_counterexample':True}))
if __name__=='__main__':main()
