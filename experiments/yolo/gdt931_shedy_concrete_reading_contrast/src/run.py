"""Fixed whole-word candidate display and complete local consequences; no decoder."""
import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import io
import json
from pathlib import Path

EXP = Path(__file__).resolve().parents[1]
ROOT = EXP.parents[2]
ART = EXP / 'artifacts'
EDS = ['ZL3b', 'IT2a', 'RF1b']
PAGES = ['f77r', 'f17r', 'f21r', 'f32v', 'f29v']


def tsv(rows):
    out = io.StringIO()
    w = csv.DictWriter(out, fieldnames=list(rows[0]), delimiter='\t', lineterminator='\n')
    w.writeheader(); w.writerows(rows)
    return out.getvalue()


def build():
    lock = json.loads((EXP / 'PREREG_LOCK.json').read_text())
    for name, digest in lock['files'].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, name
    model = json.loads((EXP / 'src/MODEL.json').read_text())
    prior = json.loads((ROOT / model['prior_model']).read_text())
    rows = json.loads((ROOT / model['source']).read_text())['groups']
    rows = sorted(rows, key=lambda r: (EDS.index(r['edition']), PAGES.index(r['page']),
                                     int(r['locus'].split('.')[1]), int(r['source_group_index'])))
    bases = {p['base']: p['id'] for p in prior['pairs']}
    marked = {p['marked']: p['id'] for p in prior['pairs']}
    nouns = bases | marked
    lines, blocks = defaultdict(list), defaultdict(list)
    for r in rows:
        number = int(r['locus'].split('.')[1])
        frame = [i for i, (lo, hi) in enumerate(prior['paragraph_frames'][r['page']], 1)
                 if lo <= number <= hi] if r['kind'] == 'P' else []
        assert r['kind'] != 'P' or len(frame) == 1
        r = dict(r, block=f"{r['page']}:P{frame[0]}" if frame else r['locus'] + ':LABEL')
        lines[r['edition'], r['locus']].append(r)
        blocks[r['edition'], r['block']].append(r)
    alignment, cases, attachments = [], [], []
    for (ed, bid), rr in blocks.items():
        for i, r in enumerate(rr):
            raw = r['ivtff_group_raw']
            left = rr[i-1] if i and r['kind'] == 'P' else None
            right = rr[i+1] if i+1 < len(rr) and r['kind'] == 'P' else None
            a = {k:r[k] for k in ('source_group_id','edition','page','locus','kind','block',
                                  'source_group_index','ivtff_group_raw','left_separator','right_separator')}
            for mid, gloss in model['readings'].items():
                a[mid] = gloss+'?' if raw == model['target'] else nouns[raw]+'?' if raw in nouns else '⟦'+raw+'⟧'
            alignment.append(a)
            if raw == model['target']:
                case = dict(a)
                for side, neighbor in [('left',left),('right',right)]:
                    case[side+'_id'] = neighbor['source_group_id'] if neighbor else ''
                    case[side+'_raw'] = neighbor['ivtff_group_raw'] if neighbor else ''
                    case[side+'_nominal'] = nouns.get(case[side+'_raw'],'')
                    case[side+'_cross_line'] = bool(neighbor and neighbor['locus'] != r['locus'])
                case['full_raw_line'] = ' '.join(x['ivtff_group_raw'] for x in lines[ed,r['locus']])
                case['semantic_participant_confirmed'] = False
                cases.append(case)
            if raw in marked and r['kind'] == 'P':
                for direction, neighbor in [('LEFT',left),('RIGHT',right)]:
                    head = neighbor['ivtff_group_raw'] if neighbor else ''
                    status = ('BOUNDARY' if neighbor is None else 'MARKED_HEAD' if head in marked
                              else 'SHEDY_HYPOTHESIS' if head == model['target']
                              else 'BASE_HYPOTHESIS' if head in bases else 'UNTRANSLATED_HEAD')
                    attachments.append({'edition':ed,'source_group_id':r['source_group_id'],
                        'locus':r['locus'],'raw':raw,'direction':direction,
                        'head_id':neighbor['source_group_id'] if neighbor else '', 'head_raw':head,
                        'cross_line':bool(neighbor and neighbor['locus'] != r['locus']), 'status':status})
    result = {'experiment':'GDT931','status':'CONCRETE_SHEDY_HYPOTHESES_UNDERDETERMINED',
              'editions':{},'candidate_meanings':model['readings'], 'selected_translation':None,
              'source_groups':len(rows),'confirmed_words':0,'independent_meaning_tests':0,
              'new_admissions':0,'reserved_pages_opened':False,
              'visual_relation_evidence_added':False,'statistical_significance_claimed':False,
              'lexical_rendering_is_not_complete_clause':True}
    out = {'ALIGNMENT.tsv':tsv(alignment),'SHEDY_CASES.tsv':tsv(cases),'ATTACHMENTS.tsv':tsv(attachments)}
    for ed in EDS:
        aa = [a for a in alignment if a['edition'] == ed]
        cc = [c for c in cases if c['edition'] == ed]
        result['editions'][ed] = {'source_groups':len(aa),'shedy_occurrences':len(cc),
            'shedy_by_page':dict(Counter(c['page'] for c in cc)),
            'candidate_positions':sum(a['ivtff_group_raw'] in nouns or a['ivtff_group_raw']=='shedy' for a in aa),
            'adjacent_nominated_nominal':sum(bool(c['left_nominal'] or c['right_nominal']) for c in cc),
            'directed_head_statuses':{d:dict(Counter(a['status'] for a in attachments if a['edition']==ed and a['direction']==d)) for d in ('LEFT','RIGHT')}}
        doc = [f'# GDT931 — {ed}: alle Quellzeilen und drei konstante shedy-Lesungen','',
               'A–D sind unübersetzte nominale Annahmen (Nennwertalternative aus GDT930).',
               'M=Flüssigkeit, V=fließt, A=feucht. Alle Wortwerte hypothetisch; keine eingefügten Teilnehmer.',
               'Die ? markieren Hypothesen, ⟦…⟧ bleibt ungelesen. Keine Übersetzung eines vollständigen Absatzes.','']
        for (reader, locus), rr in lines.items():
            if reader != ed: continue
            line = [a for a in aa if a['locus']==locus]
            raw = ''.join(('' if i==0 else ' / ' if 'UNCERTAIN' in r['left_separator'] else ' ')+r['ivtff_group_raw'] for i,r in enumerate(rr))
            doc += ['## '+locus+' — '+rr[0]['block'],'',f'`{raw}`','']
            for mid in model['readings']:
                doc += [mid+': '+' '.join(a[mid] for a in line),'']
        out[f'READING_{ed}.md'] = '\n'.join(doc).rstrip()+'\n'
    out['RESULT.json'] = json.dumps(result,indent=2,ensure_ascii=False)+'\n'
    return out


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--check',action='store_true')
    args = parser.parse_args()
    for name, content in build().items():
        if args.check: assert (ART/name).read_text() == content, name
        else: (ART/name).write_text(content)
    print((ART/'RESULT.json').read_text())


if __name__ == '__main__':
    main()
