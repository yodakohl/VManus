#!/usr/bin/env python3
"""Run the frozen diagnostic and normalize only trailing Markdown whitespace."""
from pathlib import Path
import subprocess,sys
e=Path(__file__).resolve().parents[1]
subprocess.run([sys.executable,str(e/'src/run.py')],check=True)
p=e/'artifacts/FULL_READER.md'
p.write_text(p.read_text().rstrip()+'\n')
