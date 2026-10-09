from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime, timezone
import gzip, json, hashlib, importlib.util
from engine import weighted

D = Path('experiments/yolo/gdt1236_prefix_proof_support'); A = D/'artifacts'

def main():
    s = json.loads((D/'src/SPEC.json').read_text())
    lock = json.loads((A/'REGISTRATION_LOCK.json').read_text())
    for path, expected in lock['files'].items():
        assert hashlib.sha256(Path(path).read_bytes()).hexdigest() == expected, path
    spec = importlib.util.spec_from_file_location('old_prefix_summary',s['old_engine'])
    old = importlib.util.module_from_spec(spec); spec.loader.exec_module(old)
    groups = json.loads(gzip.decompress(Path(s['source']).read_bytes()))
    previous = json.loads(Path(s['previous']).read_text())
    out = {'status':'COMPLETE_SUPPORT_DIAGNOSTIC','outcome_utc':datetime.now(timezone.utc).isoformat(),'readers':{}}
    for reader in s['readers']:
        rows = groups[reader]
        counts = Counter(tuple(r['units']) for r in rows)
        pages = defaultdict(set)
        for r in rows: pages[tuple(r['units'])].add(r['page'])
        records = {}
        for measure in s['measures']:
            source = dict(counts) if measure == 'occurrences' else {w:len(p) for w,p in pages.items()}
            cert = weighted(source, s['seconds_per_reader_measure'])
            weights = dict(zip(map(tuple,cert['universe']),cert['weights']))
            cuts = []
            for t in s['thresholds']:
                selected = {w for w,n in source.items() if n >= t}
                R = {w for w,n in weights.items() if n >= t}
                used = {a for w in selected for a in w}
                summary = old.summarize(R,used)
                if not selected:
                    summary['status'] = 'NO_RETAINED_WORDS'
                    summary['caps'] = {str(k): 'NOT_ASSESSABLE' for k in (22,26,28)}
                if t == 1: assert summary == previous['readers'][reader]['summary']
                F = set(summary['F'])
                cuts.append({'threshold':t,'retained_types':len(selected),'retained_tokens':sum(counts[w] for w in selected),
                    'closure_size':len(R),'summary':summary,
                    'all_original_tokens_using_only_forced_singletons':sum(n for w,n in counts.items() if set(w)<=F)})
            records[measure] = {'singleton_maximum_support':{w[0]:n for w,n in weights.items() if len(w)==1 and n>0},'thresholds':cuts}
            (A/('CERTIFICATE_'+reader+'_'+measure+'.json.gz')).write_bytes(gzip.compress(json.dumps(cert,separators=(',',':')).encode(),mtime=0))
        out['readers'][reader] = {'original_tokens':len(rows),'original_types':len(counts),'measures':records}
    (A/'RESULT.json').write_text(json.dumps(out,indent=2)+'\n')
    print({r:{m:v['singleton_maximum_support'] for m,v in rec['measures'].items()} for r,rec in out['readers'].items()})

if __name__ == '__main__': main()
