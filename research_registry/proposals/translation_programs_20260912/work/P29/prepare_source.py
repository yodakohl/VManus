"""Manual complete clause inventory of the public 1925 transcription, read before comparison."""
import json
from pathlib import Path
D=Path('research_registry/proposals/translation_programs_20260912/work/P29')
raw=[
('GOAL','INK','NA','Gute Tinte herstellen','Si vis facere bonum atramentum sive tinctam bonam'),
('TAKE','WATER','12 librae Regenwasser','Regenwasser nehmen','accipe de aqua pluviali libras xij.'),
('TAKE','GALLS','2 librae Gallen','Gallen nehmen','et de gallis libras ij.,'),
('WET','GALLS+WATER','abends bis morgens; dieselben Gallen und dasselbe Regenwasser','Gallen in Regenwasser einweichen','et in sero pone dictas gallas in aquam pluvialem predictam temperando usque ad mane,'),
('HEAT','GALLS+WATER','Kochen; Wasser bis zur Hälfte verbraucht','Gemeinsam kochen bis Halbvolumen','et fac bulire simul tantum ita quod aqua ilia consumetur usque ad mediam partem ;'),
('FILTER','WATER1','sehr gut durch feines Tuch; erste Filtration','Flüssigkeit abseihen','deinde cola illam aquam optime per pannum subtile,'),
('HEAT','WATER1','dieselbe Flüssigkeit zurück ans Feuer, kein Ruhenlassen','Filtrat ans Feuer zurückstellen','deinde repone dictam aquam ad ignem,'),
('TAKE','GUM','4 unciae arabisches Gummi','Gummi nehmen','et accipe de gumma arabica uncias iiij.'),
('HEAT','GUM+WATER1','zusammen kochen bis Gummi aufgelöst','Gummi mit Flüssigkeit kochen','et dimitte bulire cum aqua predicta donee gumma liquefacta fuerit.'),
('FILTER','WATER2','erneut; zweite Filtration','Erneut abseihen','Et iterum cola eam,'),
('TAKE','WINE','1 libra guter weißer klarer Wein','Wein nehmen','postea accipe de vino bono albo et claro libram unam'),
('TAKE','VITRIOL','3 unciae Vitriol; Portaltext schreibt très','Vitriol nehmen','et de vitriolo uncias très'),
('MIX','WINE+VITRIOL','beide gut miteinander','Wein und Vitriol vermischen','et bene distempera pariter,'),
('HEAT','WINE+VITRIOL+WATER2','kurz kochen mit vorheriger Flüssigkeit','Mischung mit Flüssigkeit kurz kochen','et fac illud bulire aliquantulum cum aqua predicta'),
('FILTER','INK','erneut gut; dritte Filtration','Zum dritten Mal abseihen','et iterum cola bene,'),
('RESULT','INK','gute Tinte','Ergebnis Tinte','et erit bonum atramentum.')]
rows=[dict(id=f'S{i:02}',order=i,family=f,material=m,conditions=c,meaning=g,latin=l) for i,(f,m,c,g,l) in enumerate(raw)]
(D/'HISTORICAL_CLAUSES.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
(D/'HISTORICAL_TEXT.txt').write_text(' '.join(r['latin'] for r in rows)+'\n')
(D/'HISTORICAL_PROVENANCE.json').write_text(json.dumps({'url':'https://www.persee.fr/doc/bec_0373-6237_1925_num_86_1_460583','title':"Recette d’encre du XIVe siècle",'publication':'Bibliothèque de l’École des chartes 86 (1925), p.484','manuscript':'BnF latin8651, f88v','source_scope':'Complete Latin recipe printed on that single page; French editorial introduction excluded from recipe, not omitted recipe content','read_date':'2026-09-12','capture':'Manual transcription of complete public portal text into16 contiguous clauses; not a new manuscript collation. Portal OCR spellings donee and très retained.','interpretive_limit':'WATER1/WATER2 are stages of continuing liquid, not separate invented starting ingredients; repone ad ignem is reheat, not rest.','copyright':'Medieval Latin text in1925 publication; source attribution retained'},ensure_ascii=False,indent=2)+'\n')
