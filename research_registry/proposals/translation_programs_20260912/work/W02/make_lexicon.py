"""Serialize explicitly authored whole-word hypotheses; this is not a decoder."""
import csv,json
from pathlib import Path
E=Path(__file__).resolve().parent
# Every meaning below is an authored, unconfirmed development choice.
first={
'ychor':('ferner','LINK'), 'tchody':('Bereitung','HEADING'), 'shocthol':('benetztes Krautpulver','MATERIAL'),
's':('jeweils','DISTRIBUTIVE'),'ychos':('zerkleinere','ACTION'),'ychol':('trockne','ACTION'),
'daiin':('Dosis Q','AMOUNT'),'cthol':('Krautpulver','MATERIAL'),'dol':('Portion','AMOUNT'),
'chor':('Blüten','MATERIAL'),'okchey':('zerstoße fein','ACTION'),'qokom':('erwärme portionsweise','ACTION'),
'oeeo':('miss ab','ACTION'),'dal':('Maß','AMOUNT'),'cthom':('Kräuterportion','MATERIAL'),
'qokchod':('trockne vollständig','ACTION'),'ychear':('vermische','MIX'),'kchdy':('feines Pulver','MATERIAL'),
'lor':('mit','RELATION'),'char':('Blütenanteil','MATERIAL'),'otam':('Ansatzmasse','MATERIAL'),
'ctho':('Krautmehl','MATERIAL'),'m':('danach','LINK'),'dy':('fertig','STATE'),
'shy':('feucht','STATE'),'qokam':('erwärme','ACTION'),'cthy':('Kraut','MATERIAL'),
'yodaiin':('weitere Dosis Q','AMOUNT'),'oees':('gemischt','STATE'),'or':('Anteil','AMOUNT'),
'qokor':('erhitze','ACTION'),'chol':('trocken','STATE'),'tchalody':('fein gesiebt','STATE'),
'chockhy':('vermische','MIX'),'chy':('heiß','STATE'),'ain':('Maßzahl P','NUMBER'),'ar':('Teil','AMOUNT'),
'ochy':('kühle','ACTION'),'cthar':('kleine Kräuterportion','MATERIAL'),'y':('und','LINK'),
'chaies':('weich','STATE'),'ckhal':('presse aus','ACTION'),'cthodam':('Kräuterrückstand','MATERIAL'),
'ytchocthol':('benetztes Krautmehl','MATERIAL'),'ches':('stampfe','ACTION'),'ocholy':('trockenes Feinmehl','MATERIAL'),
'kchos':('zerreibe','ACTION'),'dor':('abgemessene Menge','AMOUNT'),'dchor':('Blütenportion','MATERIAL'),
'choldar':('Trockenanteil','MATERIAL'),'okol':('Grundansatz','MATERIAL'),'ycheor':('zum Schluss','LINK'),
'octham':('bewahre auf','ACTION')}
# Further explicit whole-word assumptions used across the twelve other complete paragraphs.
extra={
'ol':('mit','RELATION'),'aiin':('Maßzahl Q','NUMBER'),'oky':('warm','STATE'),'otaiin':('Dosis des kühlen Ansatzes','AMOUNT'),
'cheor':('Auszug','MATERIAL'),'chey':('prüfe','ACTION'),'oty':('kühl','STATE'),'okeol':('warme Flüssigkeit','MATERIAL'),
'okeey':('erwärme vorsichtig','ACTION'),'ckhy':('stampfe','ACTION'),'odaiin':('zusätzliche Dosis Q','AMOUNT'),
'dar':('Teilmenge','AMOUNT'),'shol':('feucht','STATE'),'r':('darauf','LINK'),'sho':('Flüssigkeit','MATERIAL'),
'shody':('benetztes Material','MATERIAL'),'kchol':('Trockenmaterial','MATERIAL'),'qokeey':('erhitze anhaltend','ACTION'),
'otor':('kühler Anteil','MATERIAL'),'cthor':('Krautanteil','MATERIAL'),'dain':('Dosis P','AMOUNT'),
'cheey':('zerreibe fein','ACTION'),'al':('davon','REFERENCE'),'okey':('erwärmt','STATE'),'chody':('getrocknetes Material','MATERIAL'),
'otal':('kühles Ausgangsmaterial','MATERIAL'),'okal':('Ausgangsmaterial','MATERIAL'),'sor':('weiterer Bestandteil','LINK'),
'sy':('abgesetzt','STATE'),'sheol':('feuchtes Gemenge','MATERIAL'),'chodaiin':('Dosis Q des Trockenmaterials','AMOUNT'),
'cheo':('Zubereitung','MATERIAL'),'ykeey':('erwärme erneut','REPEAT_ACTION'),'tchor':('verarbeitetes Blütenmaterial','MATERIAL'),
'qotchy':('seihe ab','ACTION'),'dam':('Restmenge','AMOUNT'),'qokchy':('mische ein','MIX'),'sar':('je Teil','DISTRIBUTIVE'),
'o':('und','LINK'),'ody':('Endprodukt','MATERIAL'),'ykaiin':('erwärmte Dosis Q','AMOUNT'),'oar':('Anteil davon','AMOUNT'),
'shodaiin':('Dosis Q des feuchten Materials','AMOUNT'),'qokeor':('erhitze den Auszug','ACTION_TYPED'),
'qotor':('kühle ab','ACTION'),'odol':('abgemessene Zubereitung','MATERIAL'),'choy':('grob','STATE'),
'qo':('nimm','ACTION'),'qokcho':('verarbeite warm','ACTION'),'kaiin':('Wärmestufe Q','QUALITY_VALUE'),
'odal':('abgemessener Anteil','AMOUNT'),'keeor':('Feinauszug','MATERIAL'),'kchor':('trockene Blüten','MATERIAL'),
'tchol':('getrockneter Anteil','MATERIAL'),'okaiin':('Dosis des Grundansatzes','AMOUNT'),
'chkeey':('zerreibe vollständig','ACTION'),'os':('zusammen','DISTRIBUTIVE'),'ycheol':('danach','LINK'),
'okeor':('warmer Auszug','MATERIAL'),'oteol':('kühle Flüssigkeit','MATERIAL'),'she':('lasse stehen','ACTION'),
'cheeor':('geklärter Auszug','MATERIAL'),'chr':('Blütenrest','MATERIAL'),'ctheey':('Krautzubereitung','MATERIAL'),
'qotol':('kalter Ansatz','MATERIAL'),'ytar':('weiterer Teil','AMOUNT'),'ytaiin':('weitere Dosis des kühlen Ansatzes','AMOUNT'),
'qokchol':('erwärmtes Trockenmaterial','MATERIAL'),'qokol':('erwärmter Grundansatz','MATERIAL'),
'por':('Zubereitungsmenge','AMOUNT'),'cheol':('flüssige Zubereitung','MATERIAL'),'cthal':('Kräuterstück','MATERIAL'),
'qotar':('abgeteilter Anteil','AMOUNT'),'cho':('Inneres','REGION'),'qoky':('erwärme mäßig','ACTION'),
'qokeol':('erhitzte Flüssigkeit','MATERIAL'),'qokain':('erwärmte Dosis P','AMOUNT'),'tol':('kühles Material','MATERIAL'),
'tod':('kalter Rest','MATERIAL'),'sham':('feuchte Masse','MATERIAL'),'yteey':('kühle erneut','REPEAT_COOL'),
'qokar':('erwärmter Anteil','MATERIAL'),'sheo':('feuchte Zubereitung','MATERIAL'),
'pchor':('nimm','ACTION'),'chshoty':('kühl-feuchtes Material','MATERIAL'),'chory':('frische Blüten','MATERIAL'),
'ols':('Endzubereitung','MATERIAL'),'sheeor':('wässriger Auszug','MATERIAL'),'shekeey':('weiche ein','ACTION'),
'teody':('abgekühlt','STATE'),'shor':('Samen','MATERIAL'),'dair':('Teilmenge R','AMOUNT'),
'sheey':('benetze','ACTION'),'qoteedy':('vollständig abgekühlt','STATE'),'oteedy':('kühle vollständig','ACTION')}
assert not(set(first)&set(extra))
for form in ['otaiin','chodaiin','ykaiin','okaiin','ytaiin','qokain','shodaiin']:
 meaning,_=extra[form];extra[form]=(meaning,'MATERIAL_DOSE')
src=json.loads((E/'SOURCE.json').read_text());loci={}
for t in src['targets']:
 for p in t['hosts']['ZL3b']:
  for l in p['lines']:
   for i,w in enumerate(l['words'],1):loci.setdefault(w,[]).append(l['locus']+':'+str(i))
with (E/'LEXICON.tsv').open('w') as f:
 out=csv.writer(f,delimiter='\t',lineterminator='\n');out.writerow(['form','hypothesis','role','origin','loci','status'])
 for form,(meaning,role) in sorted((first|extra).items()):
  assert form in loci,form
  out.writerow([form,meaning,role,'W01' if form=='ychor' else 'W02 first paragraph authored' if form in first else 'W02 common extension authored',';'.join(loci[form]),'UNCONFIRMED_ASSUMPTION'])
print('Authored dictionary:',len(first),'first;',len(extra),'extension;',len(first|extra),'total')
