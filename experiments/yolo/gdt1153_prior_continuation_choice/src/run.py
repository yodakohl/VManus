import collections
import hashlib
import importlib.util
import json
import re
from pathlib import Path

E = Path(__file__).resolve().parents[1]
R = E.parents[2]

def dump(name, value):
    (E / 'artifacts' / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def main():
    lock = json.loads((E / 'PREREG_LOCK.json').read_text())
    for path, expected in lock['files'].items():
        assert hashlib.sha256((R / path).read_bytes()).hexdigest() == expected, path
    path = R / 'experiments/yolo/gdt927_chor_continuation_full_context_audit/src/run.py'
    spec = importlib.util.spec_from_file_location('unchanged927', path)
    old = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(old)
    data = old.load()
    candidates = json.loads((R / 'experiments/yolo/gdt926_repeated_context_continuation_atlas/artifacts/CANDIDATES_ZL3b.json').read_text())
    assert len(candidates) == 13
    assert sum(len(c['occurrences']) for c in candidates) == 26
    rows, contexts = [], {}
    for reader, lines in data.items():
        by_id = {l['id']: l for l in lines}
        for candidate in candidates:
            competitors = sorted(b['next'] for b in candidate['branches'])
            assert len(competitors) == 2
            anchor = candidate['anchor']
            for occurrence in candidate['occurrences']:
                line_id, chosen = occurrence['line'], occurrence['next']
                row = dict(reader=reader, context_id=candidate['id'], anchor=anchor,
                           line=line_id, chosen=chosen, competitors=competitors,
                           original_start=occurrence['start'], leaf=occurrence['leaf'])
                rows.append(row)
                line = by_id.get(line_id)
                sequence = anchor + [chosen]
                matches = [] if line is None else [i for i in range(len(line['words'])-len(sequence)+1) if line['words'][i:i+len(sequence)] == sequence]
                row['matches'] = matches
                if line is None or len(matches) != 1 or not line['literal_line']:
                    row.update(status='UNTESTABLE', reason='NATIVE_TRIPLE_NOT_UNIQUE_OR_HOST_UNCERTAIN')
                    if line is not None: row['host_line'] = line
                    continue
                start = matches[0]
                if reader == 'ZL3b': assert start == occurrence['start']
                paragraph = old.paragraph(lines, line['metadata']['locus'])
                key = reader + '|' + paragraph['lines'][0]['id'] + '--' + paragraph['lines'][-1]['id']
                context = {k: v for k, v in paragraph.items() if k != 'seed'}
                if key in contexts: assert contexts[key] == context
                contexts[key] = context
                row['paragraph_key'] = key
                prefix, reliability = [], True
                for prior_line in paragraph['lines']:
                    n = start if prior_line['id'] == line_id else len(prior_line['words'])
                    words = prior_line['words'][:n]
                    reliability &= all(re.fullmatch('[a-z]+', w) is not None for w in words)
                    reliability &= all(prior_line['seams'][:max(0,n-1)])
                    prefix.extend(dict(word=w, group_id=g, line=prior_line['id']) for w,g in zip(words,prior_line['group_ids'][:n]))
                    if prior_line['id'] == line_id: break
                row['prefix_groups'] = len(prefix)
                row['prefix_reliable'] = bool(reliability)
                row['earlier'] = {w: [dict(item, distance_to_anchor=len(prefix)-i) for i,item in enumerate(prefix) if item['word']==w] for w in competitors}
                row['counts'] = {w: len(row['earlier'][w]) for w in competitors}
                if not paragraph['complete_marked_paragraph']:
                    row.update(status='UNTESTABLE', reason='NO_COMPLETE_MARKED_PARAGRAPH')
                elif not reliability:
                    row.update(status='UNTESTABLE', reason='UNCERTAIN_PRIOR_SCOPE')
                else:
                    present = [w for w in competitors if row['counts'][w] > 0]
                    if len(present) != 1:
                        row.update(status='ABSTAIN', reason='BOTH_PREVIOUS' if present else 'NEITHER_PREVIOUS')
                    else:
                        predicted = present[0]
                        row.update(predicted=predicted, status='COMPATIBLE' if predicted == chosen else 'CONTRADICTION', reason='EXACTLY_ONE_PREVIOUS')
    summaries = {}
    for reader in data:
        panel = [r for r in rows if r['reader']==reader]
        counts = dict(collections.Counter(r['status'] for r in panel))
        summaries[reader] = dict(cases=len(panel), counts=counts,
            reasons=dict(collections.Counter(r['reason'] for r in panel)),
            physical_leaves=len({r['leaf'] for r in panel}),
            choice_leaves=len({r['leaf'] for r in panel if r['status'] in ('COMPATIBLE','CONTRADICTION')}),
            complete_paragraphs=len({r['paragraph_key'] for r in panel if 'paragraph_key' in r and contexts[r['paragraph_key']]['complete_marked_paragraph']}),
            decision='CONTRADICTED' if counts.get('CONTRADICTION') else 'LOCALLY_COMPATIBLE' if counts.get('COMPATIBLE') else 'NO_CHOICE_CAPACITY')
    result = dict(status='FIXED_PRIOR_CONTINUATION_CHOICE_COMPLETE', panels=summaries,
                  primary_case_count=26, readers_are_alternatives=True,
                  independent_confirmation=0, meanings_identified=0, significance_claim=False)
    dump('CASES.json', rows)
    dump('PARAGRAPHS.json', contexts)
    dump('RESULT.json', result)
    table = ['# All fixed continuation choices', '', 'Counts concern only the complete paragraph prefix before the shared context. Uncertain prefixes are not scored. Readers are alternatives.', '', '|Reader|Context|Locus|Chosen|Competing earlier counts|Prediction|Outcome|Reason|', '|---|---|---|---|---|---|---|---|']
    for row in rows:
        counts = ', '.join(w+':'+str(n) for w,n in row.get('counts',{}).items()) or 'unavailable'
        table.append('|'+ '|'.join([row['reader'],row['context_id'],row['line'].split('|')[1],row['chosen'],counts,row.get('predicted','—'),row['status'],row['reason']]) +'|')
    (E / 'CANDIDATE_TABLE.md').write_text('\n'.join(table)+'\n')
    whole = ['# Complete contexts and explicitly unbounded contexts', '',
             'Original groups retained. These are transcriber paragraphs, not established sentences.', '']
    for key, paragraph in sorted(contexts.items()):
        whole += ['## ' + key, '', 'Complete marked paragraph: ' + str(paragraph['complete_marked_paragraph']), '', '```text']
        whole += [line['metadata']['locus'] + ': ' + ' '.join(line['words']) for line in paragraph['lines']]
        whole += ['```', '']
    (E / 'WHOLE_CONTEXTS.md').write_text('\n'.join(whole).rstrip() + '\n')
    print(json.dumps(result, indent=2))

if __name__ == '__main__': main()
