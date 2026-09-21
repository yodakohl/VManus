"""Reverse clause recognizer and relation-based consequence implementation.

Does not import the forward parser, graph constructor or valuation evaluator.
"""
import itertools

def interpret(tokens, mode):
    assert mode in ('GROUPED','NEAREST')
    assert tokens[-5:] == ['IF','REFUSES','GRAFT','NO','PRODUCT']
    end = len(tokens)-5
    assert tokens[end-2] == 'BUD' and tokens[end-1] in ('SPRING','SUMMER')
    bud_season = tokens[end-1]
    season_pos = end-3
    assert tokens[season_pos] in ('SPRING','SUMMER')
    start = season_pos-1
    while start >= 0 and tokens[start] in ('SPLIT','INNER_BARK'):
        start -= 1
    method_tokens = tokens[start+1:season_pos]
    assert method_tokens and len(set(method_tokens)) == len(method_tokens)
    assert tokens[start-3:start+1] == ['METHODS','STOCK_ROLE','DONOR_ROLE','SHOOT_SOURCE']
    method_start = start-3
    assert tokens[method_start-5:method_start] == ['PREPARE','RECEIVING_PART','OF_FIRST','BY','CUT']
    assert tokens[:method_start-5] == ['SELECT','STOCK_NOUN','AND','DONOR_NOUN']
    limits = [0,method_start-5,method_start,end,len(tokens)]
    clauses = [dict(kind=k,start=a,end=b) for k,a,b in zip(
        ['selection','preparation','method_account','refusal_rule'],limits,limits[1:])]
    relation = []
    for j,n in enumerate(method_tokens):
        seasons = [tokens[season_pos]] if mode=='GROUPED' or j==len(method_tokens)-1 else None
        relation.append(dict(name=n,receiver='A',donor='B',material='S',origin='B',material_kind='shoot',
                             interface='split' if n=='SPLIT' else 'inner_bark_wood',seasons=seasons))
    relation.append(dict(name='BUD',receiver='A',donor='B',material='T',origin='B',
                         material_kind='bark_piece_with_bud',interface='budding_site',seasons=[bud_season]))
    graph = dict(mode=mode,clauses=clauses,plants={'A':'stock','B':'donor'},ordered_pair=['A','B'],
                 preparation=dict(owner='A',part='receiving_part',means='CUT',modality='instruction'),
                 methods=relation,rule=dict(quantifier='each_method_case_E',subject='A',
                 antecedent='REFUSES(A,E)',consequent='NOT PRODUCT_OF(E)'),
                 actual_grafts=[],actual_refusals=[],actual_products=[])
    scenarios=[]
    seasons=('SPRING','SUMMER')
    for t in seasons:
        for m in relation:
            for r in (False,True):
                # Derive possible products from all four two-variable valuations.
                options=sorted({p for p in (False,True) if (int(r)+int(p)) < 2})
                scenarios.append(dict(season=t,method=m['name'],refuses=r,
                    instruction_licensed=m['seasons'] is None or t in m['seasons'],
                    receiver='A',donor='B',material=m['material'],origin='B',
                    graft_product_options=options,stock_own_product_options=[False,True]))
    valuations=[]
    names=method_tokens+['BUD']
    # Enumerate products first; a present product rules out only its own refusal.
    for output in itertools.product((False,True),repeat=len(names)):
        domains=[(False,) if present else (False,True) for present in output]
        for refusal in itertools.product(*domains):
            for own in (False,True):
                valuations.append(dict(refused=dict(zip(names,refusal)),
                    graft_products=dict(zip(names,output)),stock_own_product=own))
    return graph,scenarios,valuations
