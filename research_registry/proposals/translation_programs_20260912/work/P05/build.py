#!/usr/bin/env python3
"""Project authored P05 readings and derive their explicit, conditional references."""
import csv
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent

def tsv(name, fields, rows):
    with (HERE / name).open('w') as f:
        w = csv.DictWriter(f, fieldnames=fields, delimiter='\t', lineterminator='\n')
        w.writeheader()
        w.writerows(rows)

def main():
    source = HERE / 'PRODUCER_DRAFT.md'
    text = source.read_text()
    lex, aligned = {}, []
    locus = None
    for line in text.splitlines():
        m = re.fullmatch(r'### (f(?:29v|32v)\.\d+)', line)
        if m:
            locus = m[1]
        m = re.fullmatch(r'\| (\d+) \| `([^`]+)` \| (.*?) \|', line)
        if m:
            n, word, gloss = m.groups()
            aligned.append((locus, int(n), word))
            if not gloss.startswith('[unaufgelöst:'):
                assert word not in lex or lex[word] == gloss, (word, gloss)
                lex[word] = gloss
    inp = json.loads((HERE.parent / 'P09/INPUT.json').read_text())['lines']
    by_locus = {x['locus']: x for x in inp}
    for locus, n, word in aligned:
        assert by_locus[locus]['groups'][n-1] == word
    assert len(aligned) == 79 and len(set(aligned)) == 79 and len(lex) == 52
    # The corrected manually written extension must conserve exact whole forms.
    extension = []
    loc = None
    for line in (HERE / 'FOLLOWUP_v02.md').read_text().splitlines():
        m = re.fullmatch(r'### (f(?:17r|21r)\.\d+)', line)
        if m:
            loc = m[1]
        m = re.fullmatch(r'\| (\d+) \| `([^`]+)` \| (.*?) \|', line)
        if m:
            n, word, meaning = m.groups()
            assert by_locus[loc]['groups'][int(n)-1] == word
            assert meaning == lex.get(word, f'[unaufgelöst: {word}]')
            extension.append((loc, int(n), word))
    assert len(extension) == len(set(extension)) == 66
    assert sum(w in lex for _,_,w in extension) == 16
    changes = {'qotchy': 'siebe', 'qotcheaiin': 'abgetrenntes Feinpulver',
               'shan': 'Feinanteil', 'sy': 'abgesetzt'}
    dry = dict(lex, **changes)
    model = {'status': 'HYPOTHESES_ONLY', 'source': source.name,
             'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
             'v01': lex, 'v03': dry, 'changes_v03': changes}
    (HERE / 'MODELS.json').write_text(json.dumps(model, ensure_ascii=False, indent=2)+'\n')
    stats = {}
    for label, values in [('v01', lex), ('v03', dry)]:
        rows = []
        for line in inp:
            for n, word in enumerate(line['groups'], 1):
                rows.append({'locus': line['locus'], 'group_index': n, 'raw_group': word,
                             'hypothesis_meaning': values.get(word, f'[unaufgelöst: {word}]'),
                             'status': 'ASSUMED_NOT_CONFIRMED' if word in values else 'UNRESOLVED'})
        tsv('ALIGNMENT_'+label+'.tsv', list(rows[0]), rows)
        stats[label] = {'all_positions': len(rows), 'assumed_positions': sum(r['raw_group'] in values for r in rows),
                        'unresolved_positions': sum(r['raw_group'] not in values for r in rows),
                        'assumed_types': len(values)}
    lex_rows=[]
    for form, meaning in sorted(dry.items()):
        loci=[x['locus']+':'+str(i) for x in inp for i,w in enumerate(x['groups'],1) if w==form]
        lex_rows.append({'form':form,'reading_variant':'exposed ZL display',
                        'meaning_hypothesis':meaning,'sense_trigger':'same whole value at every occurrence',
                        'grammar_rule':'authored working value; no component export',
                        'all_working_loci':';'.join(loci),
                        'counterexamples':'See REPORT.md; all meanings remain hypotheses'})
    tsv('LEXICON_v03.tsv',list(lex_rows[0]),lex_rows)
    # Explicitly hypothesised independent materials; regions/measures remain separate.
    material_types = ['kooiin','shor','cthy','qotcheaiin','cthold','ytchor','okaiin',
                      'odan','otchol','ctho','qotaiin','shan','chocthy','cthaiin',
                      'sho','keol','chor','cthol']
    typed = {'material_forms': material_types,
             'excluded_region_forms': ['cho','otshcho'],
             'excluded_measure_forms': ['daiin','dain','dary','odaiin','ar'],
             'unknown_forms_policy': 'not typed; may invalidate nearest-material assumptions',
             'rule': 'XX distributes over last two distinct hypothesised material whole forms in mention order, within paragraph only',
             'scope': 'all three immediate doubled fields in HERB4; exposed construction, no held test'}
    (HERE / 'REFERENCE_RULE_v02.json').write_text(json.dumps(typed, ensure_ascii=False, indent=2)+'\n')
    references = []
    for page in ['f29v','f32v','f17r','f21r']:
        tokens = [(line['locus'],n,w) for line in inp if line['locus'].split('.')[0] == page
                  for n,w in enumerate(line['groups'],1)]
        memory=[]
        for i,(loc,n,word) in enumerate(tokens):
            if i+1 < len(tokens) and word == tokens[i+1][2]:
                assert word in {'chol','daiin'}, ('new unhandled doubled field',word)
                assert len(memory) >= 2
                a,b=memory[-2:]
                references.append({'locus':loc,'indices':f'{n},{tokens[i+1][1]}','doubled_form':word,
                                   'first_material':a[0],'first_material_locus':a[1],
                                   'second_material':b[0],'second_material_locus':b[1],
                                   'v01_first_meaning':lex[a[0]],'v01_second_meaning':lex[b[0]],
                                   'v03_first_meaning':dry[a[0]],'v03_second_meaning':dry[b[0]],
                                   'status':'CONDITIONAL_MODEL_DERIVATION_NOT_OBSERVED_REFERENTS'})
            if word in material_types:
                memory=[x for x in memory if x[0]!=word]
                memory.append((word,f'{loc}:{n}'))
    assert len(references)==3
    tsv('REFERENCE_v02.tsv',list(references[0]),references)
    result={'status':'PASS_SOURCE_GLOSS_STABILITY_AND_CONDITIONAL_REFERENCE_REPLAY',
            'models':stats,'original_projected_positions':79,'original_unresolved_positions':5,
            'extension_positions':66,'extension_assumed_positions':16,'extension_unresolved_positions':50,
            'doubled_fields':3,'v03_changed_whole_form_values':4,
            'semantic_truth_validated':False,'held_pages_opened':False}
    (HERE / 'VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    print(json.dumps(references,ensure_ascii=False,indent=2))

if __name__ == '__main__':
    main()
