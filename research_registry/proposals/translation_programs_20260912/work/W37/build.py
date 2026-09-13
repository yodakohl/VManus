from pathlib import Path
E=Path(__file__).resolve().parent
for scope in ['S','I']:
 for sm in ['Q','A']:
  exec(compile((E/'engine.py').read_text(),'W37_engine','exec'),{'__file__':str(E/'engine.py'),'SHOL_MODEL':sm,'NOMINALS':['chocthy','cthaiin'],'RUN_ID':scope+'_'+sm,'SCOPE':scope})
