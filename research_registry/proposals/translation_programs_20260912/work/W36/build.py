from pathlib import Path
E=Path(__file__).resolve().parent
for candidate,nominals in [('P',['chocthy']),('K',['cthaiin']),('PK',['chocthy','cthaiin'])]:
 for sm in ['Q','A']:
  exec(compile((E/'engine.py').read_text(),'W36_engine','exec'),{'__file__':str(E/'engine.py'),'SHOL_MODEL':sm,'NOMINALS':nominals,'RUN_ID':candidate+'_'+sm})
