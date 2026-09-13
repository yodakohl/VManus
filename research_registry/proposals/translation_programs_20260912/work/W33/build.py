from pathlib import Path
E=Path(__file__).resolve().parent
for candidate,nominals in [('O',['ol']),('L',['lor']),('OL',['ol','lor'])]:
 for sm in ['Q','A']:
  exec(compile((E/'engine.py').read_text(),'W33_engine','exec'),{'__file__':str(E/'engine.py'),'SHOL_MODEL':sm,'NOMINALS':nominals,'RUN_ID':candidate+'_'+sm})
