#!/usr/bin/env python3
import json,hashlib,urllib.request
from pathlib import Path
from PIL import Image
E=Path(__file__).resolve().parents[1];R=E.parents[2]
def main():
 s=json.loads((E/'src/SOURCE.json').read_text());p=R/s['image_path']
 if not p.exists():
  p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(urllib.request.urlopen(s['image_url'],timeout=45).read())
 for path,sha in json.loads((E/'PREREG_LOCK.json').read_text())['files'].items():assert hashlib.sha256((R/path).read_bytes()).hexdigest()==sha,path
 assert Image.open(p).size==(s['width'],s['height'])
 a=json.loads((E/'artifacts/ROOT_OBSERVATION.json').read_text());b=json.loads((E/'artifacts/OBSERVER_B.json').read_text())
 result={'experiment':'GDT921','status':'PARTIAL_SOURCE_TOPOLOGY_NO_OWNED_VALUES','four_figures_agree':a['gates']['four_humans'] and b['gates']['four_human_figures'],'two_offset_registers_agree':a['gates']['four_figure_adjacent_register'] and a['gates']['separate_four_offset_register'] and b['gates']['fourfold_adjacent_register'] and b['gates']['separate_fourfold_offset_register'],'complete_source_capacity':a['capacity'] and b['gates']['complete_source_topology_capacity'],'target_binding':False,'confirmed_meanings':0,'root_month_ring_description':'WITHDRAWN; source annulus zodiac names, see POSTFREEZE_AUDIT.json','observation_hashes':{str(q.relative_to(R)):hashlib.sha256(q.read_bytes()).hexdigest() for q in [E/'artifacts/ROOT_OBSERVATION.json',E/'artifacts/OBSERVER_B.json']}}
 (E/'artifacts/RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
