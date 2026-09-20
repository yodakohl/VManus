"""Source-only complete semantic hypothesis; no target file is read."""
import collections
import hashlib
import json
from pathlib import Path

E = Path(__file__).resolve().parents[1]
R = E.parents[2]
SOURCE = 'research_registry/work_batches/ten_hours_20260915/balneis_cache/ALIM553.txt'


def n(op, *args):
    return [op, *args]


def serialize(tree, order):
    if isinstance(tree, str):
        return [tree]
    children = [atom for child in tree[1:] for atom in serialize(child, order)]
    return [tree[0], *children] if order == 'PREFIX' else [*children, tree[0]]


def build():
    water = n('WATER_OF', 'BATH')
    body = n('BODY_OF', 'PERSON')
    spring = n('SOURCE_OF', water)
    trees = [
        n('ASSERT', n('ASCRIBE', 'PEOPLE', 'BATH', 'ANASTASIA')),
        n('ASSERT', n('PROVIDE', 'BATH', n('MANY', n('BENEFIT_FOR', 'HUMAN_USE')))),
        n('ASSERT', n('REFRESH', water, n('LIMBS_OF', n('AFFLICTED', body)))),
        n('ASSERT', n('ALSO', n('RENEW', water, n('POWERS_OF', body)))),
        n('ASSERT', n('REMARKABLE', n('WHEN', n('DIG', 'PERSON', 'SAND'),
            n('FLOW_AT', n('HOT', water), n('MIDDLE_OF', 'HOLE'))))),
        n('ASSERT', n('WHEN', n('AND', n('FRESH', water),
            n('AND', n('AT', water, spring),
            n('AND', n('AFFLICTED', 'PERSON'),
            n('ENDURE', 'PERSON', n('HEAT_OF', water))))),
            n('DISPEL', water, n('SYMPTOMS_OF', 'PERSON')))),
        n('ASSERT', n('WHEN', n('AWAY_FROM', water, spring),
            n('PROVIDE', water, n('ZERO', n('BENEFIT_FOR', 'PERSON'))))),
        n('ASSERT', n('WHEN', n('COOLED', water),
            n('PROVIDE', water, n('LITTLE', n('BENEFIT_FOR', 'PERSON'))))),
        n('ASSERT', n('THEREFORE', n('WHEN',
            n('AND', n('SEEK', 'PERSON', n('WELL', n('RELIEF_OF', n('ILLNESS_OF', 'PERSON')))),
                n('RENEW', 'PERSON', water)),
            n('FUTURE', n('EXPERIENCE', 'PERSON', n('HELP_FROM', water)))))),
    ]
    spans = [[123],[124],[125],[126],[127,128],[129,130],[131],[132],[133,134]]
    glosses = [
        'People ascribe this bath to Anastasia.',
        'The bath provides many benefits for human use.',
        'Its water refreshes the limbs of an afflicted body.',
        'The water also renews bodily powers.',
        'Remarkably, when a person digs the sand, hot water flows at the middle of that hole.',
        'When the water is fresh in its own spring and the afflicted recipient endures its heat, it dispels the recipient\'s symptoms.',
        'When removed from its spring, the water provides no benefit to the recipient.',
        'When cooled, the same bath water provides little benefit to the recipient.',
        'Therefore, when the recipient seeks good relief from their illness and renews the water, they will experience help from it.',
    ]
    raw = (R / SOURCE).read_text().splitlines()
    clauses = [dict(id=f'C{i+1}', source_lines=sp, source_exact=[raw[j-1] for j in sp],
                    provisional_gloss=g, tree=t)
               for i,(sp,g,t) in enumerate(zip(spans,glosses,trees))]
    arities = {'BEGIN_RECORD':0}
    def walk(t):
        symbol,arity = (t,0) if isinstance(t,str) else (t[0],len(t)-1)
        assert symbol not in arities or arities[symbol] == arity
        arities[symbol] = arity
        if isinstance(t,list):
            for c in t[1:]: walk(c)
    for t in trees: walk(t)
    streams = {}
    for order in ('PREFIX','POSTFIX'):
        seq = ['BEGIN_RECORD']
        align = [dict(index=0,atom='BEGIN_RECORD',clause=None,source_lines=[])]
        for c in clauses:
            for a in serialize(c['tree'],order):
                align.append(dict(index=len(seq),atom=a,clause=c['id'],source_lines=c['source_lines']))
                seq.append(a)
        streams[order] = dict(atoms=seq,counts=dict(sorted(collections.Counter(seq).items())),alignment=align)
    return dict(schema='complete-anastasia-tree-v1',status='EXPLICIT_EXPLORATORY_SOURCE_HYPOTHESIS',
        source_path=SOURCE,source_sha256=hashlib.sha256((R/SOURCE).read_bytes()).hexdigest(),
        heading_line=122,heading_exact=raw[121],clauses=clauses,arities=dict(sorted(arities.items())),
        streams=streams,
        interpretation_limits=[
            'AFFLICTED is a provisional reading of ingratus in125; other lexical nuances have the same tree shape and are not distinguished by this test.',
            'PERSON denotes a generic role locally quantified in each source claim, not one individual executing all the actions.',
            'WATER_OF(BATH) denotes water of this bath, not one conserved physical portion.',
            'HOLE refers to the result of the DIG condition in C5; that binding is stipulated from the source syntax, not learned from the target.',
            'THEREFORE in C9 connects to the preceding water-condition discussion; no unstated numerical utility priority resolves C7/C8 overlap.',
            'RENEW shares a relational meaning across water-to-powers and person-to-water arguments; replacement versus refreshing remains unselected.',
            'BEGIN_RECORD is one structural header atom, not a translated source word; every target occurrence is first and it cannot cross a written word boundary.',
            'ASSERT and all other operators are proposed written semantic atoms, not an established historical parser.',
            'Nine tree assertions cover all twelve lines; neither the narrative attribution nor the digging clause may be omitted.',
        ])


if __name__ == '__main__':
    x=build()
    (E/'src/SOURCE.json').write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'clauses':len(x['clauses']),'source_lines':sum(len(c['source_lines']) for c in x['clauses']),
                      'atoms':len(x['streams']['PREFIX']['atoms']),'types':len(x['arities']),
                      'counts':x['streams']['PREFIX']['counts']},indent=2))
