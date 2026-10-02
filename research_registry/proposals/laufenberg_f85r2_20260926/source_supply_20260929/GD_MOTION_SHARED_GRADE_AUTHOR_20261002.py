"""Finite exploratory C0 semantic author: owned IT32 and historical P12 display33.
No decoder or general parser. Clause segmentation/context bindings are declared
manual authoring inputs. Every new motion grade is computed by one function.
"""
from pathlib import Path
import copy, hashlib, json
P=Path(__file__).resolve().parent
A=lambda p,*a:{'op':'ATOM','predicate':p,'arguments':list(a)}
And=lambda *a:{'op':'AND','arguments':list(a)}
Pkg=lambda e,c:{'op':'WITNESS_PACKAGE','exported_ports':[e],'condition':c}

def grade(n):
    return ('PULSED','UNMARKED','CONTINUOUS')[n]

def pattern(n,w,e,x,I):
    if n==1:return None
    if n==2:return A('CONTINUOUS_FULL_PHASE',w,e,I)
    # Two genuinely positive-flow periods separated by zero flow inside I.
    p1,z,p2=e+':positive1',e+':zero',e+':positive2'
    return {'op':'EXISTS','binders':[p1,z,p2],'body':And(
        A('NONEMPTY_SUBINTERVAL',p1,I),A('NONEMPTY_SUBINTERVAL',z,I),A('NONEMPTY_SUBINTERVAL',p2,I),
        A('POSITIVE_FLOW_THROUGHOUT',w,e,x,p1),A('ZERO_FLOW_THROUGHOUT',w,e,x,z),
        A('POSITIVE_FLOW_THROUGHOUT',w,e,x,p2),
        A('END_NOT_AFTER_START',p1,z),A('END_NOT_AFTER_START',z,p2))}

def actual(root,w,e,x,I,n=None):
    f=[A('ACTUAL',w,e),A(root,w,e,x,I)]
    if n is not None:
        q=pattern(n,w,e,x,I)
        if q:f.append(q)
    return Pkg(e,And(*f))

def event_capability(root,w,x,I,n=None):
    spec={'root_relation':root,'argument':x,'interval':I,
          'event_condition':actual(root,'$possible_world','$possible_event',x,I,n)}
    if n is not None:spec['grade']=grade(n)
    return A('CAPABLE',w,x,spec)

def motion(stem,n,mode,w,e,x,I,host=None):
    if stem=='lk' and mode!='edy':raise ValueError('No LK EY frame licensed')
    if mode=='edy':
        f=actual('FLOW',w,e,x,I,n)
        return And(f,A('USING',w,host,e)) if stem=='lk' else f
    if stem!='qok' or mode!='ey':raise ValueError('Outside licensed family')
    # The same actual pattern is placed under capability, not asserted actual.
    return And(A('LIQUID',w,x),event_capability('FLOW',w,x,I,n))

def flow_routes():
    out={}
    for stem in ['qok','lk']:
        for n in range(3):
            for mode in (['ey','edy'] if stem=='qok' else ['edy']):
                raw=stem+'e'*n+mode
                out[raw]={'stem':stem,'extra_E':n,'mode':mode,'grade':grade(n)}
    return out
ROUTES=flow_routes()
NEW_ASSEMBLIES={
 'qolchey':['qol','chey'],'otal':['ot','al'],'otchey':['ot','chey'],
 'qoky':['qok','y'],'tol':['t','ol'],'qokylddy':['qok','y','l','ddy'],
 'dain':['dain'],'shckhedy':['sh','ckh','edy'],'sheey':['sh','e','ey'],
 'oldy':['ol','dy'],'qody':['qo','dy'],'kesd':['kes','d'],
 'salchedy':['sa','lchedy'],'s':['s'],'okeedy':['oke','edy'],
 'sokeedy':['s','oke','edy'],'saii':['sa','ii'],'sairn':['sa','irn']}
PRIMITIVES={
 'qol':'THROUGH: consume a location noun and return path adjunct',
 'chey':'CONDUIT noun; first mention introduces C, later scoped mention refers to C',
 'ot':'AT: consume a location noun and return location adjunct',
 'al':'OUTLET noun O, stored as current explicit goal reference',
 'y':'INTENTION frame for FLOW, distinct from EY capability and independent of the grade map',
 't':'GOAL binder consuming an intention and a goal-reference specification',
 'ol':'reference specification for the already written outlet O',
 'l':'link an intention schema to the matching live written intention; no new plan',
 'ddy':'FULFILL: introduce actual completed event satisfying that linked intention',
 'dain':'ORDERED_SERIES discourse operator; successive actual event mentions receive successive phases',
 'sh':'DISPENSE event root in SHCKH/SHEE routes only; frozen SHEDY remains exact MOIST_PREPARATION',
 'ckh':'DOSE internal-object constructor for DISPENSE; exports a dose material and dose predicate',
 'e_SH':'scoped material-patient capability frame; not QOK/LK grade or a universal E value',
 'dy':'REFERENCE_CLOSURE on OL location and QO material specifications; grammar consumes resolved type',
 'qo':'reference specification for the current material of this written case',
 'kes':'MOVING current-state predicate, not an efficacy or heat claim',
 'd':'NEGATION of the supplied state predicate in KESD only',
 'sa':'TOPIC frame: bind an existing material-property or relational material noun as topic/subject',
 's':'FINAL_PHASE operator; prefixes the following actual event or an event expression',
 'oke':'RETURN_FLOW event root; returns to the first explicitly introduced conduit C',
 'ii':'REMAINDER relational material noun',
 'irn':'REMAINDER relational material noun; explicitly paid semantic alias of II, no spelling normalization'}
P12_LINES=[
('f83r.25','qokeedy qolchey qokeey qokedy chedy otal'),
('f83r.26','otchey qokeey qoky tol shedy qokylddy'),
('f83r.27','dain chedy qokeedy shckhedy shckhedy'),
('f83r.28','saiin cheeky sheey qokedy shedy oldy'),
('f83r.29','salchedy cheey qody kesd oldy'),
('f83r.30','s okeedy qokeedy qoky saii')]

# Part functions reduce typed operands; no compound supplies a stored clause.
def location_relation(operator,noun,w,owner,event):
    kind,ref=noun
    return And(A(kind,w,ref),A(operator,w,event if operator in ['THROUGH','AT_EVENT'] else owner,ref))

def close_reference(spec,context):
    ref=context['references'].get(spec)
    if ref is None:raise ValueError('Missing written reference donor: '+spec)
    return ref

def intend(root,w,plan,owner):
    schema={'root':root,'patient':owner,'pattern':'UNMARKED','plan':plan,'goal':None}
    return schema,Pkg(plan,A('INTENDED',w,plan,owner,{'root':root,'pattern':'UNMARKED'}))

def link_intention(root,owner,context):
    prior=context.get('live_intention')
    if not prior or prior['root']!=root or prior['patient']!=owner:
        raise ValueError('L lacks a matching written intention')
    return prior

def fulfill(schema,w,event,interval):
    facts=[actual(schema['root'],w,event,schema['patient'],interval,1),
           A('COMPLETED',w,event),A('FULFILLS',w,event,schema['plan'])]
    if schema['goal'] is not None:
        facts.extend([A('GOAL',w,event,schema['goal']),A('GOAL_SATISFIED',w,event,schema['goal'])])
    return And(*facts)

def internal_object(root,object_kind,w,event,patient,interval,object_port):
    return And(A(object_kind,w,object_port),A('MATERIAL',w,object_port),
               A('PORTION_OF',w,object_port,patient),actual(root,w,event,patient,interval),
               A('INTERNAL_OBJECT',w,event,object_port))

def topicize(base,w,owner,time,context):
    if base['kind']=='PROPERTY':return And(A('TOPIC',w,owner),A(base['predicate'],w,owner,time))
    material=base['port'];source=close_reference('case_material',context)
    return And(A('MATERIAL',w,material),A(base['predicate'],w,material,source),A('TOPIC',w,material))

def final_phase(expression,w,interval):
    return And(A('FINAL_CASE_PHASE',w,interval),expression)

def substitute(o,b):
    if isinstance(o,str):return b.get(o,o)
    if isinstance(o,list):return [substitute(x,b) for x in o]
    if isinstance(o,dict):return {k:substitute(v,b) for k,v in o.items()}
    return o

def compile_word(raw,w,x,e,I,ctx,variant):
    if raw in ROUTES:
        r=ROUTES[raw];return motion(r['stem'],r['extra_E'],r['mode'],w,e,x,I,ctx.get('host'))
    if raw=='qolchey':return location_relation('THROUGH',('CONDUIT',ctx['references']['conduit']),w,x,e)
    if raw=='otal':return location_relation('AT_EVENT',('OUTLET',ctx['references']['outlet']),w,x,e)
    if raw=='otchey':return location_relation('AT_MATERIAL',('CONDUIT',close_reference('conduit',ctx)),w,x,e)
    if raw=='tol':return A('GOAL',w,ctx['intention'],close_reference('outlet',ctx))
    if raw=='oldy':return A('AT_REFERENT',w,ctx['reference_target'],close_reference('outlet',ctx))
    if raw=='qody':return A('SAME_MATERIAL',w,x,close_reference('case_material',ctx))
    if raw=='chedy':return A('PURE',w,x,ctx['time'])
    if raw=='shedy':return A('MOIST_PREPARATION',w,x)
    if raw=='cheey':return A('CLEAR',w,x,ctx['time'])
    if raw=='qoky':return intend('FLOW',w,ctx['intention'],x)[1]
    if raw=='qokylddy':
        return fulfill(link_intention('FLOW',x,ctx),w,e,I)
    if raw=='dain':return A('ORDERED_SERIES',w,'Series3')
    if raw=='shckhedy':
        return internal_object('DISPENSE','DOSE',w,e,x,I,ctx['dose'])
    if raw=='sheey':return event_capability('DISPENSE',w,x,I)
    if raw=='saiin':return A('SUBSEQUENT',w,I,ctx['previous_phase'])
    if raw=='cheeky':return A('CAREFUL',w,e)
    if raw=='kesd':return {'op':'NOT','argument':A('MOVING',w,x,ctx['time'])}
    if raw=='solchedy':return A('HERE',w,close_reference('outlet',ctx),ctx['time'])
    if raw=='salchedy':
        return topicize({'kind':'PROPERTY','predicate':'PURIFIED' if variant=='G' else 'PURIFICATION_INTENDED'},w,x,ctx['time'],ctx)
    if raw=='s':return A('FINAL_CASE_PHASE',w,I)
    if raw in ['okeedy','sokeedy']:
        f=And(actual('RETURN_FLOW',w,e,x,I),A('RETURN_GOAL',w,e,close_reference('conduit',ctx)))
        return final_phase(f,w,I) if raw=='sokeedy' else f
    if raw in ['sairn','saii']:
        return topicize({'kind':'NOUN_RELATION','predicate':'REMAINDER_OF','port':'R'},w,x,ctx['time'],ctx)
    return {'op':'UNASSIGNED','raw':raw}

def execute(lines,namespace,variant):
    """Execute the one declared six-clause reading; never infer segmentation."""
    rows=[];bindings={'$X3':'L'};facts=[];edges=[]
    references={'conduit':None,'outlet':None,'case_material':None};live=None
    reference_sources={};series_active=False;series_events=[];final_pending=False
    contexts={25:('$X1','E1','I1','T1'),26:('$X2','E2','I2','T2'),
              27:('$X3','E3','I3a','T3'),28:('$X4','E4','I4','T4'),
              29:('$X5','State5','J5','T5'),30:('$X6','E6','I6','T6')}
    for locus,words,source_ids in lines:
        number=int(locus.split('.')[-1]);x,e,I,t=contexts[number]
        for index,raw in enumerate(words):
            sid=source_ids[index];before=dict(bindings)
            ctx={'time':t,'intention':'P2' if number==26 else 'P6',
                 'reference_target':e if number==28 else x,
                 'references':dict(references),'live_intention':copy.deepcopy(live),
                 'previous_phase':series_events[-1][1] if series_events else None}
            if raw=='qolchey':references['conduit']='C';reference_sources['conduit']=sid;ctx['references']=dict(references)
            if raw=='otal':references['outlet']='O';reference_sources['outlet']=sid;ctx['references']=dict(references)
            if raw=='dain':series_active=True
            if raw=='saiin':series_active=False
            if raw=='s':final_pending=True
            if raw=='qoky':live=intend('FLOW','W_actual',ctx['intention'],x)[0];ctx['live_intention']=copy.deepcopy(live)
            if raw=='tol':
                if live is None:raise ValueError('T lacks a written intention')
                live['goal']=close_reference('outlet',ctx);ctx['live_intention']=copy.deepcopy(live)
            event=e;phase=I
            if number==27 and raw=='shckhedy':
                ordinal=sum(r['raw']=='shckhedy' for r in rows)+1
                event='E3b' if ordinal==1 else 'E3c';phase='I3b' if ordinal==1 else 'I3c';ctx['dose']='D'+str(ordinal)
            output=compile_word(raw,'W_actual',x,event,phase,ctx,variant)
            is_actual_event=(raw in ROUTES and ROUTES[raw]['mode']=='edy') or raw=='shckhedy'
            if series_active and is_actual_event:
                output=And(output,A('MEMBER_EVENT','Series3',event))
                if series_events:edges.append(A('BEFORE_PHASE',series_events[-1][1],phase))
                series_events.append((event,phase))
            if final_pending and raw=='okeedy':
                output=final_phase(output,'W_actual',phase);final_pending=False
            pending=[]
            if raw=='qokeey':
                bindings[x]='L'
                if references['case_material'] is None:references['case_material']='L';reference_sources['case_material']=sid
            if raw=='shedy':bindings[x]='L'
            if raw=='qody':bindings[x]='L'
            if raw in ['sairn','saii']:bindings[x]='R'
            if raw=='qoky':pending=['Live intended FLOW '+ctx['intention']+' available for L/DDY or final plan mention']
            row={'source_group_id':sid,'raw':raw,'clause':number,'assembly':
                 ([ROUTES[raw]['stem'],'e'*ROUTES[raw]['extra_E'],ROUTES[raw]['mode']] if raw in ROUTES else NEW_ASSEMBLIES.get(raw,[raw])),
                 'operator_input':{'world':'W_actual','patient_port':x,'event_port':event,'phase':phase,'reference_time':t,'context':ctx},
                 'returned_predicates':output,'bindings_before':before,'bindings_after':dict(bindings),
                 'reference_registers_after':dict(references),'live_intention_after':copy.deepcopy(live),
                 'reference_donor_source_ids':dict(reference_sources),
                 'pending_contribution':pending,'status':'DERIVED_C0' if output.get('op')!='UNASSIGNED' else 'UNASSIGNED_NATIVE_VARIANT'}
            rows.append(row);facts.append(output)
    # Explicit grammar/scene relations, not functions smuggled into word roots.
    edges.extend([A('BEFORE_PHASE','I1','I2'),A('BEFORE_PHASE','I2','I3a'),
           A('BEFORE_PHASE','I3a','I3b'),A('BEFORE_PHASE','I3b','I3c'),
           A('BEFORE_PHASE','I3c','I4'),A('BEFORE_PHASE','I4','J5'),A('BEFORE_PHASE','J5','I6'),
           A('CURRENT_CASE_MATERIAL','L'),A('MATERIAL','W_actual','L'),
           A('FULL_PHASE','E1','I1'),A('FULL_PHASE','E4','I4'),
           A('SAME_TIME','T1',{'phase':'I1','position':'onset'}),
           A('SAME_TIME','T2',{'phase':'I2','position':'onset'}),
           A('SAME_TIME','T3',{'phase':'I3a','position':'onset'}),
           A('SAME_TIME','T4',{'phase':'I4','position':'onset'}),
           A('SAME_TIME','T5',{'phase':'J5','position':'description-time'}),
           A('SAME_TIME','T6',{'phase':'I6','position':'onset'}),
           A('MOVE_IMPLIES_FLOW_MOTION','FLOW','MOVING')])
    for row in rows:
        row['resolved_predicates']=substitute(row['returned_predicates'],bindings)
        row['later_consumption']='Collected into final conjunction; patient ports resolved by the explicit binding table and intention P2 consumed by QOKYLDDY.'
    final=And(*(substitute(f,bindings) for f in facts),*edges)
    def collect_packages(o):
        if isinstance(o,list):return [collect_packages(v) for v in o]
        if isinstance(o,dict):
            if o.get('op')=='WITNESS_PACKAGE':return collect_packages(o['condition'])
            return {k:collect_packages(v) for k,v in o.items()}
        return o
    ports=['L','C','O','R','D1','D2','E1','E2','E3','E3b','E3c','E4','E6','P2','P6',
           'I1','I2','I3a','I3b','I3c','I4','J5','I6','T1','T2','T3','T4','T5','T6']
    final={'op':'EXISTS','binders':ports,'body':collect_packages(final)}
    return {'namespace':namespace,'parent_variant':variant,'rows':rows,'bindings':bindings,
            'final_predicates':final,'context_edges':edges,'ordered_series_actual_members':series_events,
            'intention_P2_consumed':True,'final_P6_status':'Terminal descriptive intention mention; no unwritten fulfillment instruction or claim.',
            'unresolved_patient_ports':[v[0] for v in contexts.values() if v[0] not in bindings],
            'status':'COMPLETE_C0' if all(r['status']=='DERIVED_C0' for r in rows) and all(v[0] in bindings for v in contexts.values()) else 'PARTIAL'}

def run():
    es_path=P/'ES_JOINT_FAMILY_AUTHOR.json';es_bytes=es_path.read_bytes();es=json.loads(es_bytes)
    kernel_path=P/'GD_SHARED_CONSTRUCTION_AUTHOR_20261002.json';kb=kernel_path.read_bytes();kernel=json.loads(kb)
    packet_path=P/'FT_SOURCE_PACKET.json';pb=packet_path.read_bytes();packet=json.loads(pb)
    owned=[c for c in packet['contexts'] if c['unit_id']=='F83_P4']
    it=next(c for c in owned if c['edition']=='IT2a')
    native_lines=[(l['locus'],[g['ivtff_group_raw'] for g in l['groups']],[g['source_group_id'] for g in l['groups']]) for l in it['lines']]
    display_lines=[(l,s.split(),['P12_REPORT|'+l+'|G'+str(i+1).zfill(3) for i in range(len(s.split()))]) for l,s in P12_LINES]
    accounts={'native_IT_G':execute(native_lines,'IT2a_NATIVE', 'G'),'native_IT_I':execute(native_lines,'IT2a_NATIVE','I'),
              'report_P12_G':execute(display_lines,'P12_REPORT_DISPLAY','G'),'report_P12_I':execute(display_lines,'P12_REPORT_DISPLAY','I')}
    native_positions=[]
    for c in owned:
        for line in c['lines']:
            for g in line['groups']:
                raw=g['ivtff_group_raw'];native_positions.append({'source':g,'exact_license':raw in ROUTES or raw in NEW_ASSEMBLIES or raw in ['chedy','shedy','cheey','saiin','cheeky','solchedy'],
                    'semantic_status':'PRIMARY_FULL_ACCOUNT' if c['edition']=='IT2a' else 'ALTERNATE_EXACT_FORM_PROJECTION_ONLY_NOT_FULL_BINDING',
                    'uncertain_raw_unchanged':raw})
    forecasts={raw:{'route':ROUTES[raw],'computed_predicates':motion(r['stem'],r['extra_E'],r['mode'],'$w','$event','$patient','$full_phase','$host')}
               for raw,r in ROUTES.items()}
    dictionaries={v:{**es['parent32_models_unchanged'][v]['dictionary'],**es['prospective_EQ14_unchanged'],**es['new_exact_whole_values']} for v in ['G','I']}
    out={
     'status':'EXPLORATORY_COMPLETE_NATIVE_IT32_AND_REPORT33_C0_NOT_MEANING_CONFIRMED',
     'confirmed_words':0,'source_receipts':{'FT_SOURCE_PACKET_sha256':hashlib.sha256(pb).hexdigest(),'ES_author_sha256':hashlib.sha256(es_bytes).hexdigest(),'prior_kernel_sha256':hashlib.sha256(kb).hexdigest()},
     'owned_native_contexts':owned,'native_positions':native_positions,'accounts':accounts,
     'shared_motion_grade':{'map':{str(n):grade(n) for n in range(3)},'routes':ROUTES,'forecasts':forecasts,
       'PULSE_definition':'At least two positive-flow periods separated by a nonempty zero-flow interval within the entire assigned handling phase; endpoint pause or one flow period plus rest insufficient.',
       'CONTINUOUS_definition':'No stopping/zero-flow interval anywhere through the full assigned phase.',
       'unmarked_definition':'Actual FLOW only; no continuity or pulse assertion.',
       'QOKEY_not_QOKY':True,'LK_EY_licensed':False},
     'new_primitive_inventory':PRIMITIVES,'new_exact_assemblies':NEW_ASSEMBLIES,
     'preserved_parent_dictionaries':dictionaries,'parent_value_changes':[],
     'ES17_compatibility_obligation':{'source_kernel_sha256':hashlib.sha256(kb).hexdigest(),'full_17_source_and_bindings':kernel['source_preservation']['primary_IT_unit'],'full_17_reduction':kernel['full_17_written_order_reduction'],
      'preserved':'Existing world, material, phase, event, modifier, instrument and entry bindings retained verbatim; no meanings reauthored.',
      'grade_effect':'Old unmarked/continuous denotations unchanged. New pulse condition added only to previously unassigned zero-extra-E motion routes.'},
     'ET_preservation':{'lkedy':'actual instrumental PULSED FLOW','lkeedy':'actual instrumental FLOW pattern unmarked','lkeeedy':'actual instrumental CONTINUOUS FLOW','frames':'All consume their material/full-phase/host event; not LK EY.'},
     'paid_scope_and_binding_assumptions':[
       'Six manually declared clause spans; category transitions, ordered-series DAIN, THEN, HERE and FINAL frame delimit semantic phases. This is not an inferred universal parser or automatic line reset.',
       'One paid local description-time convention anchors each event-clause time at its phase onset; HERE state-description time lies in J5. The anchors are actual SAME_TIME atoms, not inherited universal syntax.',
       'First QOKEEDY has a forward material port resolved by written QOKEEY; QOKEDY in that same first clause predicates the same E1/full I1, adding actual pulse to unmarked FLOW.',
       'Case material L carried into subsequent explicit material mentions; repeated MOIST_PREPARATION alone does not prove identity. The coidentity policy is scoped to this candidate.',
       'CHEY introduces the case conduit C and then references it; AL introduces outlet O, OL resolves that exact outlet. First conduit serves RETURN_FLOW origin; no unmentioned source or vessel.',
       'QOKY introduces written intention P2; TOL adds its written goal O; L in QOKYLDDY resolves P2 by owner/root match; DDY adds a completed actual fulfillment E2.',
       'DAIN makes successive actual event mentions E3, E3b and E3c separate phases; identical SHCKHEDY produces same DISPENSE/DOSE operation with new witness ports. No hidden two-item source list or changed second-word meaning.',
       'State clause after HERE is interpreted at later J5, after the full pulsed phase I4; NOT MOVING at T5 does not deny the earlier actual pulse. This temporal clause convention is unconfirmed and explicitly charged.',
       'FINAL prefix opens E6; RETURN_FLOW and following generic FLOW refer to the same event. Native SAIRN/topic remainder resolves the forward patient to R, remainder of L.',
       'II and IRN are paid remainder-noun aliases in different spellings; no raw normalization. SA topicizes inherited LCHEDY in P12 but does not change frozen native SOLCHEDY=HERE.',
       'CASE quantities, finality and event recurrence are assumed; no treatment efficacy, filtration mechanism, heat, digging, source copied text, dose measurement or full arrival supplied.'
     ],
     'rival':{'id':'ONSET_MIDDLE','change':'Replace zero/one extra-E grades by onset/sustained-middle phases; retain continuous two-extra-E grade.',
      'paid_changes':['Two grade mappings','Corresponding ET LKEDY/LKEEDY values would change, so rival is not an unchanged-parent common extension.'],
      'difference':'QOKEDY no longer requires a positive-zero-positive history through its full phase; an uninterrupted onset could satisfy the rival.',
      'observed_discriminator':'No independently bound phase/history in present manuscript; distinct generated constraints are not meaning evidence.'},
     'hypothetical_sensitivity_only':{'pulsed_fixture':{'positive_periods':[[0,.3],[.7,1]],'zero_period': [.3,.7],'full_phase':[0,1]},
      'continuous_fixture':{'positive_periods':[[0,1]],'zero_periods':[],'full_phase':[0,1]},'claim':'Fixtures illustrate inequivalent obligations; no manuscript history or empirical efficacy.'},
     'source_access_actual':['Live route and existing contract/topic','Existing414 complete audit/root criticism and ET report','FT packet filtered F83_P4 before full native output','Full cached P12 file read incidentally displayed neighboring already-exposed text; only P4 used','Own previous shared kernel and existing ES source'],
     'new_target_access':False,'new_external_access':False,'decoder':False,
     'native_reader_limits':'97 native positions conserved: ZL33/IT32/RF32. Uncertain ZL/RF spellings stay unassigned. ZL/RF projections do not assert complete syntax; no imputed RF paragraph.',
     'new_formation_consequence':'QOKEDY actual pulse computed at native IT .25 G004 and .28 G004. QOKEEEDY actual continuous and QOKEY pulse-capable liquid generated prospectively, not claimed observed here.',
     'formal_analysis_qualification':'Local C0 raw-surface resegmentation, not established morphology: GDT605 can retain learned qokEdy/raw qokeedy, E can stand for raw ee; GDT689/516 distinguish DY from D_ADDR+Y. No canonical morpheme ladder or GDT787 additive-meaning proof is claimed.',
     'capability_qualification':'CAPABLE is retained as a primitive with an event-condition schema; admissible apparatus and conditions are not independently specified. Pulse-capable and continuous-capable materials may overlap. Nominal grade schemas are conditional expressions, not independently demonstrated different extensions or meaning evidence.',
     'full_connected_native_reading':'The flow-capable liquid flows through a conduit in pulses, pure, at an outlet. At the conduit, that moist preparation has an intended flow directed to the outlet, and the intention is fulfilled by a completed flow reaching that goal. In succession, the pure material flows and a dose, then another dose, is dispensed from it. Then, with care, the dispensable moist preparation flows in pulses at the outlet. Here, that same material is clear and stationary at the outlet. Finally its remainder flows back toward the conduit, with flow intended; no final fulfillment or completed return is asserted.',
     'terminal_mentions':['Final P6 is a descriptive intention status; no later FULFILLS predicate is asserted.','Dose objects are consumed as internal objects of the two actual dispensing events.','Pure/clear/stationary state descriptions are final truth conditions, not ignored instructions.'],
     'costs':{'new_primitive_or_frame_entries':len(PRIMITIVES),'new_exact_assembly_licenses':len(NEW_ASSEMBLIES),'motion_grade_cases':3,'distinct_motion_frames':['QOK nominal liquid','QOK finite material','LK instrumental material'],
       'parent_ES_semantic_decisions':16,'parent_ES_grammar_decisions':7,'extra_costs':'All scene, reference, phase, topicization, scalar aliases, single-conduit/outlet assumptions above. Counts overlap and are not code length or evidential score.'}}
    assert len(native_positions)==97
    assert len(accounts['native_IT_G']['rows'])==32 and len(accounts['report_P12_G']['rows'])==33
    assert all(v['status']=='COMPLETE_C0' for v in accounts.values())
    for raw,parts in NEW_ASSEMBLIES.items():assert ''.join(parts)==raw
    assert 'LIQUID' not in json.dumps(forecasts['qokedy']['computed_predicates'])
    assert 'LIQUID' not in json.dumps(forecasts['qokeedy']['computed_predicates'])
    out['generator_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    (P/'GD_MOTION_SHARED_GRADE_AUTHOR_20261002.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    print('native IT',accounts['native_IT_G']['status'],'32; report33; native97; QOKEDY shared pulse at2 sites')

if __name__=='__main__':run()
