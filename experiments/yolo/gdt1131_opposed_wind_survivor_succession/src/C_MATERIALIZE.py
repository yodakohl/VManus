#!/usr/bin/env python3
"""Owned C description-DAG accounting; no learning, translation validation or data query.

The dictionary supplies proposed meanings. This small materializer only records
their fixed role dependencies and preserves every SOURCE row. Source IDs are
audit node identifiers, never branches in the execution policy.
"""
import collections
import hashlib
import json
from pathlib import Path

D = Path(__file__).resolve().parents[1]

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def entry(raw, families, required, outputs, formula, operation="describe", extras=None):
    return dict(raw_form=raw, entry_id="C_" + raw, families=families,
                required_roles=required, outputs=outputs, formula=formula,
                operation=operation, whole_residual_cost=1,
                extension=raw not in {"sain", "or", "aiin", "daiin", "shodaiin"},
                additional_costs=extras or [])

# Roles are stable dictionary interfaces. Their values and actual producers vary
# with generic topic and transcript; no occurrence-specific entry is used.
E = []
def add(*a, **kw): E.append(entry(*a, **kw))
add("sain", ["OPEN"], [], {"scope":"GenericSchema"},
    "Open universal wind-kind opposition/property topic; bind ambient observer O and horizon F.", "open",
    ["topic payload", "ambient F/O binding", "generic wind typing premise"])
add("or", ["KIND"], ["scope"], {},
    "Append next universally quantified WindKind variable to ordered kind buffer; after two introductions focus describes their ordered pair.", "kind")
add("aiin", ["aN"], ["scope", "focus"], {},
    "aN retains the current nonempty DescriptionRecord and its dependency closure as a usable BoundDescriptionRef.", "an")
add("opchdy", ["REQUIRE"], ["scope", "latest_ref"], {"opposition":"SpatialOpposition"},
    "Describe diametrically opposed source directions of kind1/kind2 in F, from which they blow; source bearing is not destination.",
    extras=["spatial opposition payload", "F/O owner application", "reference dereference"])
add("qotor", ["CONTEXT", "REQUIRE"], ["scope", "opposition", "kind1", "kind2"],
    {"u":"PhysicalInstanceVar", "v":"PhysicalInstanceVar", "t0":"TimeVar", "encounter":"ConfrontationAntecedent"},
    "Universally bind distinct original u:kind1 and v:kind2; if both confront in F at t0, study the strength-conditioned outcomes. No storm is asserted.",
    extras=["two instance binders", "u!=v", "t0 binder", "same confrontation condition", "simultaneous blowing condition"])
add("sheedy", ["COMPARE"], ["scope", "encounter", "u", "v"], {"partition":"StrengthPartition"},
    "Partition confrontation by equal strength or strict inequality; inequality binds stronger to one of the original u/v and weaker to the other.",
    extras=["equal/unequal strength partition", "branch-local stronger/weaker reference binders"])
add("shodaiin", ["QUALIFIER", "d", "aN"], ["scope", "focus", "partition"], {},
    "So qualifies current strength-partition description; d collates its nonempty dependency closure; nested aN retains the qualified record.", "qualified_an",
    ["So comparison residual", "So·daN juxtaposition rule; no whole learned merge"])
add("olfar", ["CONSEQUENT"], ["scope", "latest_ref", "encounter", "u", "v", "t0"], {"unequal_rule":"ConditionalRule"},
    "If opposed original participants have unequal strength, the original stronger continues through confrontation while its action causes complete cessation of the weaker at t_after>t0. No lifetime beyond this confrontation follows.",
    extras=["inequality antecedent", "ordered t_after binder", "original stronger identity retention", "weak cessation", "stronger-causes-cessation relation", "reference dereference"])
add("ary", ["CONSEQUENT"], ["scope", "partition", "encounter", "u", "v"], {"equal_rule":"ConditionalRule"},
    "In the equal-strength branch both opposed original participants mutually obstruct; neither is singled out as a survivor.",
    extras=["equality branch", "mutual obstruction consequence"])
add("dair", ["DESCRIBE"], ["scope", "opposition", "kind1", "kind2"], {"quality_distinction":"QualityOppositionDefinition"},
    "Separately define qualitative opposition as reversal on both QH and QM, distinct from diametrical source opposition. Do not identify d·air with daN.",
    extras=["full d·air residual", "two quality-axis applications", "spatial/qualitative distinction"])
add("sheo", ["DESCRIBE"], ["scope", "quality_distinction", "kind1", "kind2"], {"mixture":"KindMixtureDescription"},
    "Qualities participate by mixture and degree; a positional comparison alone does not fix a uniform two-quality classification.",
    extras=["Se·o full residual", "degree/mixture qualification"])
add("oraiin", ["DESCRIBE", "aN"], ["scope", "quality_distinction", "mixture"], {},
    "The exact or residual selects the spatial-versus-qualitative distinction with mixture qualification; aN retains it. No universal meaning transfer from standalone or.", "residual_an",
    ["or·aN residual selector", "directed juxtaposition rule"])
add("chol", ["DESCRIBE"], ["scope", "latest_ref", "quality_distinction", "mixture"], {"classification":"KindClassification"},
    "Apply the retained distinction to classifications of these generic kinds; a shared or opposed quality is a kind property, not identity of physical winds.",
    extras=["classification residual", "reference dereference"])
add("daiin", ["d", "aN"], ["scope", "focus"], {},
    "d collates latest completed descriptive contribution and its dependency closure; aN publishes the resulting nonempty retained description.", "dan")
add("ockhdor", ["CONTEXT"], ["scope", "latest_ref"], {"local_frame":"ObserverContext"},
    "Relate the retained kind classification to arbitrary observer O and local horizon F; location from which a kind blows and visibility to O remain distinct.",
    extras=["complete o·K·d·or residual", "ambient O/F use", "reference dereference"])
add("olkor", ["DESCRIBE"], ["scope", "local_frame", "classification"], {"observability":"LocalVisibilityQualification"},
    "Not locally perceived by O does not imply globally absent; no local visibility predicate is promoted to universal nonexistence.",
    extras=["complete olk·or residual", "local/global distinction"])
add("shoral", ["DESCRIBE"], ["scope", "classification"], {"source_names":"SourceNamingRule"},
    "Kinds are named according to their source regions and may participate in neighboring classes; no cardinal labels or numeric four-kind plan is assigned.",
    extras=["S·or·al source-naming residual", "generic regional naming relation"])
add("sosees", ["QUANTIFY", "CLOSE"], ["scope", "unequal_rule", "equal_rule", "classification", "local_frame", "observability", "source_names"], {"terminal":"TerminalRule"},
    "Publish and close the connected kind account: source position, two opposition types, strength branches, local observation and source naming.", "close",
    ["full s·os·E·s terminal residual", "explicit whole-unit collection"])

add("pchedeey", ["OPEN"], [], {"scope":"GenericSchema"},
    "Open a new universal rule about adjacent wind-kind succession under solar motion; bind ambient O/F and material X, driver SUN.", "open",
    ["temporal-topic payload", "explicit N/E scope reset", "ambient O/F/X/SUN inputs", "generic wind typing premise"])
add("olkey", ["KIND", "DESCRIBE"], ["scope"], {},
    "Introduce first quantified wind kind and designate its source region as the antecedent region.", "kind",
    ["complete olk·ey antecedent-role residual"])
add("qokedy", ["KIND", "COMPARE"], ["scope", "kind1"], {},
    "Introduce a second quantified kind, distinct as a source-defined kind, as prospective adjacent successor kind.", "kind",
    ["complete qokedy successor-role residual", "kind-distinctness predicate"])
add("sheos", ["DESCRIBE"], ["scope", "kind1", "kind2"], {"adjacency":"SourceAdjacency"},
    "The source regions of kind1 and kind2 are neighboring around the same observer-relative horizon F; not a compass name or diametrical opposition.",
    extras=["full Se·os adjacency residual", "F/O application"])
add("fcheey", ["CONTEXT"], ["scope", "adjacency"], {"driver":"SolarMotionContext", "material":"DryExhalationContext"},
    "SUN motion elevates X in approached regions and ceases its elevation in withdrawn regions; establish the conditional material mechanism.",
    extras=["f·CEy solar/material residual", "SUN/X causal mechanism premise"])
add("otchedy", ["REQUIRE", "CONTEXT"], ["scope", "driver", "kind1"], {"withdrawal":"SolarWithdrawal", "t0":"TimeVar"},
    "Take conditional solar withdrawal from kind1's source at predecessor time t0.",
    extras=["ot·Cedy withdrawal residual", "t0 binder"])
add("chotey", ["REQUIRE"], ["scope", "withdrawal", "material", "kind1", "t0"], {"old_supply_ends":"MaterialCessation"},
    "At the withdrawn source, elevation of dry exhalation ceases as consequence of withdrawal.",
    extras=["C·ot·ey supply-cessation residual", "withdrawal causes unavailable supply"])
add("qocthey", ["REQUIRE", "CONTEXT"], ["scope", "old_supply_ends", "kind1", "t0"], {"u":"PhysicalInstanceVar", "old_end":"WindCessation"},
    "Bind an original wind instance u of kind1 which previously blew and ceases at t0 through lost raised material; this is an antecedent, not an observed storm.",
    extras=["qo·T·ey full cessation residual", "u binder", "previously-blowing predicate", "material loss causes cessation"])
add("oteey", ["REQUIRE", "CONTEXT", "COMPARE"], ["scope", "driver", "kind2", "old_end", "t0"], {"approach":"SolarApproach", "t1":"TimeVar", "order":"TemporalOrder"},
    "SUN approaches kind2's adjacent source at t1 strictly after the first wind's cessation at t0.",
    extras=["ot·Ey approach residual", "t1 binder", "strict t0<t1 relation"])
add("ol", ["CONTEXT"], ["scope", "latest_kind"], {"source_focus":"KindVar"},
    "Retrieve the most recently introduced kind as source-region focus; no cardinal or physical participant name.",
    extras=["whole ol latest-kind selector"])
add("oloeorain", ["REQUIRE"], ["scope", "source_focus", "approach", "material", "t1"], {"new_supply":"RaisedExhalation"},
    "At that approached adjacent source at t1, SUN raises X; retain the source owner and time of this antecedent supply.",
    extras=["complete ol·o·e·or·aI residual", "approach causes raised supply"])
add("qotaiin", ["CONSEQUENT", "aN"], ["scope", "latest_ref", "old_end", "u", "kind2", "order"], {"v":"PhysicalInstanceVar", "new_generation":"WindGeneration"},
    "Conditional on retained cessation/solar/material premises, a newly generated v of kind2 follows u's cessation. qot residual introduces generation; aN retains its description, not just the wind's kind name.", "generation_an",
    ["qot·aN generation residual", "v binder", "ordered generation event", "generation provenance", "reference dereference"])
add("tchedy", ["CONSEQUENT"], ["scope", "v", "new_generation", "kind2", "t1"], {"new_blowing":"BlowingState"},
    "Generated v blows from kind2's source at the successor state t1.",
    extras=["t·Cedy new-blowing residual"])
add("otedy", ["COMPARE"], ["scope", "u", "v", "new_generation"], {"different_instances":"PhysicalIdentityInequality"},
    "The generated successor v is physically distinct from preceding u; equality of kind labels alone cannot prove participant identity.",
    extras=["ot·edy identity residual", "u!=v explicit relation"])
add("qotchdy", ["CONSEQUENT"], ["scope", "new_generation", "new_supply", "approach", "driver"], {"generation_cause":"GenerationCausalRelation"},
    "The raised dry exhalation under solar approach causes v's generation, rather than mere replacement of its label.",
    extras=["qot·Cdy causal residual", "solar/material-to-generation causal edge"])
add("chckhey", ["COMPARE"], ["scope", "adjacency", "old_end", "new_generation"], {"same_frame":"RetainedFrameRelation"},
    "Both event source regions use the same F/O relation, and their neighboring positions are retained across the transition.",
    extras=["C·K·ey same-frame residual", "cross-time source-frame retention"])
add("qtchedy", ["CONSEQUENT"], ["scope", "old_end", "new_blowing", "different_instances", "t0", "t1"], {"two_states":"TwoIndexedStates"},
    "Write the two indexed relational states: u blew before cessation at t0; in successor state t1 u is ceased while distinct v blows. No continuing-u alias is permitted.",
    extras=["q·t·Cedy state residual", "two time-indexed state relations", "u state persistence after cessation"])
add("qodar", ["COMPARE"], ["scope", "order", "withdrawal", "approach", "old_end", "new_generation"], {"ordered_chain":"OrderedCausalChain"},
    "Retain withdrawal/lost supply/cessation before approach/raised supply/generation; ordering does not require a measured hiatus or angle.",
    extras=["q·od·ar ordered-chain residual", "causal-chain reference collection"])
add("qotedar", ["DESCRIBE"], ["scope", "two_states", "old_end", "new_generation"], {"unbroken_exclusion":"DefinitionExclusion"},
    "If the first participant instead continues unbroken, it is not this cessation-followed-generation rule; mere apparent turn is insufficient.",
    extras=["qot·e·dar continuation-exclusion residual", "counterfactual definition condition"])
add("qokar", ["DESCRIBE"], ["scope", "different_instances", "kind1", "kind2"], {"kind_identity_limit":"KindInstanceDistinction"},
    "Kind or name relations do not erase the expressly bound distinct physical participants and their provenance.",
    extras=["qok·ar kind/instance residual"])
add("qotchd", ["DESCRIBE"], ["scope", "adjacency", "same_frame"], {"adjacency_limit":"RelationDistinction"},
    "The generation relation is neighboring source succession, not replacement by a diametrically opposite wind or an assumed four-leg cycle.",
    extras=["full qot·C·d adjacency distinction residual"])
add("qotom", ["DESCRIBE"], ["scope", "old_end", "withdrawal", "old_supply_ends", "approach", "new_supply", "new_generation", "generation_cause", "two_states", "ordered_chain", "unbroken_exclusion", "kind_identity_limit", "adjacency_limit"], {"gyration_rule":"DescriptionRecord"},
    "Collect the complete substantive implication: solar-driven first cessation then adjacent distinct generation, with written identities, source owners, times, causal relations and exclusions.",
    extras=["qot·o·m rule-collection residual", "explicit antecedent/consequent collection"])
add("soiis", ["QUANTIFY", "DESCRIBE"], ["scope", "gyration_rule"], {"quantified_rule":"DescriptionRecord"},
    "Universally quantify the bound kinds, instances, frame and times in the collected conditional; wrap the resulting rule as a nonempty description for reference.",
    extras=["s·o·i·i·s universal closure residual", "ConditionalRule-to-DescriptionRecord explicit wrapping"])
add("shedaiin", ["QUALIFIER", "d", "aN"], ["scope", "focus", "latest_ref", "quantified_rule"], {},
    "Se qualifies the referenced generic kind-relation rule for retention; d collates its nonempty dependency closure and aN retains it. Se is not the So strength qualifier.", "qualified_an",
    ["Se generic-kind-rule residual", "Se·daN juxtaposition rule", "reference dereference"])
add("chokcod", ["CLOSE"], ["scope", "latest_ref", "quantified_rule"], {"terminal":"TerminalRule"},
    "Consume the retained full generic relation rule, publish and close the E topic including its ending.", "close",
    ["complete C·ok·c·od terminal residual", "explicit retained-reference dereference"])

for e in E:
    if e['raw_form'] in {'opchdy','olfar','ockhdor','qotaiin'}:
        e['reference_projection']={'opchdy':{'type':'KindVar','count':2},
                                   'olfar':{'type':'StrengthPartition','count':1},
                                   'ockhdor':{'type':'KindClassification','count':1},
                                   'qotaiin':{'type':'RaisedExhalation','count':1}}[e['raw_form']]
        e['additional_costs'].append('explicit typed retained-content projection')

def descendants(value, nodes):
    """Resolve the actual immutable retained DAG, without source-position branches."""
    found, visited = [], set()
    def walk(x):
        if isinstance(x,str) and x in nodes and x not in visited:
            visited.add(x); found.append(nodes[x]); walk(nodes[x].get('content'))
        elif isinstance(x,dict):
            for v in x.values():walk(v)
        elif isinstance(x,list):
            for v in x:walk(v)
    walk(value['id'])
    return found


def materialize():
    source = json.loads((D/'src/SOURCE.json').read_text())
    freeze = json.loads((D/'src/C_CONSTRUCTORS.json').read_text())
    assert len(freeze['families']) == 12 and len(freeze['opaque_constants']) == 6
    lookup = {e['raw_form']:e for e in E}
    rows, shared, nodes, consumers, units = [], [], {}, collections.defaultdict(set), []
    value_consumers=collections.defaultdict(set)
    blocks = {}
    for r in source['rows']:
        blocks.setdefault((r['edition'],r['block']), []).append(r)
    for (edition, block), rr in blocks.items():
        state, unknowns, blockrows, closed = {}, [], [], False
        for pos, native in enumerate(rr):
            sid, raw = native['source_group_id'], native['ivtff_group_raw']
            e = lookup.get(raw)
            row = dict(native=native, entry_id=e['entry_id'] if e else None,
                       status='UNKNOWN', interpretation=e['formula'] if e else None,
                       arguments=[], returns=[], consumer_source_ids=[],
                       cost={'dictionary_entry':e['entry_id'] if e else None, 'unknown_carry_rows':0},
                       referring={'scope':None,'owner':None,'time':None,'condition':None})
            rows.append(row);blockrows.append(row)
            if not e:
                row['barrier']='UNKNOWN exact whole; no effect executed and no inert-token assumption'
                unknowns.append((pos,sid)); continue
            op=e['operation']
            if op=='open':
                state={}; unknowns=[]; closed=False
            missing=[role for role in e['required_roles'] if role not in state]
            if missing:
                row['status']='BLOCKED_MISSING_OPERAND';row['missing_roles']=missing
                row['barrier']='same entry retained; missing typed roles, not a contradiction'
                continue
            args=[]
            for role in e['required_roles']:
                value=state[role]
                args.append({'role':role,'type':value['type'],'value_id':value['id'],
                             'producer_source_ids':[value['source_id']]})
                consumers[value['source_id']].add(sid)
                value_consumers[value['id']].add(sid)
            row['arguments']=args
            if 'reference_projection' in e:
                projection=e['reference_projection']
                values=[v for v in descendants(state['latest_ref'],nodes) if v['type']==projection['type']]
                if len(values)!=projection['count']:
                    row['status']='BLOCKED_REFERENCE_CONTENT'
                    row['barrier']='Retained record does not supply the exact typed content required by the fixed consumer'
                    row['reference_projection']={'required':projection,'actual_value_ids':[v['id'] for v in values]}
                    continue
                row['reference_projection']={'reference_value_id':state['latest_ref']['id'],
                                             'actual_typed_content':[{'type':v['type'],'value_id':v['id'],'producer_source_ids':[v['source_id']]} for v in values]}
                args.extend({'role':'retained_content','type':v['type'],'value_id':v['id'],
                             'producer_source_ids':[v['source_id']]} for v in values)
                for value in values:
                    consumers[value['source_id']].add(sid)
                    value_consumers[value['id']].add(sid)
            crossed=sorted({us for role in e['required_roles'] for up,us in unknowns
                            if state[role]['position'] < up < pos})
            row['cost']['unknown_carry_rows']=len(crossed)
            if crossed: row['cost']['unknown_carry_source_ids']=crossed
            boundary=(native['left_separator']=='UNCERTAIN_SMALL_SPACE' or native['right_separator']=='UNCERTAIN_SMALL_SPACE')
            row['status']='ACCOUNTED_C0_WITH_GAP_ASSUMPTION' if crossed else 'ACCOUNTED_C0'
            if boundary:
                row['status']='PARTIAL_BOUNDARY_REPLAY'
                row['barrier']='Native uncertain seam retained; isolated-whole execution is diagnostic, not licensed full chunk semantics'
            row['referring']={'scope':state.get('scope',{}).get('id'),
                              'owner':'O relative to F, explicitly paid ambient variables',
                              'time':'generic; see t0/t1/ordered event roles, no observed episode',
                              'condition':'quantified conditional antecedent, not an occurrence claim'}
            def produce(role, typ, content=None):
                value=dict(id=sid+'#'+role,type=typ,source_id=sid,position=pos)
                if content is not None:value['content']=content
                state[role]=value;nodes[value['id']]=value;row['returns'].append(value.copy())
                return value
            if op=='kind':
                count=sum(k.startswith('kind') and k[4:].isdigit() for k in state)+1
                value=produce('kind'+str(count),'KindVar',{'quantifier':'universal','ordinal':count})
                state['latest_kind']=value
                produce('focus','DescriptionRecord',{'members':[state['kind'+str(n)]['id'] for n in range(1,count+1)],'predicate':'kind variables in this generic topic'})
            elif op in {'an','dan','qualified_an','residual_an','generation_an'}:
                for role,typ in e['outputs'].items():produce(role,typ,{'predicate':e['formula'],'argument_value_ids':[a['value_id'] for a in args]})
                if op in {'dan','qualified_an'}:
                    old=state['focus']
                    desc=produce('collated_description','DescriptionRecord',{'selected_completed_description':old['id'],'dependency_value_ids':[a['value_id'] for a in args],
                                                                             'qualifier': 'So strength partition' if raw=='shodaiin' else 'Se generic rule' if raw=='shedaiin' else None})
                    row['internal_operations']=[{'interface_id':'d','arguments':[old['id']], 'returned_value':desc['id']}]
                elif op in {'residual_an','generation_an'}:
                    desc=produce('prepared_description','DescriptionRecord',{'predicate':e['formula'],'dependency_value_ids':[a['value_id'] for a in args]})
                else:desc=state['focus']
                ref=produce('latest_ref','BoundDescriptionRef',{'retains':desc['id'],'nonempty':True,'semantic_effect':'retained reference available to subsequent written consumers'})
                value_consumers[desc['id']].add(sid)
                produce('focus','DescriptionRecord',{'retained_description':desc['id'],'bound_ref':ref['id']})
                if raw in {'aiin','daiin','shodaiin'}:
                    shared.append({'source_group_id':sid,'raw_form':raw,'interface_id':'aN',
                                   'arguments':[{'type':'DescriptionRecord','value_id':desc['id'],'producer_source_ids':[desc['source_id']]}],
                                   'returned_value':ref,'consumer_source_ids':[],
                                   'effect':'Non-null reference allocation, later content retrieval constrains consumer; not a world truth assertion.', 'status':row['status']})
            else:
                for role,typ in e['outputs'].items():produce(role,typ,{'predicate':e['formula'],'argument_value_ids':[a['value_id'] for a in args]})
                if op!='open':produce('focus','DescriptionRecord',{'predicate':e['formula'],'dependency_value_ids':[a['value_id'] for a in args],
                                                                 'contribution_value_ids':[v['id'] for v in row['returns']]})
                if op=='close':closed=True
            row['delta']={'operation':op,'written_formula':e['formula']}
        if block in {'N','E'}:
            barriers=[r for r in blockrows if r['status']!='ACCOUNTED_C0']
            complete=not barriers and closed
            units.append({'edition':edition,'block':block,'source_ids':[r['native']['source_group_id'] for r in blockrows],
                          'native_count':len(blockrows),'literal_assigned_count':sum(r['entry_id'] is not None for r in blockrows),
                          'complete':complete,'status':'COMPLETE_CONDITIONAL_C0_PROPOSAL' if complete else 'PARTIAL_REPLAY',
                          'first_barrier':{'source_group_id':barriers[0]['native']['source_group_id'],'raw_form':barriers[0]['native']['ivtff_group_raw'],'status':barriers[0]['status'],'reason':barriers[0].get('barrier')} if barriers else None,
                          'closed':closed,'status_counts':dict(collections.Counter(r['status'] for r in blockrows))})
    # Preserve canonical source order even though replay is isolated per reader/block.
    byid={r['native']['source_group_id']:r for r in rows}
    rows=[byid[r['source_group_id']] for r in source['rows']]
    for row in rows:
        row['consumer_source_ids']=sorted(consumers[row['native']['source_group_id']])
        row['returned_value_consumers']=[{'value_id':v['id'],'type':v['type'],
                                         'consumer_source_ids':sorted(value_consumers[v['id']])} for v in row['returns']]
    for use in shared:use['consumer_source_ids']=sorted(value_consumers[use['returned_value']['id']])
    for e in E:e['occurrences']=[r['source_group_id'] for r in source['rows'] if r['ivtff_group_raw']==e['raw_form']]
    outside=[{'source_group_id':r['native']['source_group_id'],'raw_form':r['native']['ivtff_group_raw'],'entry_id':r['entry_id'],
              'status':r['status'],'missing_roles':r.get('missing_roles',[])} for r in rows if r['entry_id'] and r['native']['block'] not in {'N','E'}]
    costs={'initial_constructor_families':12,'initial_opaque_constants':6,'initial_exact_entries':5,
           'dictionary_entries':len(E),'extension_exact_entries':sum(e['extension'] for e in E),
           'whole_residual_payloads':len(E),'additional_payload_or_rule_items':sum(len(e['additional_costs']) for e in E),
           'alternate_aliases':0,'alternate_whole_extensions':0,'automatic_casts':0,
           'payload_record_type_names':sorted({typ for e in E for typ in e['outputs'].values()}),
           'payload_record_type_policy':'Each named type denotes its separately paid exact-entry payload; these are not confirmed lexical types or automatic casts.',
           'ambient_inputs':['O','F','X','SUN','QH','QM'],
           'defaults':['ordered kind-introduction buffer','latest completed description focus','latest retained reference','latest introduced kind source selector'],
           'scope_transitions':['sain opens N generic topic','sosees closes N','pchedeey explicitly opens/reset E','chokcod closes E'],
           'unknown_carry_row_edge_count':sum(r['cost']['unknown_carry_rows'] for r in rows),
           'unknown_carry_occurrence_rows':sum(r['cost']['unknown_carry_rows']>0 for r in rows),
           'time_and_identity_obligations':'See additional_costs and formula of qotor/olfar/qocthey/oteey/qotaiin/otedy/qtchedy/qodar; no kind equality cast.',
           'unused_instructions':[r['native']['source_group_id'] for r in rows if r['entry_id'] and r['status']=='BLOCKED_MISSING_OPERAND'],
           'zero_consumer_accounted_outputs':[r['native']['source_group_id'] for r in rows if r['status'].startswith('ACCOUNTED') and not r['consumer_source_ids']],
           'unused_retained_reference_values':[v['id'] for r in rows for v in r['returns'] if v['type']=='BoundDescriptionRef' and not value_consumers[v['id']]],
           'unweighted_costs_only':True}
    account={'schema':'GDT1131_C_ACCOUNT_v1','candidate_id':'C','status':'COMPLETE_IT_CONDITIONAL_C0_HYPOTHESIS_ALTERNATES_PARTIAL',
             'source_sha256':sha(D/'src/SOURCE.json'),'constructor_sha256':sha(D/'src/C_CONSTRUCTORS.json'),
             'claim_ceiling':'Exploratory internally connected authored reading; no independent manuscript meaning validation, translated words remain zero.',
             'status_definitions':{'ACCOUNTED_C0':'Fixed entry supplied typed operands in this authored hypothesis; not semantic validation.',
                                   'ACCOUNTED_C0_WITH_GAP_ASSUMPTION':'Fixed entry has typed operands but carries them across explicitly priced UNKNOWN rows.',
                                   'PARTIAL_BOUNDARY_REPLAY':'Native uncertain boundary prevents claiming complete isolated-whole semantics.',
                                   'BLOCKED_MISSING_OPERAND':'Entry assigned identically, cannot execute without its typed producers.',
                                   'BLOCKED_REFERENCE_CONTENT':'Fixed consumer cannot project the required typed content from the actual retained record.',
                                   'UNKNOWN':'No assigned exact whole, not inert.'},
             'dictionary':E,'rows':rows,'primary_units':units,'shared_part_uses':shared,'costs':costs,
             'outside_assigned_recurrences':outside,
             'retained_countercase':{'sequence':'IT/ZL or shedy tedy sodaiiin chy; RF or {ch\u0027}edy tedy sodaiiin chy',
                                    'or_entry':'same KIND entry; missing explicit generic scope at .13, so blocked',
                                    'remaining_exact_wholes':'shedy / {ch\u0027}edy / tedy / sodaiiin / chy remain UNKNOWN; no Assertable cast and no silent equivalence with sheedy/shodaiin',
                                    'decision':'Does not reproduce the old or(shedy) type cast; does not claim a complete S account. Missing scope is a debt.'},
             'world_counterfactuals':[
                 {'unit':'IT N','change':'Under identical F, original u/v, opposed confrontation and unequal strength, only a fresh same-kind replacement survives while original stronger ceases.',
                  'violated_written_predicate':'olfar retains stronger from the original pair, not merely its kind.',
                  'nonseed_source_ids':['IT2a|f85r2.2|G005','IT2a|f85r2.3|G001','IT2a|f85r2.3|G002','IT2a|f85r2.3|G004'],
                  'limit':'A generic implication constrains a world satisfying its antecedent; it does not establish that this world occurred.'},
                 {'unit':'IT E','change':'Keep solar/source/material premises but let u continue uninterrupted and merely change its label to v at the adjacent source.',
                  'violated_written_predicate':'qocthey binds cessation; otedy requires v!=u; qtchedy requires ceased u and blowing v in successor state; qotchdy binds new-generation cause.',
                  'nonseed_source_ids':['IT2a|f85r2.8|G003','IT2a|f85r2.9|G002','IT2a|f85r2.9|G004','IT2a|f85r2.9|G005','IT2a|f85r2.10|G001','IT2a|f85r2.10|G003'],
                  'limit':'These are hypothetical meanings assigned to exact manuscript groups, not meaning-discriminating observed anchors.'}],
             'remaining_equivalences':['Consistent renaming of generic variables/kinds/frames preserves meaning.','The same predicates may be expressed by dynamic event updates or static indexed states; this account explicitly uses both event descriptions and two indexed states.','Generic suppression and generic succession can coexist in one account; the candidate label is not exclusive.'],
             'manuscript_owned_distinguishing_consequence':None,
             'assumptions_dependencies':['Hypothetical lexical and compositional bindings, including every exact whole residual, remain unconfirmed.','Same-word entry invariance is enforced, but outside missing scope/arguments do not supply complete readings.','No cardinal, geometric ownership, four semantic legs, image object identification or Latin phonetic mapping is donated.','Fixed structural cuts license form retention, not the proposed semantics.','Observer/material/solar/quality constants are paid ambient inputs, not observed manuscript values.','Conditional consequence truth follows only in worlds satisfying stated antecedents; no actual weather history inferred.'],
             'independent_confirmation_capacity':0,'confirmed_translated_words':0,'other_authors_read':False}
    (D/'artifacts/C_ACCOUNT.json').write_text(json.dumps(account,indent=2,ensure_ascii=False)+'\n')
    report={'candidate_id':'C','native_rows':len(rows),'primary_units':units,'dictionary_entries':len(E),
            'costs':costs,'shared_supported_forms':sorted({x['raw_form'] for x in shared}),
            'shared_consumed_it_forms':sorted({x['raw_form'] for x in shared if x['source_group_id'].startswith('IT2a|') and x['consumer_source_ids']}),
            'status_counts':dict(collections.Counter(r['status'] for r in rows)),
            'all_native_fields_preserved':all(r['native']==s for r,s in zip(rows,source['rows'])),
            'all_exact_recurrences_same_entry':all(r['entry_id']==lookup[r['native']['ivtff_group_raw']]['entry_id'] for r in rows if r['native']['ivtff_group_raw'] in lookup),
            'semantic_validation':False}
    assert len(rows)==473 and report['all_native_fields_preserved'] and report['all_exact_recurrences_same_entry']
    assert len(report['shared_consumed_it_forms']) >= 2
    initial=json.loads((D/'artifacts/C_INITIAL_FREEZE_RECEIPT.json').read_text())
    assert sha(D/'src/C_CONSTRUCTORS.json')==next(iter(initial['files'].values()))
    (D/'artifacts/C_CHECK.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['native_rows','dictionary_entries','shared_supported_forms','status_counts','all_native_fields_preserved','all_exact_recurrences_same_entry']}))
    for u in units:print(u['edition'],u['block'],u['status'],u['first_barrier'])

if __name__=='__main__':materialize()
