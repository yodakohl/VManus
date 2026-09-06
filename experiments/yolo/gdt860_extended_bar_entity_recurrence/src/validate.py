import argparse,hashlib,json,re
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
def findall(raw):
 found=[]
 for entity in ['@167;','@168;']:
  start=0
  while True:
   i=raw.find(entity,start)
   if i<0:break
   found.append((i,entity));start=i+len(entity)
 return sorted(found)
def main():
 p=argparse.ArgumentParser();p.add_argument('--controls',action='store_true');a=p.parse_args();assert findall('@1670; @167 @168x;')==[];assert findall('x@168;y@167;@168;')==[(1,'@168;'),(7,'@167;'),(12,'@168;')];assert findall('abc')==[];assert findall('[@168;:@167;]')==[(1,'@168;'),(7,'@167;')]
 if a.controls:print('INDEPENDENT CONTROLS PASS');return
 s=json.loads((E/'src/SPEC.json').read_text());expected=[];expected_lines=[];summary={}
 for ed,q in s['sources'].items():
  raw=(ROOT/q['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==q['sha256'];src=json.loads(raw);assert src['group_columns']==s['group_columns'];edhits=[];edlines=[]
  for idx,line in enumerate(src['lines']):
   meta=line['metadata'];assert meta['edition']==ed and meta['page'] in s['allowed_selectors'] and not meta['page'].startswith('f84');local=[]
   for row in line['groups']:
    assert len(row)==5
    for off,ent in findall(row[2]):
     assert row[2][off:off+len(ent)]==ent
     record=dict(edition=ed,source_line_index=idx,metadata=meta,source_group_id=row[0],source_group_index=row[1],raw_group=row[2],left_separator=row[3],right_separator=row[4],raw_char_offset=off,entity=ent,raw_annotation_characters=sorted(c for c in set(row[2]) if c in '[]{}?!*<>:'),physical_leaf=re.match(r'f\d+',meta['page'])[0],outside_known_locus=meta['locus']!='f56r.1');local.append(record)
   if local:
    record=dict(edition=ed,source_line_index=idx,line=line,ordered_mentions=local,both_entities_mentioned=all(any(h['entity']==ent for h in local) for ent in s['entities']),outside_known_locus=meta['locus']!='f56r.1');edlines.append(record)
   edhits.extend(local)
  expected.extend(edhits);expected_lines.extend(edlines);outside=[h for h in edhits if h['metadata']['locus']!='f56r.1']
  summary[ed]=dict(entity_counts={ent:len([h for h in edhits if h['entity']==ent]) for ent in s['entities']},total_mentions=len(edhits),distinct_loci=sorted(set(h['metadata']['locus'] for h in edhits)),physical_leaf_keys=sorted(set(h['physical_leaf'] for h in edhits)),outside_entity_counts={ent:len([h for h in outside if h['entity']==ent]) for ent in s['entities']},outside_total_mentions=len(outside),outside_loci=sorted(set(h['metadata']['locus'] for h in outside)),outside_leaf_keys=sorted(set(h['physical_leaf'] for h in outside)),same_line_both_mention_loci=[l['line']['metadata']['locus'] for l in edlines if l['both_entities_mentioned']],annotated_raw_group_mention_count=len([h for h in edhits if h['raw_annotation_characters']]))
 assert expected==json.loads((E/'artifacts/HITS.json').read_text());assert expected_lines==json.loads((E/'artifacts/SOURCE_LINES.json').read_text());r=dict(status='ADDITIONAL_TEXT_LOCATORS_ONLY' if any(h['outside_known_locus'] for h in expected) else 'SOURCE_LOCAL_ONLY_NO_TRANSFER_PANEL',summary=summary,total_mentions=len(expected),hit_bearing_reader_lines=len(expected_lines));assert r==json.loads((E/'artifacts/RESULT.json').read_text())
 v=dict(status='PASS',independent_literal_find=True,all_occurrences_source_checked=len(expected),lossless_hit_line_parity=True,scope_checked=True,controls='PASS');(E/'artifacts/VALIDATION.json').write_text(json.dumps(v,sort_keys=True,separators=(',',':'))+'\n');print(json.dumps(v))
if __name__=='__main__':main()
