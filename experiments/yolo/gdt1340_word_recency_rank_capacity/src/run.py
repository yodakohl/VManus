from pathlib import Path
from collections import defaultdict
import gzip,hashlib,json,re
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def main():
 for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 strict=read(R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz');edges=read(R/'experiments/yolo/gdt1314_binary_line_edge_capacity/artifacts/EDGES.json.gz');prior=read(R/'research_registry/proposals/production_origin_supply_20261003/BINARY_WORD_RANK_BOUND_20261011.json');out={}
 for ed,rows in sorted(strict.items()):
  mandatory=prior['readers'][ed]['required_one_drawings'];assert set(mandatory)<={r['units'][0] for r in rows};keys=[c['necessary_zero_set'] for c in prior['readers'][ed]['necessary_candidates_not_validated_keys']];panels={}
  for name,panel in [('STRICT',rows),('STRICT_PLUS_EDGES',rows+edges[ed])]:
   panel=sorted(panel,key=lambda r:r['id']);assert len({r['id'] for r in panel})==len(panel);cases=[]
   for zero in keys:
    bad=[{'id':r['id'],'raw':r['ivtff_group_raw'],'page':r['page']} for r in panel if r['units'][0] in zero];rec={'zero':zero,'head_violations':bad,'valid':not bad}
    if not bad:
     ranks=[int(''.join('0' if u in zero else '1' for u in r['units']),2) for r in panel];mx=max(ranks);idx=ranks.index(mx);fol=defaultdict(int)
     for r,v in zip(panel,ranks):f=re.match(r'f(\d+)',r['page']).group(1);fol[f]=max(fol[f],v)
     vals=sorted(fol.values(),reverse=True);rec.update(required_dictionary_size=mx,maximum_witness={'id':panel[idx]['id'],'raw':panel[idx]['ivtff_group_raw'],'units':panel[idx]['units'],'rank':mx},folio_maxima=dict(sorted(fol.items(),key=lambda t:int(t[0]))),second_folio_maximum=vals[1] if len(vals)>1 else None)
    cases.append(rec)
   good=[c for c in cases if c['valid']];L=max(len(r['units']) for r in panel);panels[name]={'groups':len(panel),'max_units':L,'elementary_length_bound':2**(L-1),'keys':cases,'surviving_zero_sets':[c['zero'] for c in good],'minimum_required_dictionary_size':min((c['required_dictionary_size'] for c in good),default=None),'minimum_second_folio_maximum':min((c['second_folio_maximum'] for c in good),default=None),'status':'CANONICAL_HEAD_EXCLUDED' if not good else 'NECESSARY_DICTIONARY_COST_ONLY'}
  out[ed]=panels
 result={'status':'READER_SPECIFIC_CANONICAL_HEAD_AND_DICTIONARY_BOUND','readers':out,'ceiling':'Necessary fixed-binary wordbook capacity only; no native decoding, dictionary selection, cost threshold or meaning.'};(B/'artifacts/RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 for ed,ps in out.items():
  for name,p in ps.items():print(ed,name,p['status'],p['surviving_zero_sets'],p['minimum_required_dictionary_size'],p['minimum_second_folio_maximum'],p['max_units'])
if __name__=='__main__':main()
