import importlib.util,hashlib,json
from pathlib import Path
from urllib.request import urlopen
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2];s=json.loads((E/'src/SPEC.json').read_text())
def get(u):
 with urlopen(u,timeout=45) as r:return r.read()
def save(n,x):(E/'artifacts'/n).write_text(json.dumps(x,sort_keys=True,separators=(',',':'))+'\n')
u='https://collections.library.yale.edu/manifests/2002046';raw=get(u);manifest=json.loads(raw);images=[]
for page in s['pages']:
 ms=[c for c in manifest['items'] if c['label'].get('none')==[page[1:]]];assert len(ms)==1
 c=ms[0];key=c['id'].rsplit('/',1)[-1];url=f"https://collections.library.yale.edu/iiif/2/{key}/full/{s['image_width']},/0/default.jpg";data=get(url)
 (E/'runtime'/f'{page}.jpg').write_bytes(data);images.append(dict(page=page,canvas_id=key,label=c['label'],source_width=c['width'],source_height=c['height'],url=url,sha256=hashlib.sha256(data).hexdigest(),bytes=len(data)))
save('SOURCES.json',dict(manifest_url=u,manifest_sha256=hashlib.sha256(raw).hexdigest(),images=images))
p=ROOT/'experiments/yolo/gdt829_repeated_passage_reflow_capacity/src/run.py';x=importlib.util.spec_from_file_location('guarded_reader',p);m=importlib.util.module_from_spec(x);x.loader.exec_module(m)
q=json.loads((ROOT/'experiments/yolo/gdt829_repeated_passage_reflow_capacity/src/SPEC.json').read_text());q['allowed_selectors']=s['pages'];rows,guard=m.query(q);loci={t['locus'] for t in s['targets']};contexts=[r for r in rows if r['locus'] in loci];save('CONTEXTS.json',contexts);save('GUARD.json',guard)
for t in s['targets']:
 rs=[r for r in contexts if r['edition']=='ZL3b' and r['locus']==t['locus'] and int(r['source_group_index'])==t['index']];assert len(rs)==1 and rs[0]['ivtff_group_raw']==t['expected']
print(json.dumps(images))
