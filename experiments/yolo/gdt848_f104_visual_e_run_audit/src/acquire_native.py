"""Pre-observation acquisition amendment; all original query logic preserved."""
from pathlib import Path
p=Path(__file__).with_name('run.py')
s=p.read_text()
a="/{s['image_width']},/0/default.jpg"
assert s.count(a)==1
exec(compile(s.replace(a,"/full/0/default.jpg"),str(p),'exec'),dict(__file__=str(p),__name__='__main__'))
