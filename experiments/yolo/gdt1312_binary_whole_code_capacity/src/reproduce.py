"""Run byte-frozen scientific programs with disposable scratch storage."""
import importlib.util
import sys
import tempfile
from pathlib import Path
sys.dont_write_bytecode = True
HERE=Path(__file__).resolve().parent
if len(sys.argv)!=2 or sys.argv[1] not in {'run','validate'}:
 raise SystemExit('usage: reproduce.py run|validate')
mode=sys.argv[1]
spec=importlib.util.spec_from_file_location('registered_binary_capacity_'+mode,HERE/(mode+'.py'))
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
with tempfile.TemporaryDirectory(prefix='vmanus_binary_whole_') as scratch:
 module.CACHE=Path(scratch)
 module.main()
