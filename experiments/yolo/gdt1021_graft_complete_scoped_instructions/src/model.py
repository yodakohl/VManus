"""Typed instruction schema; no actual plant operation or success oracle."""
from itertools import product

class Invalid(ValueError):
    pass

def parse(tokens, mode):
    if mode not in ('GROUPED', 'NEAREST'):
        raise Invalid('unknown scope')
    i = 0
    clauses = []
    def take(pattern, name):
        nonlocal i
        if tokens[i:i + len(pattern)] != pattern:
            raise Invalid('construction:' + name)
        start = i
        i += len(pattern)
        clauses.append({'kind': name, 'start': start, 'end': i})
    take(['SELECT','STOCK_NOUN','AND','DONOR_NOUN'], 'selection')
    plants = {'A': 'stock', 'B': 'donor'}
    pair = ['A', 'B']
    take(['PREPARE','RECEIVING_PART','OF_FIRST','BY','CUT'], 'preparation')
    prep = {'owner': pair[0], 'part': 'receiving_part', 'means': 'CUT',
            'modality': 'instruction'}
    begin = i
    prefix = ['METHODS','STOCK_ROLE','DONOR_ROLE','SHOOT_SOURCE']
    if tokens[i:i + 4] != prefix:
        raise Invalid('method roles')
    i += 4
    methods = []
    while i < len(tokens) and tokens[i] in ('SPLIT', 'INNER_BARK'):
        methods.append({'name': tokens[i], 'receiver': 'A', 'donor': 'B',
                        'material': 'S', 'origin': 'B', 'material_kind': 'shoot',
                        'interface': {'SPLIT': 'split', 'INNER_BARK': 'inner_bark_wood'}[tokens[i]],
                        'seasons': None})
        i += 1
    if not methods or i >= len(tokens) or tokens[i] not in ('SPRING','SUMMER'):
        raise Invalid('shoot season')
    season = tokens[i]
    i += 1
    scoped = methods if mode == 'GROUPED' else methods[-1:]
    for m in scoped:
        m['seasons'] = [season]
    if tokens[i:i + 1] != ['BUD']:
        raise Invalid('budding method')
    i += 1
    if i >= len(tokens) or tokens[i] not in ('SPRING','SUMMER'):
        raise Invalid('bud season')
    methods.append({'name':'BUD','receiver':'A','donor':'B','material':'T',
                    'origin':'B','material_kind':'bark_piece_with_bud',
                    'interface':'budding_site','seasons':[tokens[i]]})
    i += 1
    if len({m['name'] for m in methods}) != len(methods):
        raise Invalid('duplicate method name')
    clauses.append({'kind':'method_account','start':begin,'end':i})
    take(['IF','REFUSES','GRAFT','NO','PRODUCT'], 'refusal_rule')
    if i != len(tokens):
        raise Invalid('unconsumed groups')
    return {'mode':mode,'clauses':clauses,'plants':plants,'ordered_pair':pair,
            'preparation':prep,'methods':methods,
            'rule':{'quantifier':'each_method_case_E','subject':'A',
                    'antecedent':'REFUSES(A,E)','consequent':'NOT PRODUCT_OF(E)'},
            'actual_grafts':[], 'actual_refusals':[], 'actual_products':[]}

def scenarios(graph):
    rows = []
    for season, method, refuses in product(('SPRING','SUMMER'),graph['methods'],(False,True)):
        rows.append({'season':season,'method':method['name'],'refuses':refuses,
                     'instruction_licensed':method['seasons'] is None or season in method['seasons'],
                     'receiver':method['receiver'],'donor':method['donor'],
                     'material':method['material'],'origin':method['origin'],
                     'graft_product_options':[False] if refuses else [False,True],
                     'stock_own_product_options':[False,True]})
    return rows

def valuations(graph):
    names = [m['name'] for m in graph['methods']]
    rows = []
    for bits in product((False,True),repeat=2*len(names)+1):
        refused = dict(zip(names,bits[:len(names)]))
        products = dict(zip(names,bits[len(names):-1]))
        if all(not refused[n] or not products[n] for n in names):
            rows.append({'refused':refused,'graft_products':products,'stock_own_product':bits[-1]})
    return rows
