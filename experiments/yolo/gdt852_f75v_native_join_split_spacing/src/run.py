import hashlib,json
from pathlib import Path
from urllib.request import urlopen
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
def save(n,x):(E/'artifacts'/n).write_text(json.dumps(x,sort_keys=True,separators=(',',':'))+'\n')
def get(u):
 with urlopen(u,timeout=45) as r:return r.read()
u='https://collections.library.yale.edu/manifests/2002046';raw=get(u);manifest=json.loads(raw)
cs=[c for c in manifest['items'] if c['label'].get('none')==['75v']];assert len(cs)==1
c=cs[0];key=c['id'].rsplit('/',1)[-1];url=f'https://collections.library.yale.edu/iiif/2/{key}/full/full/0/default.jpg';data=get(url)
(E/'runtime/f75v.jpg').write_bytes(data)
save('SOURCES.json',dict(manifest_url=u,manifest_sha256=hashlib.sha256(raw).hexdigest(),page='f75v',canvas_id=key,label=c['label'],source_width=c['width'],source_height=c['height'],url=url,sha256=hashlib.sha256(data).hexdigest(),bytes=len(data)))
page=[]
for ed in ['ZL3b','IT2a','RF1b']:
 p=ROOT/f'experiments/yolo/gdt851_primitive_tandem_raw_group_discovery/artifacts/SOURCE_{ed}.json';d=json.loads(p.read_text());page.append(dict(edition=ed,group_columns=d['group_columns'],lines=[x for x in d['lines'] if x['metadata']['page']=='f75v']))
save('SOURCE_PAGE.json',page)
d=page[0];line=[x for x in d['lines'] if x['metadata']['locus']=='f75v.44'];assert len(line)==1
rr=[dict(zip(d['group_columns'],g)) for g in line[0]['groups']];lookup={int(x['source_group_index']):x['ivtff_group_raw'] for x in rr}
for t in json.loads((E/'src/SPEC.json').read_text())['targets']:assert [lookup[i] for i in t['indices']]==t['expected']
print('Source photograph and fixed-page lossless contexts saved.')
