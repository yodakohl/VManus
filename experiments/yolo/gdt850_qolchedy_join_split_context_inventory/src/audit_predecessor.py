"""Post-count exposition audit; not a preregistered outcome test."""
import hashlib,json,re
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
c=json.loads((E/'artifacts/PREDECESSOR_COMPARISON.json').read_text());hits=json.loads((E/'artifacts/HITS.json').read_text())
p=ROOT/c['prior_target_source'];old=set(re.findall(r'^## (f[0-9]+[rv](?:[0-9]+)?\.[0-9]+)$',p.read_text(),re.M));new={h['locus'] for h in hits}
assert old==set(c['old_target_loci']);assert new==set(c['new_target_loci'])
assert new-old==set(c['newly_outside_old_target_list']);assert old-new==set(c['old_only'])
assert c['same_line_case']==[h for h in hits if h['locus']=='f75v.44']
for ed in ['ZL3b','IT2a']:assert {h['surface'] for h in c['same_line_case'] if h['edition']==ed}=={'JOINED','SPLIT'}
(E/'artifacts/PREDECESSOR_VALIDATION.json').write_text(json.dumps(dict(status='PASS_POST_COUNT_TARGET_LIST_AND_SAME_LINE_AUDIT',source=c['prior_target_source'],source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),prior_loci=len(old),current_loci=len(new),newly_outside=len(new-old)),indent=2)+'\n')
print('PASS')
