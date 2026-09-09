import argparse,pickle,struct
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--cache-dir',type=Path,required=True);a=p.parse_args()
with (a.cache_dir/'pattern_sets.bin').open('wb') as out:
 for v in 'aeiouy':
  with (a.cache_dir/('patterns_'+v+'.pkl')).open('rb') as f:index=pickle.load(f)
  out.write(struct.pack('<I',len(index)))
  for pat in sorted(index):
   out.write(struct.pack('<H',len(pat)));out.write(bytes(pat))
print('exported pattern sets')
