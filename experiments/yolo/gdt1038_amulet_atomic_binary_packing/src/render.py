"""Render complete public tables from frozen alternatives and checked results."""
import csv
import json
from pathlib import Path

ART = Path(__file__).resolve().parents[1] / 'artifacts'
table = json.loads((ART / 'ALL_ALTERNATIVES.json').read_text())
result = json.loads((ART / 'RESULT.json').read_text())
occurrences = {}
forms = {row['raw']: row['analyses'] for row in table['inventory']}
for unit in table['units']:
    for block in unit['blocks']:
        for group in block['groups']:
            occurrences.setdefault(group['raw'], []).append(group['source_id'])
            forms[group['raw']] = group['analyses']
with (ART / 'SURFACE_ALTERNATIVES.tsv').open('w') as stream:
    writer = csv.writer(stream, delimiter='\t', lineterminator='\n')
    writer.writerow(['raw','dictionary_entry','all_parts','all_tags','all_occurrence_ids'])
    for raw, analyses in sorted(forms.items()):
        writer.writerow([raw, raw in table['lexicon'], json.dumps([a['parts'] for a in analyses]),
            json.dumps([a['tags'] for a in analyses]), ';'.join(occurrences.get(raw, []))])
unit = next(u for u in table['units'] if u['id'] == 'EXTENSION_IT2a')
mode = next(u for u in result['units'] if u['id'] == unit['id'])['modes']['ATOMIC_OR_BINARY']
assert mode['count'] == 1, 'Linear presentation requires exactly one complete path'
with (ART / 'EXTENSION_IT_COMPLETE_ALIGNMENT.tsv').open('w') as stream:
    writer = csv.writer(stream, delimiter='\t', lineterminator='\n')
    writer.writerow(['source_id','raw','parts','terminal_positions','unchanged_tags','unchanged_meanings'])
    for edge in mode['blocks'][0]['edges']:
        group = unit['blocks'][0]['groups'][edge['group_index']]
        writer.writerow([group['source_id'], group['raw'], ' + '.join(edge['parts']),
            ','.join(str(i+1) for i in range(edge['terminal_start'], edge['terminal_end'])),
            ' + '.join(edge['tags']), ' | '.join(table['lexicon'][p]['meaning'] for p in edge['parts'])])
