"""Post-result disclosure of every fixed marker interval and original member."""
from common import *
import csv,collections

def table(name,rows):
    with (A/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)

def main():
    original=read(A/'ORIGINAL_CERTIFICATES.json');saved=read(A/'SAVED_CERTIFICATES.json');codes={r['id']:r['code'] for r in read(A/'ORIGINAL_CANDIDATES.json')}
    rows=[];markers=[]
    for r in original:
        rows.append(dict(candidate=r['id'],original=r['original'],variant=r['variant_index'],prediction='Every THEN requires n>previously_certified',status=r['status'],exact_whole_code=json.dumps(codes[r['original']],sort_keys=True,separators=(',',':')),observed_intervals=json.dumps(r['certificate']['markers'],separators=(',',':')),independent_meaning_capacity=0))
    table('ORIGINAL_PREDICTIONS.tsv',rows)
    rows=[]
    for r in saved:
        bad=[m for m in r['certificate']['markers'] if not m['valid']]
        rows.append(dict(source=r['source'],case=r['case'],engine=r['engine'],context=r['context'],status=r['status'],markers=len(r['certificate']['markers']),empty_intervals=len(bad),first_failed_clause=bad[0]['clause'] if bad else '',first_failed_groups=(str(bad[0]['start']+1)+'-'+str(bad[0]['end'])) if bad else '',independent_meaning_capacity=0))
        for m in r['certificate']['markers']:markers.append(dict(source=r['source'],case=r['case'],engine=r['engine'],clause=m['clause'],group=m['start']+1,previously_certified=m['previously_certified'],completed=m['completed'],interval=','.join(map(str,m['interval'])),valid=m['valid']))
    table('SAVED_RESULTS.tsv',rows);table('ALL_MARKER_INTERVALS.tsv',markers)
    summary=dict(original_settings=len(original),original_coherent=sum(r['status']=='COHERENT' for r in original),original_interval_classes=sorted({json.dumps([m['interval'] for m in r['certificate']['markers']]) for r in original}),saved_maps=len(saved),saved_failed=sum(not r['certificate']['valid'] for r in saved),all_saved_markers=len(markers),empty_saved_intervals=sum(not r['valid'] for r in markers),full_result=read(A/'RESULT.json'),execution=read(A/'EXECUTION_RECEIPT.json'),validation=read(A/'VALIDATION.json'))
    put('SUMMARY.json',summary);print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
