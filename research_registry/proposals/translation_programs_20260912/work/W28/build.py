from pathlib import Path
E=Path(__file__).resolve().parent
for model in ['Q','A']:
 exec(compile((E/'engine.py').read_text(),'W28_engine','exec'),{'__file__':str(E/'engine.py'),'SHOL_MODEL':model})
