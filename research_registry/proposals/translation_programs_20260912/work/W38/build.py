from pathlib import Path
E=Path(__file__).resolve().parent
for scope,quality_scope in [('P','PHYSICAL'),('C','CONSTITUTION')]:
 for sm in ['Q','A']:
  exec(compile((E/'engine.py').read_text(),'W38_engine','exec'),{'__file__':str(E/'engine.py'),'SHOL_MODEL':sm,'NOMINALS':['chocthy','cthaiin'],'RUN_ID':scope+'_'+sm,'SCOPE':'S','QUALITY_SCOPE':quality_scope})
