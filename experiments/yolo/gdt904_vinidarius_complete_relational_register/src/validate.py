#!/usr/bin/env python3
from pathlib import Path
import subprocess,sys
E=Path(__file__).resolve().parents[1]
subprocess.run([sys.executable,str(E/'src/validate_source.py')],check=True)
