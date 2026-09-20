"""Post-run proof summaries, with no changed source, writer, or target selection."""
import collections,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];A=E/'artifacts'
cs=json.loads((A/'CASES.json').read_text());out=[]
def starts_nine(words):
    possible=[]
    for k in range(1,len(words[0])+1):
        v=words[0][:k];wi=off=0
        for _ in range(9):
            if wi==len(words) or not words[wi].startswith(v,off):break
            off+=len(v)
            if off==len(words[wi]):wi+=1;off=0
        else:possible.append(v)
    return possible
for c in cs:
    if c['status']=='UNKNOWN_SOURCE':reason='UNKNOWN_SOURCE'
    elif c['characters']<192:reason='NONEMPTY_ATOM_LENGTH'
    elif c['groups']>192:reason='WORD_SEAM_CAPACITY'
    elif c['empty_initial_domains']:reason='EMPTY_NECESSARY_ATOM_DOMAIN'
    else:reason='COMPLETE_CODE_ENUMERATION'
    row=dict(index=c['index'],edition=c['edition'],paragraph=c['paragraph'],writer=c['writer'],classification=reason)
    if c['writer']=='PREFIX' and c['status']!='UNKNOWN_SOURCE':
        row['nine_initial_SEQ_possible_codes']=starts_nine(c['words'])
        assert not row['nine_initial_SEQ_possible_codes']
    out.append(row)
result=dict(status='PASS',scope='Post-run explanation of unchanged registered failures, not a new test or source repair',mutually_exclusive_case_counts=dict(collections.Counter(r['classification'] for r in out)),prefix_nine_SEQ_short_proofs=sum('nine_initial_SEQ_possible_codes' in r for r in out),rows=out)
(A/'FAILURE_EXPLANATIONS.json').write_text(json.dumps(result,separators=(',',':'))+'\n');print(json.dumps({k:v for k,v in result.items() if k!='rows'},indent=2))
