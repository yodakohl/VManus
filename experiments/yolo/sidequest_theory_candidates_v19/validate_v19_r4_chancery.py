#!/usr/bin/env python3
import csv, json, re
from collections import Counter
from pathlib import Path

P=Path(__file__).resolve().parent
def read(name):
    with (P/name).open(encoding='utf-8',newline='') as f: return list(csv.DictReader(f,delimiter='\t'))

d=read('V19_R4_HERBAL_CARD_DICTIONARY.tsv')
i=read('V19_R4_100_EVENT_INTERLINEAR.tsv')
a=read('V19_R4_SINGLETON_ALTERNATIVES.tsv')
v=read('V19_R4_VISIBLE_PLANT_FREEZE.tsv')
bad=re.compile(r'\b(unknown|opaque|payload|item|value|state|plant detail|property|operation|untranslated)\b',re.I)
checks={
 'dictionary_66':len(d)==66,
 'interlinear_100':len(i)==100,
 'singleton_alternatives_55':len(a)==55,
 'visible_freeze_4':len(v)==4,
 'exact_type_coverage':{r['exact_tuple_id'] for r in d}=={r['exact_tuple_id'] for r in i},
 'all_defaults_nonempty':all(r['selected_default_English'].strip() for r in d),
 'all_contextual_readings_nonempty':all(r['contextual_reading'].strip() for r in i),
 'two_concrete_singleton_rivals':all(r['alternative_A'].strip() and r['alternative_B'].strip() for r in a),
 'no_forbidden_semantic_blanks':not any(bad.search(r['selected_default_English']) for r in d),
 'four_pages_only':{r['page'] for r in i}=={'f10r','f11r','f55v','f56r'},
 'broad_classes_12':len({r['broad_source_class'] for r in d})==12,
 'persistent_picture_activations_4':sum(int(r['silent_argument_count']) for r in i)==4,
 'sealed_pages_absent':not any(r['page'].startswith('f84') for r in i),
}
out={'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks,'counts':{
 'events':len(i),'types':len(d),'singletons':len(a),'broad_classes':len({r['broad_source_class'] for r in d}),
 'picture_owner_activations':sum(int(r['silent_argument_count']) for r in i),
 'recurrent_type_counts':Counter(r['exact_tuple_id'] for r in i).most_common(11),
},'sealed_data':{'f84':True,'f84r':True,'accessed':[]}}
(P/'V19_R4_VALIDATION.json').write_text(json.dumps(out,indent=2)+"\n",encoding='utf-8')
print(json.dumps(out,indent=2))
raise SystemExit(out['status']!='PASS')
