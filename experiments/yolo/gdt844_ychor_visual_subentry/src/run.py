import hashlib,json
from pathlib import Path
from urllib.request import urlopen
E=Path(__file__).resolve().parents[1]
def get(url):
    with urlopen(url,timeout=30) as r:return r.read()
url='https://collections.library.yale.edu/manifests/2002046'
raw=get(url); manifest=json.loads(raw); rows=[]
for page in json.loads((E/'src/SPEC.json').read_text())['pages']:
    matches=[c for c in manifest['items'] if c['label'].get('none')==[page[1:]]]
    assert len(matches)==1,(page,len(matches))
    c=matches[0]; key=c['id'].rsplit('/',1)[-1]
    image_url=f'https://collections.library.yale.edu/iiif/2/{key}/full/1600,/0/default.jpg'
    data=get(image_url); (E/'runtime').mkdir(exist_ok=True)
    (E/'runtime'/f'{page}.jpg').write_bytes(data)
    rows.append(dict(page=page,canvas_label=c['label'],canvas_id=key,url=image_url,sha256=hashlib.sha256(data).hexdigest(),bytes=len(data)))
(E/'artifacts/SOURCES.json').write_text(json.dumps(dict(manifest_url=url,manifest_sha256=hashlib.sha256(raw).hexdigest(),images=rows),indent=2)+'\n')
print(json.dumps(rows))
