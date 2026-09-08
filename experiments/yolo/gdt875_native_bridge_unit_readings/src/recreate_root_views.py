# Retrospective source-view reproduction, not a preregistered scoring routine.
import json,hashlib
from pathlib import Path
from PIL import Image
B=Path(__file__).resolve().parents[1];R=B.parents[2]
s=json.loads((B/'artifacts/ROOT_VIEWS.json').read_text());ims={i['canvas_id']:i for i in s['source_images']}
for view in s['views']:
 source=ims[view['canvas_id']];p=R/source['cache_path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==source['sha256']
 if view['box_xyxy'] is None:continue
 with Image.open(p) as original:
  im=original.crop(tuple(view['box_xyxy']));rot=view['rotation_ccw_degrees']
  if rot:im=im.transpose({90:Image.Transpose.ROTATE_90,270:Image.Transpose.ROTATE_270}[rot])
  out=B/'runtime'/f"{view['name']}.png";out.parent.mkdir(exist_ok=True);im.save(out)
 assert hashlib.sha256(out.read_bytes()).hexdigest()==view['display_file_sha256']
print('Exact source rectangles reconstructed; native judgement not checked.')
