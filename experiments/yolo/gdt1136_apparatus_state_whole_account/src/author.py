"""GDT1136 finite C0 author, fresh glossary; no inherited P4/P12 semantics.

Every IT source group has one finite lexical contribution. Manual phrase
bindings, event order and causal laws are hypotheses priced separately.
This is not a parser or evidence that the words have their proposed meanings.
"""
from pathlib import Path
import copy
import csv
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / 'artifacts'
SOURCE_FILES = ['artifacts/NATIVE_GROUPS.tsv', 'artifacts/WORD_PRIORS.json',
                'artifacts/WORD_PRIORS_RECEIPT.json', 'METHOD.md', 'PREREGISTRATION.md']

# raw | gloss | finite type | predicate/operation | proposed ordered components
# Exact surface cards are always retained. Components are authored, not learned.
LEXICAL_TEXT = '''
aiin|a quantity|quantity|QUANTITY|aiin
aiioly|the final remaining quantity|quantity|FINAL_REMAINDER|aii+ol+y
aithy|suitably|adverb|SUITABLE|aith+y
al|the same|identity|SAME_VESSEL|al
am|finish|boundary|END_STAGE|am
chchy|narrow passage|hardware|NARROW_PASSAGE|chchy
chear|the vessel rim|hardware|RIM|chear
checkhey|a measured increment|quantity|MEASURED_INCREMENT|checkh+ey
cheey|polished|vessel_property|POLISHED|che+ey
chekeey|closely fitted|vessel_property|CLOSELY_FITTED|che+k+eey
cheol|the apparatus vessel|vessel|VESSEL|che+ol
cheor|the discharge spout|hardware|DISCHARGE_SPOUT|che+or
cheos|its closure|hardware|CLOSURE|che+os
chety|secure|vessel_property|SECURE|che+t+y
chkchol|a strainer for stock|hardware|STOCK_STRAINER|chk+chol
chkey|a stopper|hardware|STOPPER|chk+ey
chls|a sealing joint|hardware|SEALING_JOINT|chls
cho|the inlet|hardware|INLET|cho
chodaiin|the next inlet stage|stage_nominal|INLET_STAGE|cho+daiin
chokchey|fit the inlet|operation|FIT_INLET|cho+k+chey
chokeey|the inlet is fitted|vessel_property|INLET_FITTED|cho+k+eey
choko|the inlet fitting|hardware|INLET_FITTING|cho+ko
chol|feedstock|material|FEEDSTOCK|chol
cholp|previous feedstock|material|PREVIOUS_FEEDSTOCK|chol+p
chopcheey|an attached inlet spout|hardware|ATTACHED_INLET_SPOUT|cho+p+cheey
chor|a stock portion|quantity|STOCK_PORTION|chor
chosaiin|the inlet in the following phase|stage_nominal|FOLLOWING_INLET_PHASE|cho+saiin
chs|the seal|hardware|SEAL|chs
chsm|close the vessel|operation|CLOSE_VESSEL|chs+m
chy|an opening|hardware|OPENING|ch+y
ckheey|measured|material_property|MEASURED|ckh+eey
cpheocthy|a supporting plate|hardware|SUPPORTING_PLATE|cpheocthy
cphoar|wash|operation|CLEAN|cphoar
csol|an outer support|hardware|OUTER_SUPPORT|csol
ctheea|open|vessel_property|OPEN|ctheea
ctheol|the empty vessel|vessel_property|BULK_EMPTY|cth+eol
cthey|the connecting passage|hardware|CONNECTING_PASSAGE|cth+ey
ctody|the passage is closed|vessel_property|PASSAGE_CLOSED|cto+dy
daiin|next|boundary|NEXT_PHASE|daiin
dairin|stage finished|boundary|STAGE_FINISHED|dairin
daisin|stage retained|boundary|STAGE_RETAINED|daisin
dal|a part|quantity|PART|dal
dar|the recovered fraction|recovered|RECOVERED_FRACTION|dar
dchey|without leakage|event_property|WITHOUT_LEAKAGE|d+chey
dol|the vessel base|hardware|BASE|d+ol
dor|the recovered output portion|recovered|RECOVERED_OUTPUT_PORTION|d+or
doteoda|drain completely|operation|DRAIN_COMPLETELY|doteoda
dy|completed|event_property|COMPLETED|dy
etolctheol|drain the vessel|operation|DRAIN|etol+ctheol
fcheolain|the washing quantity for the vessel|quantity|WASHING_QUANTITY|f+cheol+ain
kalshey|wet while holding steady|operation|HELD_WETTING|kal+shey
kchdol|a base fitting|hardware|BASE_FITTING|k+ch+dol
keeo|rest|operation|REST|keeo
kol|the vessel surface|surface|VESSEL_SURFACE|k+ol
kor|the output surface|output_part|OUTPUT_SURFACE|k+or
o|not|negator|NOT|o
oaiin|another quantity|quantity|ANOTHER_QUANTITY|o+aiin
odar|recover further|operation|RECOVER_FURTHER|o+dar
odariin|the washing recovery phase|stage_nominal|WASH_RECOVERY_PHASE|o+dar+iin
oeeor|the settled output|output_property|SETTLED|oee+or
oiin|a remainder quantity|quantity|REMAINDER_QUANTITY|oiin
okal|held firmly|event_property|HELD_FIRMLY|ok+al
okchol|stock in contact|material_property|IN_CONTACT|ok+chol
okeeeol|sustained vessel contact|operation|SUSTAINED_CONTACT|ok+eee+ol
okeeol|continued vessel contact|operation|CONTINUED_CONTACT|ok+ee+ol
okeeor|the continued output|output_property|CONTINUED|ok+ee+or
okeey|contact is maintained|event_property|CONTACT_MAINTAINED|ok+eey
okeol|contact the vessel|operation|CONTACT|ok+e+ol
okeoly|vessel contact completed|event_property|CONTACT_COMPLETED|ok+e+ol+y
okeor|the contacted output|output_property|CONTACTED|ok+e+or
okey|bring into contact|operation|BRING_CONTACT|ok+ey
okol|the inner vessel surface|surface|INNER_SURFACE|ok+ol
okolol|the full inner surface of the vessel|surface|FULL_INNER_SURFACE|ok+ol+ol
okor|the inner output portion|output_part|INNER_OUTPUT_PORTION|ok+or
ol|this vessel|vessel_reference|THIS_VESSEL|ol
olaiin|a quantity for this vessel|quantity|VESSEL_QUANTITY|ol+aiin
olcheeol|the washed vessel surface|vessel_property|WASHED_SURFACE|ol+chee+ol
olchey|the receiving opening of this vessel|hardware|RECEIVING_OPENING|ol+chey
olo|the exposed vessel surface|surface|EXPOSED_SURFACE|ol+o
or|this output|output_reference|THIS_OUTPUT|or
oraiin|an output quantity|quantity|OUTPUT_QUANTITY|or+aiin
ory|the output is complete|output_property|OUTPUT_COMPLETE|or+y
otaiin|a fresh quantity|quantity|FRESH_QUANTITY|ot+aiin
otechy|receive through the opening|operation|RECEIVE_OPENING|ot+e+chy
oteeod|receiving completed|event_property|RECEIVING_COMPLETED|ot+ee+od
oteey|receive steadily|operation|RECEIVE_STEADILY|ot+eey
oteol|introduce a fresh charge into the vessel|operation|FRESH_CHARGE|ot+e+ol
otol|the fresh charge for the vessel|material|FRESH_CHARGE_NOMINAL|ot+ol
pcheol|prepare the vessel|operation|PREPARE_VESSEL|p+cheol
qkeey|dry|vessel_property|DRY|qk+eey
qockheol|withdraw through a measured passage|operation|MEASURED_WITHDRAWAL|qockh+eol
qockhol|a connecting tube|hardware|CONNECTING_TUBE|qockh+ol
qodar|withdraw the recovered fraction|operation|WITHDRAW_RECOVERY|qo+dar
qokcheol|withdraw from the apparatus vessel|operation|PRODUCE_WITHDRAWAL|qok+cheol
qokchey|withdraw through the opening|operation|OPENING_WITHDRAWAL|qok+chey
qokchor|withdraw a stock portion|operation|STOCK_WITHDRAWAL|qok+chor
qokeol|decant the vessel contents|operation|DECANT|qok+eol
qoky|continue withdrawing|operation|CONTINUE_WITHDRAWAL|qok+y
qotoiir|the entire withdrawn bulk quantity|recovered|ENTIRE_WITHDRAWN_BULK|qot+oiir
qotol|withdraw all vessel bulk contents|operation|WITHDRAW_ALL_BULK|qot+ol
qpol|condition|operation|CONDITION|qp+ol
r|again|adverb|REPEAT|r
s|still|adverb|PERSISTING|s
sain|begin the next stage|boundary|BEGIN_NEXT_STAGE|sain
sar|a batch|material|BATCH|sar
scheol|the still retained vessel|vessel_reference|RETAINED_VESSEL|s+cheol
shea|the liquid body|material|LIQUID_BODY|shea
sheeckhey|a measured liquid increment|quantity|LIQUID_INCREMENT|she+e+ckh+ey
sheeol|clear vessel liquid|material_property|CLEAR|she+e+ol
sheeor|active liquid output|written_product_property|P_POSITIVE|she+e+or
sheey|stir thoroughly|operation|THOROUGH_STIR|she+ey
sheo|bulk liquid|material|BULK_LIQUID|she+o
sheockhey|a liquid measure|hardware|LIQUID_MEASURE|she+o+ckh+ey
sheody|wetting completed|event_property|WETTING_COMPLETED|she+o+dy
sheokeey|finish liquid contact|operation|PRODUCE_CONTACT|she+ok+eey
sheol|the liquid associated with the vessel|material|VESSEL_LIQUID|she+ol
sheom|liquid handling finished|boundary|LIQUID_STAGE_END|she+om
sheoor|inactive liquid output|written_product_property|P_NEGATIVE|she+o+or
sheor|liquid output|output_reference|LIQUID_OUTPUT|she+or
shey|wet|operation|WET|she+y
shkeeo|settle the liquid|operation|SETTLE_LIQUID|sh+k+eeo
sho|the liquid portion|material|LIQUID_PORTION|sh+o
shody|liquid preparation completed|event_property|LIQUID_PREP_COMPLETED|sh+o+dy
shok|the liquid contact layer|surface|LIQUID_CONTACT_LAYER|sh+ok
shol|liquid at the vessel|material|LIQUID_AT_VESSEL|sh+ol
shor|the liquid fraction|recovered|LIQUID_FRACTION|sh+or
shotey|rinse|operation|RINSE|sh+ot+ey
shy|liquid ready|material_property|LIQUID_READY|sh+y
soiin|another output quantity|quantity|ANOTHER_OUTPUT|s+oiin
ssheo|the still retained bulk liquid|material|RETAINED_BULK|s+s+heo
tchey|the outlet passage|hardware|OUTLET_PASSAGE|t+chey
teeol|hold the vessel steadily|operation|STEADY_HOLD|t+ee+ol
teol|hold the vessel|operation|HOLD|t+e+ol
ycheeo|subsequently rinse the surface|operation|SUBSEQUENT_SURFACE_RINSE|y+cheeo
ydar|the subsequent recovered fraction|recovered|SUBSEQUENT_RECOVERY|y+dar
yfolaiin|the subsequent washing quantity|quantity|SUBSEQUENT_WASH_QUANTITY|y+f+ol+aiin
ykchy|after settling|adverb|AFTER_SETTLING|y+k+ch+y
ykeor|the subsequently contacted output|output_property|SUBSEQUENT_CONTACTED_OUTPUT|y+k+e+or
ykhey|after measurement|adverb|AFTER_MEASUREMENT|y+k+h+ey
ypchey|prepare the opening subsequently|operation|SUBSEQUENT_OPENING_PREP|y+p+chey
ypcholy|the previous stock preparation is complete|material_property|PREVIOUS_STOCK_PREP_COMPLETE|y+p+chol+y
ypho?o|washing agent (uncertain surface)|wash_material|WASH_AGENT_UNCERTAIN|ypho?o
yteeoldy|the vessel holding stage completed|event_property|HOLD_STAGE_COMPLETED|y+t+ee+ol+dy
yteol|subsequently hold the vessel|operation|SUBSEQUENT_HOLD|y+t+e+ol
'''

LEXICON = {}
for line in LEXICAL_TEXT.strip().splitlines():
    raw, gloss, kind, semantic, parts = line.split('|')
    assert raw not in LEXICON
    parts = parts.split('+')
    assert ''.join(parts) == raw, (raw, parts)
    LEXICON[raw] = {'raw': raw, 'gloss': gloss, 'type': kind, 'semantic': semantic,
                    'components': parts, 'meaning_status': 'AUTHORED_C0_NOT_CONFIRMED',
                    'whole_form_residual_cost': 1,
                    'assembly_cost': int(len(parts) > 1)}

COMPONENTS = {
    'ol': 'vessel-oriented reference operand, restricted to the listed exact cards',
    'or': 'output-oriented operand, restricted to listed exact cards',
    'cheol': 'apparatus vessel nominal',
    'chol': 'feedstock nominal',
    'daiin': 'phase advancement operator',
    'aiin': 'quantity nominal',
    'dar': 'recovered material relation',
    'she': 'liquid-domain operand',
    'sh': 'liquid-domain allomorph hypothesis; not automatic deletion of E',
    'qok': 'withdrawal-domain operator',
    'qot': 'total bulk withdrawal domain',
    'ok': 'contact domain',
    'ot': 'fresh receiving domain',
    'p': 'preparation domain',
    'y_initial': 'subsequent-entry operation, only the listed initial-Y cards',
    'y_final': 'completed/action closure, only the listed final-Y cards; a separately paid scoped value',
    'dy': 'completed-stage closure',
    'e_OR': 'P-positive product qualifier in SHE/E/OR only',
    'o_OR': 'P-negative product qualifier in SHE/O/OR only',
    'che': 'apparatus domain in CHE/OL; other CHE cards keep their charged residual',
    'qp': 'conditioning event root in QP/OL',
    'e_event': 'event realization between OT fresh receiver and OL vessel operand',
    'o_ANOTHER': 'another-quantity operator in O/AIIN only; distinct from standalone negation and O_OR',
}

# Inspectable finite core; other surface splits retain paid whole residuals.
CORE_AST = {
    'cheol': {'constructor':'DOMAIN_NOUN','domain':'APPARATUS','reference':'VESSEL','parts':['che','ol']},
    'pcheol': {'constructor':'ACTION_ON_NOUN','root':'PREPARE_VESSEL','noun':'cheol','parts':['p','cheol']},
    'qpol': {'constructor':'EVENT_ON_REFERENCE','root':'CONDITION','reference':'VESSEL','parts':['qp','ol']},
    'qotol': {'constructor':'EVENT_ON_REFERENCE','root':'WITHDRAW_ALL_BULK','reference':'VESSEL','parts':['qot','ol']},
    'oteol': {'constructor':'EVENT_ON_REFERENCE','root':'FRESH_CHARGE','reference':'VESSEL','parts':['ot','e','ol']},
    'qokcheol': {'constructor':'ACTION_ON_NOUN','root':'PRODUCE_WITHDRAWAL','noun':'cheol','parts':['qok','cheol']},
    'sheor': {'constructor':'DOMAIN_REFERENCE','domain':'LIQUID','reference':'OUTPUT','property':None,'parts':['she','or']},
    'sheeor': {'constructor':'QUALIFIED_DOMAIN_REFERENCE','domain':'LIQUID','reference':'OUTPUT','property':{'predicate':'P','polarity':True},'parts':['she','e','or']},
    'sheoor': {'constructor':'QUALIFIED_DOMAIN_REFERENCE','domain':'LIQUID','reference':'OUTPUT','property':{'predicate':'P','polarity':False},'parts':['she','o','or']},
    'oaiin': {'constructor':'QUALIFIED_QUANTITY','noun':'QUANTITY','qualifier':'ANOTHER','parts':['o','aiin']},
}
HOMONYMS = [
    {'surface':'e','scopes':['e_event between OT/OL','e_OR between SHE/OR'],'cost':1},
    {'surface':'o','scopes':['standalone NOT','o_OR between SHE/OR','o_ANOTHER before AIIN'],'cost':2},
    {'surface':'y','scopes':['initial subsequent','final closure'],'cost':1},
]

RULES = [
    ('R01', 'Three native IT paragraph units are one case/procedure. Entry titles do not reset the apparatus; this is a paid procedural-unity premise.'),
    ('R02', 'PCHEOL at .1G1 prepares one new V and returns its actual apparatus-state packet. CHEOL/OL/SCHEOL later resolve that written case by consuming the same packet vessel field, not by spelling a new V.'),
    ('R03', 'AL in .8G15 predicates identity of the immediately preceding OL nominal with the pre-cleaning vessel from the returned history. This is written SAME, in addition to the broader reference rule.'),
    ('R04', 'The finite phrase map below supplies participant and event attachments. No automatic line/clause parser or universal word-order rule is inferred.'),
    ('R05', 'The nominal stock is A during conditioning/withdrawal and B during the fresh-charge runs. A word meaning FEEDSTOCK stays fixed while its supplied discourse participant changes. Previous-feedstock expressions refer to A.'),
    ('R06', 'Conditioning QPOL accepts V and conditioning material A introduced by the stock domain; its state change is a separate explicit law, not encoded as a whole sentence.'),
    ('R07', 'QOTOL means all BULK contents withdrawn, not complete microscopic decontamination. The returned apparatus state survives that operation. CPHOAR is a separate CLEAN action after product1, before run2.'),
    ('R08', 'OTEOL at .5G18 and .8G2 introduces fresh quantities B1/B2 through the same constructor. OTOL/OTAIIN preparatory nominal mentions may refer forward to those actual written introduction events. Such forward mentions assert nominal conditions, not earlier actual vessel loading.'),
    ('R09', 'Both fresh quantities are portions of one B stock, with equal relevant input type, amount=1, P_initial=0, clarity=1 and concentration=1. Equality of these parameters is a paid shared factory/default, not frequency evidence. Apparatus state is deliberately not included among B initial conditions.'),
    ('R10', 'OAIIN .7G2 asserts B2 != B1. SOIIN .9G16 asserts O2 != O1. Fresh allocation law additionally prevents reuse of consumed material. Distinct variable names alone do not imply distinctness.'),
    ('R11', 'SHEOKEEY .6G8 finishes contact of B1 with V and returns O1. QOKCHEOL .9G3 withdraws processed B2 from V and returns O2. Generic local contact/withdrawal words supply subsidiary stages, not duplicate primary products.'),
    ('R12', 'SHEEOR .6G9 independently writes P(O1); SHEOOR .7G13 independently writes NOT P(O2). SHEOR everywhere is unqualified liquid-output reference. Neither assertion is generated by the law.'),
    ('R13', 'The forward product2 assertion at .7G13 is attached to the subsequent run and later resolved by the actual .9G3 product return; it is not a second assertion about O1. This manual proleptic scope is a significant fitted cost.'),
    ('R14', 'Output reference OR/SHEOR denotes O0 during conditioning/recovery, O1 in run1, O2 in run2. Output-part nominals do not themselves assert P or create new products.'),
    ('R15', 'Hardware nominals introduce/mention typed parts of V. Quantity nouns qualify the current material/run or the explicitly indicated washing/recovery quantity. Each such attachment is recorded; no numerical count is inferred from repeated I letters.'),
    ('R16', 'A fixed lexical property contributes a predicate at its assigned phase; operation properties modify the actual operation or its pending prepared event. No property changes sense by occurrence.'),
    ('R17', 'Standalone O at .1G13 negates the following DRY surface property. O_OR is a separately charged product qualifier, not universal O negation or O=one.'),
    ('R18', 'STILL/AGAIN/NEXT boundaries add persistence/repetition/order predicates. No hidden cleaning, fresh input, or product property is inserted by them.'),
    ('R19', 'The prescribed primary event order is preparation < conditioning < complete bulk withdrawal < freshB1 < contact/product1 < cleaning < freshB2 < withdrawal/product2 < finish. Source phrase order and explicitly priced forward scopes are supplied, not discovered syntax.'),
    ('R20', 'CTHEOL bulk-empty references the completed A withdrawal before freshB1 loading; later subsidiary draining concerns preparations/recovery and does not erase the apparatus state.'),
    ('R21', 'Several rare exact forms are lexical residuals rather than universal morpheme rules. Each exact card has one meaning charge and every compound card one ordered assembly charge. No free unrestricted component concatenation is claimed.'),
    ('R22', 'YPHO?O receives a conditional whole-surface washing-agent hypothesis. Its unknown glyph is not repaired, translated independently, or matched to a determinate alternate spelling; semantic assignment is conditional on the entire uncertain transcription token.'),
    ('R23', 'IT .10 is only ten groups. The longer ZL/RF .10 bodies remain alternate-reader incompleteness. No missing IT groups or nominal/vessel bijection is invented.'),
    ('R24', 'Subsidiary rinsing is not CPHOAR washing: the fixed model explicitly assumes wetting/rinsing/holding/partial recovery leave the tracked apparatus state unchanged. Each subsidiary operation receives a paid law below. A film can also survive brief rinsing and be removed by separately written washing; that selectivity is a fitted law, not evidence of chemistry.'),
    ('R25', 'A washing-agent port is introduced by the CLEAN frame and forward qualified by uncertain YPHO?O .7G10. Preparatory rinsing may use an auxiliary rinse-fluid port R_pre; it is not the conserved B1/B2 main charge. These material arguments are paid frame defaults, not separately discovered ingredient words.'),
    ('R26', 'The process chain is a qualitative projection of primary commitments; bulk_amount=1 marks occupied bulk, not exact mass balance during subsidiary partial decants. The B factory amount is one common nominal unit. Full detailed conservation/satisfiability of every auxiliary operation is not independently established.'),
]

# Explicit phrase boundaries and bindings, not inferred sentences. Each IT
# position appears exactly once. Material/output fields are forward ports where
# appropriate and are resolved by the actual producer packets below.
PHRASES = [
 (1,1,3,'apparatus preparation','V','V','E_prepare'),
 (1,4,10,'condition with the initial stock','A','O0','E_condition'),
 (1,11,22,'apparatus surface and fittings for conditioning','A','O0','E_condition'),
 (2,1,7,'arrange and hold the conditioning vessel','A','O0','E_holdA'),
 (2,8,18,'contact and decant the conditioning material','A','O0','E_decantA'),
 (2,19,23,'repeat wetting and holding the conditioning stock','A','O0','E_wetA'),
 (3,1,17,'drain and withdraw all bulk conditioning material','A','O0','E_bulk_withdraw'),
 (3,18,24,'prepare the fresh liquid and recovery outlet','B1','O1','E_prepareB1'),
 (4,1,9,'rinse, settle and arrange the unfilled receiving vessel','B1','O1','E_prepareB1'),
 (4,10,21,'complete the measured receiving preparation','B1','O1','E_prepareB1'),
 (5,1,17,'set the vessel and quantity for the fresh first run','B1','O1','E_prepareB1'),
 (5,18,25,'introduce the fresh first charge and receive it','B1','O1','E_fresh1'),
 (6,1,8,'hold and finish contact of the first charge','B1','O1','E_product1'),
 (6,9,16,'describe the active first output and complete its batch','B1','O1','E_product1'),
 (7,1,12,'wash the same vessel and prepare a distinct fresh quantity','B2','O2','E_clean'),
 (7,13,20,'state the subsequent inactive output and finish preparation','B2','O2','E_prepareB2'),
 (8,1,6,'introduce the second fresh charge and fit the inlet','B2','O2','E_fresh2'),
 (8,7,16,'continue handling in the same still retained vessel','B2','O2','E_handle2'),
 (8,17,25,'complete the second output path and liquid handling','B2','O2','E_handle2'),
 (9,1,10,'withdraw the second product and recover it','B2','O2','E_product2'),
 (9,11,23,'assert a distinct output and complete recovery','B2','O2','E_recover2'),
 (10,1,10,'secure the washed vessel and final remainder','B2','O2','E_finish'),
]

def atom(predicate, *args):
    return {'op': 'ATOM', 'predicate': predicate, 'arguments': list(args)}

def sid(line, pos):
    return f'IT2a|f101r.{line}|G{pos:03d}'

def initial_packet(vessel):
    return {'vessel': vessel, 'apparatus_state': 0, 'bulk': None,
            'bulk_amount': 0, 'history': [], 'product_returns': {}}

def step(state, operation, origin, *, conditioning=True, cleaning=True, model='apparatus'):
    """Single qualitative law, with explicit actual prior state as sole input."""
    s = copy.deepcopy(state)
    before = copy.deepcopy(state)
    product = None
    if operation == 'CONDITION':
        s['bulk'], s['bulk_amount'] = 'A', 1
        if conditioning:
            s['apparatus_state'] = 1
    elif operation == 'WITHDRAW_ALL_BULK':
        s['bulk'], s['bulk_amount'] = None, 0
        if model == 'memoryless_bulk':
            s['apparatus_state'] = 0
    elif operation == 'CLEAN':
        s['bulk'], s['bulk_amount'] = None, 0
        if cleaning:
            s['apparatus_state'] = 0
    elif operation in ['FRESH1', 'FRESH2']:
        n = 1 if operation == 'FRESH1' else 2
        b = {'identity': 'B' + str(n), 'source': 'Stock_B',
             'amount': 1, 'initial_P': 0, 'clarity': 1, 'concentration': 1,
             'fresh': True, 'origin': origin}
        s['bulk'], s['bulk_amount'] = b, b['amount']
    elif operation in ['PRODUCT1', 'PRODUCT2']:
        n = 1 if operation == 'PRODUCT1' else 2
        b = s['bulk']
        if not isinstance(b, dict) or b['identity'] != 'B' + str(n):
            raise ValueError('Product needs its actual prior fresh-charge return')
        product = {'identity': 'O' + str(n), 'source_quantity': b['identity'],
                   'source_initial_conditions': copy.deepcopy(b),
                   'P_generated_by_law': bool(s['apparatus_state']),
                   'vessel': s['vessel'], 'producer': origin}
        s['product_returns'][product['identity']] = copy.deepcopy(product)
        s['bulk'], s['bulk_amount'] = None, 0
        if model == 'memoryless_bulk':
            s['apparatus_state'] = 0
    else:
        raise ValueError(operation)
    s['history'].append({'operation': operation, 'origin': origin,
                         'actual_prior_state': before, 'actual_product_return': product})
    return s, product

def actual_chain(*, conditioning=True, cleaning=True, model='apparatus'):
    vessel_return = {'identity': 'V', 'producer': sid(1,1), 'type': 'ApparatusVessel'}
    state = initial_packet(vessel_return)
    trace = []
    fresh_returns = {}
    product_returns = {}
    for op, line, pos in [('CONDITION',1,9), ('WITHDRAW_ALL_BULK',3,5),
                          ('FRESH1',5,18), ('PRODUCT1',6,8), ('CLEAN',7,1),
                          ('FRESH2',8,2), ('PRODUCT2',9,3)]:
        prior = state
        state, product = step(prior, op, sid(line,pos), conditioning=conditioning,
                              cleaning=cleaning, model=model)
        trace.append({'operation': op, 'source_group_id': sid(line,pos),
                      'actual_input': copy.deepcopy(prior), 'actual_return': copy.deepcopy(state),
                      'same_vessel_value_consumed': state['vessel'] == vessel_return})
        if op.startswith('FRESH'):
            fresh_returns[state['bulk']['identity']] = copy.deepcopy(state['bulk'])
        if product:
            product_returns[product['identity']] = product
    return {'model': model, 'vessel_return': vessel_return, 'trace': trace,
            'final_state': state, 'fresh_returns': fresh_returns,
            'product_returns': product_returns}

def phrase_for(line, pos):
    spans = [p for p in PHRASES if p[0] == line and p[1] <= pos <= p[2]]
    if len(spans) != 1:
        raise ValueError(('Bad finite phrase coverage',line,pos,spans))
    return spans[0]

def reduction(src, chain):
    raw = src['ivtff_group_raw']
    card = LEXICON[raw]
    line = int(src['locus'].split('.')[-1])
    pos = int(src['source_group_index'])
    phrase = phrase_for(line,pos)
    _, start, end, description, material, output, event = phrase
    sem, kind = card['semantic'], card['type']
    v = copy.deepcopy(chain['vessel_return'])
    event_phase = {'event': event, 'phrase': [line,start,end]}
    target = material
    if kind in ['vessel', 'vessel_reference', 'vessel_property', 'hardware', 'surface', 'identity']:
        target = v
    elif kind in ['output_reference','output_part','output_property','written_product_property']:
        target = copy.deepcopy(chain['product_returns'].get(output, {'identity':'O0','source':'A','status':'conditioning-output nominal; no P assertion'}))
    elif kind in ['event_property','adverb','boundary','operation','negator']:
        target = event_phase
    elif kind == 'wash_material':
        target = 'Wash_R'
    elif sem == 'PREVIOUS_FEEDSTOCK':
        target = 'A'
    elif kind == 'recovered':
        target = 'Recovered_A' if line <= 3 else 'Recovered_' + material
    if sem == 'P_POSITIVE':
        facts = [atom('LIQUID_OUTPUT', target), atom('P', target['identity'])]
    elif sem == 'P_NEGATIVE':
        facts = [atom('LIQUID_OUTPUT', target), {'op':'NOT','argument':atom('P',target['identity'])}]
    elif sem == 'SAME_VESSEL':
        facts = [atom('SAME_PHYSICAL_VESSEL', v, chain['trace'][3]['actual_return']['vessel'])]
    elif sem == 'ANOTHER_QUANTITY':
        facts = [atom('QUANTITY', 'B2'), atom('DISTINCT_MATERIAL_QUANTITIES','B2','B1')]
    elif sem == 'ANOTHER_OUTPUT':
        facts = [atom('OUTPUT_QUANTITY','O2'),atom('DISTINCT_MATERIAL_QUANTITIES','O2','O1')]
    elif sem == 'DRY' and line == 1 and pos == 14:
        facts = [{'op':'NOT','argument':atom('DRY', v)}]
    elif sem == 'NOT':
        facts = [atom('NEGATION_SCOPE', src['source_group_id'], sid(1,14))]
    elif kind == 'hardware':
        component = {'identity': 'Hardware_' + raw, 'type': sem}
        facts = [atom(sem,component),atom('APPARATUS_PART',component,v)]
    elif kind in ['vessel', 'vessel_reference']:
        facts = [atom('MENTION_VESSEL', v, sem)]
    elif kind == 'operation':
        agent = ('R_pre' if line < 7 else 'Wash_R') if sem in ['RINSE','SUBSEQUENT_SURFACE_RINSE'] else ('Wash_R' if sem=='CLEAN' else material)
        facts = [atom(sem,event_phase,agent,v)]
        if sem == 'FRESH_CHARGE':
            b = chain['fresh_returns'][material]
            facts += [atom('FRESH',copy.deepcopy(b)), atom('CHARGE_INTO',copy.deepcopy(b),v),
                      atom('RELEVANT_INITIAL_CONDITIONS',b['identity'],{k:b[k] for k in ['source','amount','initial_P','clarity','concentration']})]
        elif sem == 'WITHDRAW_ALL_BULK':
            facts += [atom('BULK_EMPTY_AFTER',v,event_phase)]
        elif sem == 'CLEAN':
            facts += [atom('CLEAN_PATIENT',v),atom('CLEAN_AGENT','Wash_R')]
        elif sem == 'CONDITION':
            facts += [atom('CONDITION_PATIENT',v),atom('CONDITION_AGENT','A')]
    else:
        facts = [atom(sem,target,event_phase)]
    return {'source': dict(src), 'lexical_card': copy.deepcopy(card),
            'compositional_reduction_if_core':copy.deepcopy(CORE_AST.get(raw)),
            'composition_status':'FINITE_TYPED_CORE' if raw in CORE_AST else 'EXACT_WHOLE_RESIDUAL_WITH_PROPOSED_SURFACE_PARTS',
            'manual_phrase': {'span':[line,start,end], 'description':description},
            'typed_bindings': {'target':target,'material_port':material,'output_port':output,'event_port':event_phase,'vessel_actual_return':v},
            'returned_constraints':facts,
            'assignment_status':'ASSIGNED_CONDITIONAL_UNCERTAIN_SURFACE_C0' if '?' in raw else 'ASSIGNED_C0',
            'source_raw_preserved':raw,
            'forward_dependency': 'product2 actual return at .9G3' if line == 7 and pos >= 13 else None}

def written_product_assertions(rows):
    """Extract only actual compiled textual P atoms, never generated state."""
    written, origins = {}, {}
    for row in rows:
        for f in row['returned_constraints']:
            positive = f['op']=='ATOM' and f['predicate']=='P'
            negative = f['op']=='NOT' and f['argument']['predicate']=='P'
            if positive or negative:
                p = f if positive else f['argument']
                owner = p['arguments'][0]
                if owner in written:
                    raise ValueError('Duplicate/contradictory textual product property')
                written[owner] = positive
                origins[owner] = row['source']['source_group_id']
    assert written=={'O1':True,'O2':False}
    assert origins=={'O1':sid(6,9),'O2':sid(7,13)}
    return written, origins

def compare(chain, written):
    generated = {o:r['P_generated_by_law'] for o,r in chain['product_returns'].items()}
    return {'written_property_assertions':written,'law_generated_values':generated,
            'matches_both_written_assertions':generated == written,
            'interpretation':'A conditional model/reading consistency check, not manuscript evidence.'}

def run():
    packet = list(csv.DictReader((ART/'NATIVE_GROUPS.tsv').open(),delimiter='\t'))
    native_it = [s for s in packet if s['edition']=='IT2a']
    priors = json.loads((ART/'WORD_PRIORS.json').read_text())
    prior_map = {p['form']:p for p in priors['profiles']}
    types = set(s['ivtff_group_raw'] for s in native_it)
    assert len(native_it)==209 and len(types)==144
    assert set(LEXICON)==types, {'missing':sorted(types-set(LEXICON)), 'extra':sorted(set(LEXICON)-types)}
    intended_positions = [(p[0],i) for p in PHRASES for i in range(p[1],p[2]+1)]
    actual_positions = [(int(s['locus'].split('.')[-1]),int(s['source_group_index'])) for s in native_it]
    assert intended_positions==actual_positions, 'Phrase map must have neither gaps nor invented positions'
    for raw, ast in CORE_AST.items():
        assert ast['parts']==LEXICON[raw]['components']
        if ast.get('root'):
            assert ast['root']==LEXICON[raw]['semantic']
    assert CORE_AST['sheeor']['property']['polarity'] is True
    assert CORE_AST['sheoor']['property']['polarity'] is False
    chain = actual_chain()
    rows = [reduction(s,chain) for s in native_it]
    assert [r['source'] for r in rows]==native_it
    assert all(r['returned_constraints'] and all(f['op'] in ['ATOM','NOT'] for f in r['returned_constraints']) for r in rows)
    full_formula = {'op':'EXISTS','binders':['V','A','Stock_B','B1','B2','O0','O1','O2','Wash_R','R_pre',
                    'Recovered_A','Recovered_B1','Recovered_B2']+
                    sorted(set(p[6] for p in PHRASES))+
                    ['Hardware_'+raw for raw,c in LEXICON.items() if c['type']=='hardware'],
                    'body':{'op':'AND','arguments':[copy.deepcopy(f) for r in rows for f in r['returned_constraints']]},
                    'interpretation':'All209 attached contributions collected into one finite authored formula. Terminal descriptive predicates are assertions, not automatically consumed causal operations. Only the required tracked contrast is executable/model-checked; whole detailed truth is not proven.'}
    sort_environment = {'V':'ApparatusVessel','A':'StockMaterialQuantity','Stock_B':'MaterialStock',
                        'B1':'FreshMaterialQuantity','B2':'FreshMaterialQuantity',
                        'O0':'ConditioningOutputQuantity','O1':'ProductOutputQuantity','O2':'ProductOutputQuantity',
                        'Wash_R':'WashingMaterialQuantity','R_pre':'AuxiliaryRinseMaterialQuantity',
                        'Recovered_A':'RecoveredMaterialQuantity','Recovered_B1':'RecoveredMaterialQuantity','Recovered_B2':'RecoveredMaterialQuantity'}
    sort_environment.update({p[6]:'EventOrCompositeHandlingPhase' for p in PHRASES})
    sort_environment.update({'Hardware_'+raw:'ApparatusPart' for raw,c in LEXICON.items() if c['type']=='hardware'})
    written, written_origins = written_product_assertions(rows)
    baseline = compare(chain,written)
    no_condition = actual_chain(conditioning=False)
    no_cleaning = actual_chain(cleaning=False)
    bulk = actual_chain(model='memoryless_bulk')
    film = actual_chain(model='adherent_A_film')
    assert baseline['matches_both_written_assertions']
    assert not compare(no_condition,written)['matches_both_written_assertions']
    assert not compare(no_cleaning,written)['matches_both_written_assertions']
    assert not compare(bulk,written)['matches_both_written_assertions']
    assert compare(film,written)['matches_both_written_assertions']
    primary_semantics = {'CONDITION':'CONDITION','WITHDRAW_ALL_BULK':'WITHDRAW_ALL_BULK',
                         'FRESH1':'FRESH_CHARGE','PRODUCT1':'PRODUCE_CONTACT','CLEAN':'CLEAN',
                         'FRESH2':'FRESH_CHARGE','PRODUCT2':'PRODUCE_WITHDRAWAL'}
    for t in chain['trace']:
        native = next(s for s in native_it if s['source_group_id']==t['source_group_id'])
        assert LEXICON[native['ivtff_group_raw']]['semantic']==primary_semantics[t['operation']]
    fresh = chain['fresh_returns']
    keys = ['source','amount','initial_P','clarity','concentration']
    assert {k:fresh['B1'][k] for k in keys} == {k:fresh['B2'][k] for k in keys}
    assert fresh['B1']['identity'] != fresh['B2']['identity']
    assert any(any(f.get('predicate')=='DISTINCT_MATERIAL_QUANTITIES' and f['arguments']==['B2','B1'] for f in r['returned_constraints']) for r in rows)
    assert any(any(f.get('predicate')=='DISTINCT_MATERIAL_QUANTITIES' and f['arguments']==['O2','O1'] for f in r['returned_constraints']) for r in rows)
    # Alternate readers remain exact lexical traces, never imputed full accounts.
    native_alternatives = []
    for s in packet:
        raw = s['ivtff_group_raw']
        native_alternatives.append({'source':dict(s), 'raw_unchanged':raw,
            'lexical_card_if_exact':copy.deepcopy(LEXICON.get(raw)),
            'status':'PRIMARY_COMPLETE_CONDITIONAL_ACCOUNT' if s['edition']=='IT2a' else
                ('EXACT_SHARED_LEXICAL_TRACE_ONLY_NOT_FULL_ACCOUNT' if raw in LEXICON else 'UNASSIGNED_ALTERNATE_RAW'),
            'reason':None if raw in LEXICON else 'No exact frozen lexical card. No normalization, concatenation, entity resolution, or IT substitution.'})
    assert len(native_alternatives)==665
    profile_summary = {raw:{'local_IT_count':sum(s['ivtff_group_raw']==raw for s in native_it),
                            'baseline_cache179_numeric':{e:{k:v[k] for k in ['count','rank','pages_with_form','positions','repetition']} for e,v in prior_map[raw]['editions'].items()}}
                       for raw in sorted(types)}
    main_operations = {'PREPARE_VESSEL','CONDITION','WITHDRAW_ALL_BULK','FRESH_CHARGE','PRODUCE_CONTACT','PRODUCE_WITHDRAWAL','CLEAN'}
    subsidiary_laws = [{'operation':op,'law':'Preserve tracked apparatus_state m; subsidiary bulk/material bookkeeping is outside this qualitative primary-state projection. No P/NOTP assertion is generated.','cost':1}
                      for op in sorted(set(c['semantic'] for c in LEXICON.values() if c['type']=='operation')-main_operations)]
    costs = {
        'exact_lexical_semantic_residual_cards':len(LEXICON),
        'listed_ordered_assembly_licenses':sum(c['assembly_cost'] for c in LEXICON.values()),
        'component_value_hypotheses':len(COMPONENTS),
        'manual_phrase_bindings':len(PHRASES),
        'reference_frame_defaults_and_identity_rules':len(RULES),
        'causal_laws':4,
        'scoped_polarity_qualifiers':2,
        'scoped_homonym_decisions':sum(h['cost'] for h in HOMONYMS),
        'finite_core_compositions':len(CORE_AST),
        'subsidiary_event_preservation_laws':len(subsidiary_laws),
        'new_confirmed_words':0,
        'clause_macros':0,
        'unpriced_homonyms':0,
        'scope': 'Exact cards and component hypotheses overlap; counts are costs/decisions, not evidence or a minimum description-length score. Every listed component not in COMPONENTS is a paid exact-card residual, not a free global morpheme.'}
    out = {
        'status':'FROZEN_COMPLETE_CONDITIONAL_IT209_C0_PENDING_FIXED_REVIEW',
        'confirmed_words':0,'phase':'exploratory authoring then fixed review',
        'source_receipts':{n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in SOURCE_FILES},
        'author_code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'scope':'Previously exposed f101r only; prior179 cache excludes target. No new image, reserve, unrelated target or external contact. No old glossary is imported/enforced as this candidate dictionary.',
        'prior_diagram_knowledge':'No image facts supplied in this task. This author previously read the frozen P4 input and authored the f83 CHEOL fragment in the preceding task. This is fresh dictionary authorship, not blind rediscovery or independent meaning agreement; overlaps such as CHEOL receptacle/vessel are prior-exposure-sensitive.',
        'lexicon':LEXICON,'component_hypotheses':COMPONENTS,'finite_core_AST':CORE_AST,'scoped_homonyms':HOMONYMS,
        'subsidiary_event_laws':subsidiary_laws,
        'priced_rules':[{'id':k,'rule':v,'cost':1} for k,v in RULES],
        'manual_phrase_map':[{'line':p[0],'start':p[1],'end':p[2],'reading':p[3],'material':p[4],'output':p[5],'event':p[6],'cost':1} for p in PHRASES],
        'costs':costs,'IT_per_group_reduction':rows,'all_native_alternatives':native_alternatives,
        'full_authored_formula':full_formula,
        'declared_sort_environment':sort_environment,
        'signature_policy':{
            'hardware_nominals':'TypePredicate(ApparatusPart), APPARATUS_PART(ApparatusPart,ApparatusVessel)',
            'vessel_properties_and_surface_relations':'Predicate(ApparatusVessel,EventOrCompositeHandlingPhase); a surface relation does not create an independently bound surface object',
            'material_quantity_and_stage_nominals':'Predicate(MaterialQuantity,EventOrCompositeHandlingPhase); phase nominals relate the material topic to the supplied handling phase',
            'event_properties_adverbs_boundaries':'Predicate(EventOrCompositeHandlingPhase,EventOrCompositeHandlingPhase); adverbs/phase conditions apply to the composite phrase event',
            'operations':'Operation(EventOrCompositeHandlingPhase,MaterialQuantity_or_ApparatusVessel,ApparatusVessel); second operand is the typed procedure material/patient. CLEAN uses Wash_R and RINSE its explicit auxiliary fluid',
            'output_attributes':'Predicate(OutputQuantity,EventOrCompositeHandlingPhase)',
            'product_contrast':'P(OutputQuantity) or NOT P(OutputQuantity); extracted from actual compiled source contributions',
            'identity':'SAME_PHYSICAL_VESSEL(ApparatusVessel,ApparatusVessel); DISTINCT_MATERIAL_QUANTITIES(MaterialQuantity,MaterialQuantity)',
            'scope':'These are declared C0 signatures. Full logical/physical satisfiability remains for review; lexical labels are not semantic evidence.'},
        'product_property_definition':'P is the authored binary active/inactive product quality. No specific independently bound assay, pharmacological efficacy or measured phenotype is supplied; the boolean contrast and the transfer law are hypotheses.',
        'coverage_distinction':{'glossary_assigned_positions':209,'typed_and_attached_contributions':209,
                                'all_collected_into_finite_conjunction':True,
                                'whole_formula_independently_proven_satisfiable':False,
                                'later_causal_consumption':'Only nominated primary operation/state ports; other descriptive attributes are terminal truth-condition assertions, not claimed future consumers.'},
        'actual_causal_return_chain':chain,
        'causal_laws': [
            'Conditioning A sets apparatus-associated state m=1; initial apparatus state m=0 is a paid premise.',
            'Complete bulk withdrawal changes bulk/amount to empty/0 while m persists in apparatus/film models; memoryless model resets m.',
            'Fresh B input has initialP=0 and other conserved factory conditions; completed contact/withdrawal produces P_output=m. This transfer law is separately hypothesized.',
            'Written cleaning resets m=0 and removes bulk. Adherent A film can obey precisely the same update/retention/reset laws.'
        ],
        'written_contrast': {'P_O1_source':written_origins['O1'],'NOT_P_O2_source':written_origins['O2'],
                             'P_O1':True,'P_O2':False,'not_law_generated':True,
                             'forward_O2_binding':'Written .7G13 property consumes actual .9G3 product return through R13; it does not select product identity by variable spelling alone.'},
        'written_required_operations':{'condition':sid(1,9),'bulk_all_withdrawal':sid(3,5),'freshB1':sid(5,18),'clean':sid(7,1),'freshB2':sid(8,2),
                                       'sameV':sid(8,15),'differentB':sid(7,2),'differentO':sid(9,16)},
        'conditional_consistency':baseline,
        'counterfactuals': {'without_conditioning':{'chain':no_condition,'comparison':compare(no_condition,written)},
                            'without_cleaning':{'chain':no_cleaning,'comparison':compare(no_cleaning,written)},
                            'same_consumer_code_and_no_duplicate_state_seed':True,
                            'interpretation':'Only an upstream operation parameter is changed; actual returned state then propagates. Written P/NOTP observations remain frozen and mismatch is reported.'},
        'fixed_rival_models':{'memoryless_bulk_reset':{'chain':bulk,'comparison':compare(bulk,written)},
                              'persistent_apparatus_state':baseline,
                              'adherent_A_film_equivalent_law':{'chain':film,'comparison':compare(film,written)},
                              'film_distinguished':False},
        'fresh_initial_condition_equality':{'keys':keys,'B1':fresh['B1'],'B2':fresh['B2'],'equal_except_identity_and_source_event':True,'assumed_factory_rule':'R09'},
        'profile_numbers_consulted_before_glossary_freeze':profile_summary,
        'frequency_use': [
            'DAIIN740/169pages, OL456/106, AIIN390/97, OR298/106: use broad phase/reference/quantity functions rather than scene-specific coordinates or sentence macros.',
            'CHOL345/127, SHEY238/77, DAR242/110, SHOL163/86, CHEEY150/61: fixed generic stock/wetting/recovery/liquid-at-vessel/surface-property hypotheses; exact counts never establish any gloss.',
            'SHEEOR4/4 and SHEOOR0 in baseline cache: contrast is an authored exact-card hypothesis, not a discovered polarity proof. Target-local occurrences are separately retained.',
            'SHEOR44/35 stays neutral output, not freely active/inactive by occurrence. OTEOL29/27 remains one fresh-input constructor at both target positions.',
            'Zero counts in the old179-selector cache do not mean absence/hapax; f101r is excluded. All144 selected forms have explicit local counts.',
            'GDT608: directed composition and exact residual identity both matter; component hypotheses are not confirmed morphology and OL/OR are not reduced to a single O meaning.'
        ],
        'known_counterexamples_retained':['S02 bulk-only original failures unchanged; new apparatus/film memory candidate is additional.', 'W35 recipient gap not repaired.', 'GDT940 fixed nominal extension failure unchanged.', 'GDT1116 universal negative-then-pure failure unchanged; no such universal process law here.', 'GDT812 has no local labels or vessel/paragraph bijection.'],
        'rivals_and_limits': [
            'Adherent A film and non-film apparatus state are observationally equivalent under this finite law. Complete bulk removal does not exclude film or microscopically retained A.',
            'Independent entries/new vessel and changed B inputs remain alternative interpretations of the raw text. R01/R02/R03/R09 exclude them only inside this authored candidate, not empirically.',
            'The exact glossary is highly fitted (144 cards, most locally once). Exact209 alignment is completeness of authorship, not semantic accuracy, independent confirmation or decipherment progress.',
            'The product2 forward scope and exact E_OR/O_OR polarity are substantial unsupported semantic/grammar hypotheses. No textual frequency supplies their truth.',
            'IT YPHO?O is conditionally assigned without glyph resolution. Alternate uncertain forms and extra .10 groups do not converge into IT.',
            'Subsidiary operations are finite typed local stage assertions; only the nominated primary events change the tracked qualitative state. This abstraction is a paid process-model assumption, not an established account of historical procedure.',
            'The ten finite core ASTs expose limited compositional sharing; the remaining134 exact word types retain whole residual meanings and proposed surface parts only. Their compound licenses do not themselves demonstrate semantic composition.',
            'No complete detailed mass-balanced witness or proof of all auxiliary event predicates is supplied. The executed consistency check covers the tracked contrast and identity/equality commitments; fixed review must audit the whole reading.',
            'No plant/source name, apparatus mechanism, surface chemistry, image owner, calibrated significance or near-complete reserve eligibility.'
        ],
        'freeze_policy':'No post-review edits. Root owns fixed review, registry and publication.'
    }
    (ART/'AUTHOR_ACCOUNT.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    md = ['# GDT1136 frozen conditional whole IT account', '',
          'Fresh C0 glossary: **209/209 IT native groups receive finite conditional contributions; confirmed words0**. This is highly fitted authorship, not a semantic finding. Full665 native groups remain preserved; ZL/RF only receive exact lexical traces and unresolved alternatives, never an imputed full reading.', '',
          out['prior_diagram_knowledge'], '',
          'Each position contributes one or more typed, manually attached predicates collected in the final authored conjunction. Many surface/quantity/handling attributes are terminal descriptive assertions rather than later causal inputs. The executable check covers the required primary contrast; it is not a complete truth or mass-balance proof for every auxiliary predicate.', '',
          '## Conditional connected reading', '',
          'Prepare the apparatus vessel. Wet the initial stock and condition the vessel with it; arrange the surface, measures, stopper, inlet and supporting parts, keeping the surface wet rather than dry. Hold the vessel, maintain contact and decant the stock, then wet/hold again. Drain and withdraw the complete bulk conditioning charge; the bulk vessel is empty while its apparatus-associated state is retained under the explicit model.', '',
          'Prepare the fresh liquid, recover the withdrawn fraction and arrange/rinse the receiving parts. In the empty receiving vessel, settle and measure the fresh preparation, fitting and closing its passages. Introduce a fresh B quantity, receive and hold it, and finish its contact with the retained vessel. The separately written liquid-output description is **active, P(O1)**. Measure the output and finish that batch.', '',
          'Wash the vessel, prepare another distinct fresh quantity, and rinse with a washing agent whose IT word surface remains uncertain. The subsequent product is separately described prospectively as **inactive, NOT P(O2)**; this forward reference is paid and resolves to the later actual product return. Introduce the second fresh B charge, fit and hold the same still-retained apparatus, handle the liquid, and withdraw/recover the second output. State that this is another output quantity. Secure the washed surface and finish with the remaining quantity.', '',
          'The English paragraphs connect the finite phrase map; exact word contributions below are the authoritative detail. Neither narrator nor causal law adds an unmentioned cleaning or derives the two written P assertions.', '',
          '## Required written anchors and actual reuse', '',
          '| Commitment | Native IT source | Authored sense |', '|---|---|---|']
    for k,v in out['written_required_operations'].items():
        raw = next(s['ivtff_group_raw'] for s in native_it if s['source_group_id']==v)
        md.append('| '+k+' | '+v.replace('|','\\|')+' | '+raw+' = '+LEXICON[raw]['gloss']+' |')
    md += ['| P(O1) | '+sid(6,9).replace('|','\\|')+' | SHEEOR: active output |',
           '| NOT P(O2) | '+sid(7,13).replace('|','\\|')+' | SHEOOR: inactive output, forward resolved |', '',
           'PCHEOL returns the actual vessel/state packet. Each conditioning, bulk removal, fresh introduction, product operation and cleaning function reads the preceding return. OL/AL and both run producers read the vessel field of that packet. There is no independently preseeded second copy of the conditioning result. Removing conditioning changes product1; removing cleaning changes product2 while written product assertions stay fixed.', '',
           'B1/B2 share the explicitly paid factory conditions; OAIIN writes B2≠B1 and SOIIN writes O2≠O1. SAME is written by AL; continuity of the case also uses paid discourse rules. These are stronger author commitments, not facts recovered from spelling.', '',
           '## Costs, components and rule assumptions', '', '```json',json.dumps(costs,indent=2),'```', '']
    for k,v in RULES:
        md += ['- **'+k+' (cost1):** '+v]
    md += ['', 'Component sharing is limited to ten inspectable finite core ASTs. The remaining134 cards are whole lexical residuals with proposed surface parts, not demonstrated semantic composition. Every exact word card is separately charged; residual senses such as plate, tube, washing agent or polished are semantic atoms, not complete arbitrary clauses. No old P4/P12 values are inherited. E_OR/O_OR, standalone O, O_ANOTHER and positional Y values have explicit scoped homonym costs; neutral SHEOR never switches polarity.', '',
           '## Exact IT alignment', '',
           '| Source | Raw | Fixed gloss | Manual event/material/output | Constraints |', '|---|---|---|---|---|']
    for r in rows:
        b=r['typed_bindings']
        fields=[r['source']['source_group_id'],r['source_raw_preserved'],r['lexical_card']['gloss'],b['event_port']['event']+'/'+b['material_port']+'/'+b['output_port'],json.dumps(r['returned_constraints'],ensure_ascii=False,separators=(',',':'))]
        md.append('| '+' | '.join(f.replace('|','\\|') for f in fields)+' |')
    md += ['', '## Model comparison, priors and native limits', '',
           'The persistent apparatus candidate and an adherent A-film with the identical update/reset law both generate P(O1)=true and P(O2)=false. The frozen bulk-reset model generates false/false and conflicts with written P(O1). Conditioning-disabled gives false/false; cleaning-disabled gives true/true. These are conditional consistency results, not empirical rejection of the alternative readings.', '',
           'P/NOTP at the two source positions are lexical constraints, independent of the generated values. A-film is retained: bulk-empty says nothing about zero adherent material. Independent-entry/new-vessel and changed-input alternatives remain manuscript rivals; the present candidate rules assume them away locally.', '']
    md.extend('- '+x for x in out['frequency_use'])
    md += ['']
    md.extend('- '+x for x in out['rivals_and_limits'])
    md += ['', '## Exact alternative-reader table', '',
           'All raw entities, uncertain/small spaces and native paragraph flags are retained in JSON. Exact matches here are lexical traces only; no matching-position normalization or missing IT .10 text is invented.', '',
           '| Source | Raw | Status |', '|---|---|---|']
    for a in native_alternatives:
        if a['source']['edition'] != 'IT2a':
            md.append('| '+a['source']['source_group_id'].replace('|','\\|')+' | '+a['raw_unchanged'].replace('|','\\|')+' | '+a['status']+' |')
    md += ['', 'No post-review repair. Exact outputs and generator are frozen with hashes in AUTHOR_RECEIPT.json; root owns publication.', '']
    (ART/'AUTHOR_READING.md').write_text('\n'.join(md))
    receipt = {'status':out['status'],'deterministic':True,'no_new_access':True,
               'prior_exposure_disclosure':out['prior_diagram_knowledge'],
               'read_scope':SOURCE_FILES+['VOYNICH_CURRENT_ROUTE.md','GDT608 REPORT.md','composition topic excerpts'],
               'source_hashes':out['source_receipts'],'author_code_sha256':out['author_code_sha256'],
               'outputs':{n:hashlib.sha256((ART/n).read_bytes()).hexdigest() for n in ['AUTHOR_ACCOUNT.json','AUTHOR_READING.md']},
               'checks':{'exact_IT209':True,'exact_all_native665':True,'exact_types144':True,'all_manual_spans_exactly_once':True,
                         'all209_typed_attached_and_collected':True,'whole_auxiliary_truth_proof':False,
                         'actual_state_chain':True,'independent_written_P_contrast':True,'conditioning_and_cleaning_counterfactuals':True,'film_rival_retained':True},
               'meaning_confirmed':False}
    (ART/'AUTHOR_RECEIPT.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':out['status'],'costs':costs,'comparison':baseline,'hashes':{
        'src/author.py':out['author_code_sha256'],
        **{'artifacts/'+n:hashlib.sha256((ART/n).read_bytes()).hexdigest() for n in ['AUTHOR_ACCOUNT.json','AUTHOR_READING.md','AUTHOR_RECEIPT.json']} }},indent=2))

if __name__ == '__main__':
    run()
