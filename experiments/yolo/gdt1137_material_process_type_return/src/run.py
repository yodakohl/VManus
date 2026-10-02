from pathlib import Path
import runpy
p=Path(__file__).with_name("author.py")
if p.exists():
    runpy.run_path(str(p),run_name="__main__")
else:
    print("REGISTERED_AUTHOR_NOT_RELEASED")
