import argparse,hashlib,json,re
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2];PAT=re.compile(r'@167;|@168;')
def enc(x):return json.dumps(x,sort_keys=True,separators=(',',':'))+'\n'
def save(n,x,check=False):
 p=E/'artifacts'/n
 if check:assert p.read_text()==enc(x),n
 else:p.write_text(enc(x))
def mentions(raw):return [(m.start(),m.group()) for m in PAT.finditer(raw)]
def leaf(p):return re.match(r'f[0-9]+',p)[0]
def controls():
 assert mentions('@1670; @167 @168x;')==[];assert mentions('x@168;y@167;@168;')==[(1,'@168;'),(7,'@167;'),(12,'@168;')];assert mentions('abc')==[];assert mentions('[@168;:@167;]')==[(1,'@168;'),(7,'@167;')]
 return dict(status='PASS',controls=['exact_entity_prefix_rejection','multiple_mentions','unmatched','offset_order','alternative_mentions_preserved'])
def analyze(s,data):
 hits=[];lines=[];summary={}
 for ed,source in data.items():
  assert source['group_columns']==s['group_columns']
  for li,line in enumerate(source['lines']):
   m=line['metadata'];assert m['page'] in s['allowed_selectors'] and not m['page'].startswith('f84');assert m['edition']==ed;local=[]
   for g in line['groups']:
    assert len(g)==5
    for offset,entity in mentions(g[2]):
     h=dict(edition=ed,source_line_index=li,metadata=m,source_group_id=g[0],source_group_index=g[1],raw_group=g[2],left_separator=g[3],right_separator=g[4],raw_char_offset=offset,entity=entity,raw_annotation_characters=sorted(set(g[2]) & set('[]{}?!*<>:')),physical_leaf=leaf(m['page']),outside_known_locus=m['locus']!=s['known_locus']);hits.append(h);local.append(h)
   if local:lines.append(dict(edition=ed,source_line_index=li,line=line,ordered_mentions=local,both_entities_mentioned={h['entity'] for h in local}==set(s['entities']),outside_known_locus=m['locus']!=s['known_locus']))
  hh=[h for h in hits if h['edition']==ed];oo=[h for h in hh if h['outside_known_locus']];ll=[l for l in lines if l['edition']==ed]
  summary[ed]=dict(entity_counts={e:sum(h['entity']==e for h in hh) for e in s['entities']},total_mentions=len(hh),distinct_loci=sorted({h['metadata']['locus'] for h in hh}),physical_leaf_keys=sorted({h['physical_leaf'] for h in hh}),outside_entity_counts={e:sum(h['entity']==e for h in oo) for e in s['entities']},outside_total_mentions=len(oo),outside_loci=sorted({h['metadata']['locus'] for h in oo}),outside_leaf_keys=sorted({h['physical_leaf'] for h in oo}),same_line_both_mention_loci=[l['line']['metadata']['locus'] for l in ll if l['both_entities_mentioned']],annotated_raw_group_mention_count=sum(bool(h['raw_annotation_characters']) for h in hh))
 result=dict(status='ADDITIONAL_TEXT_LOCATORS_ONLY' if any(h['outside_known_locus'] for h in hits) else 'SOURCE_LOCAL_ONLY_NO_TRANSFER_PANEL',summary=summary,total_mentions=len(hits),hit_bearing_reader_lines=len(lines))
 return hits,lines,result
def main():
 p=argparse.ArgumentParser();p.add_argument('--controls',action='store_true');p.add_argument('--check',action='store_true');a=p.parse_args()
 if a.controls:save('CONTROLS.json',controls());print('CONTROLS PASS');return
 s=json.loads((E/'src/SPEC.json').read_text());data={}
 for ed,q in s['sources'].items():
  raw=(ROOT/q['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==q['sha256'];data[ed]=json.loads(raw)
 hits,lines,result=analyze(s,data)
 for n,v in [('HITS.json',hits),('SOURCE_LINES.json',lines),('RESULT.json',result)]:save(n,v,a.check)
 print(enc(result))
if __name__=='__main__':main()
