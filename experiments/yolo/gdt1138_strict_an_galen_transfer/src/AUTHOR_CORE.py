"""Finite strict partial C account. No target/source-body imports or ID dispatch."""
from dataclasses import dataclass, asdict
from pathlib import Path
import json

SPEC = json.loads(Path(__file__).with_suffix('.json').read_text())
LEXICON = {e['form']: e for e in SPEC['literal_entries']}

@dataclass(frozen=True)
class DescriptionRecord:
    id: str
    content_json: str
    dependencies: tuple = ()
    completed: bool = True
    @property
    def content(self):
        return json.loads(self.content_json)

@dataclass(frozen=True)
class BoundDescriptionRef:
    id: str
    record: DescriptionRecord


def record(identifier, content, dependencies=(), completed=True):
    if not content:
        raise ValueError('NonemptyDescriptionRecord required')
    return DescriptionRecord(identifier, json.dumps(content, sort_keys=True), tuple(dependencies), completed)


def aN(current, buffer):
    if current is None or not current.content:
        raise ValueError('aN requires NonemptyDescriptionRecord')
    ref = BoundDescriptionRef('ref:' + str(len(buffer)+1) + ':' + current.id, current)
    buffer.append(ref)
    return ref


def d(completed, records):
    if completed is None or not completed.completed:
        raise ValueError('d requires CompletedDescriptionRecord')
    closure = []
    visited = set()
    def collect(item):
        if item.id in visited:
            return
        visited.add(item.id)
        for dep in item.dependencies:
            collect(records[dep])
        closure.append({'id': item.id, 'content': item.content})
    collect(completed)
    # d retains the exact contribution plus its full dependency content.
    return record('d:' + completed.id,
                  {'contribution': completed.content, 'dependency_closure': closure},
                  completed.dependencies)


def project(ref, field):
    if ref is None:
        return {'status':'MISSING_REFERENCE', 'field':field}
    content = ref.record.content
    if field not in content:
        return {'status':'MISSING_TYPED_FIELD', 'field':field,
                'actual_type':'BoundDescriptionRef', 'retained_content':content}
    return {'status':'PROJECTED', 'field':field, 'value':content[field]}


def consume_water(operator, ref, context=None):
    projection = project(ref, 'WATER')
    if projection['status'] != 'PROJECTED':
        return {'status':'TYPED_BARRIER', 'operator':operator,
                'required_noun_type':'WATER', 'projection':projection,
                'required_context_type':'ordered-water-context' if operator=='FIRST' else 'water-reference',
                'context_supplied': context is not None,
                'later_predicate':None}
    # Even an externally supplied field cannot synthesize missing typed context.
    required = 'ordered-water-context' if operator=='FIRST' else 'water-reference'
    if not isinstance(context, dict) or context.get('type') != required:
        return {'status':'TYPED_BARRIER','operator':operator,'required_context_type':required,
                'projection':projection,'later_predicate':None}
    return {'status':'UNLICENSED_CONTEXT_VALUE','operator':operator,'later_predicate':None}


def replay(groups, interventions=None):
    """Interventions: index-keyed delete_donor or replace_payload at actual aN return."""
    interventions = interventions or {}
    records, refs, trace, water_consumers = {}, [], [], []
    focus = completed = norm = None
    values = []
    for i, group in enumerate(groups):
        form = group if isinstance(group, str) else group['form']
        identifier = 'written:' + str(i + 1)  # provenance, never semantic lookup
        entry = LEXICON.get(form)
        if entry:
            value = entry['value']
            current = record(identifier, {'kind':'lexical-description','form':form,
                                         'value':value,'type':entry['type'],'denotation':entry['denotation']})
            records[identifier] = current
            focus = completed = current
            if value == 'FULLY' and values[-2:] == ['BOIL', 'NOT']:
                dependencies = tuple('written:' + str(j) for j in range(i-1, i+2))
                current = record('construct:' + str(i+1),
                                 {'kind':'prohibition','predicate':{'FULLY':'BOIL'},'mode':'prohibited'},dependencies)
                records[current.id] = current
                focus = completed = norm = current
            elif value == 'BOIL' and values[-1:] == ['FULLY']:
                deps = ['written:' + str(i), identifier]
                content = {'kind':'predicate-description','predicate':{'FULLY':'BOIL'},'mode':'unsaturated'}
                if norm is not None:
                    deps.append(norm.id)
                    content = {'kind':'quoted-reprise','predicate':{'FULLY':'BOIL'},'mode':'quoted',
                               'norm_content':norm.content}
                current = record('construct:' + str(i+1), content, deps)
                records[current.id] = current
                focus = completed = current
            trace.append({'position':i+1,'form':form,'literal_entry':entry,'record':asdict(current),
                          'status':'LITERAL_DESCRIPTION_ONLY','unfilled_signature':entry['type']})
            if value in ('FIRST','OTHER'):
                water_consumers.append({'position':i+1,'operator':value,'ref':None})
            values.append(value)
        elif form in ('aiin','daiin'):
            argument = d(completed, records) if form=='daiin' and completed is not None else focus
            if form == 'daiin':
                focus = argument
            intervention = interventions.get(str(i+1), interventions.get(i+1, {}))
            if intervention.get('delete_donor'):
                argument = None
            if 'replace_payload' in intervention and argument:
                argument = record(argument.id, intervention['replace_payload'], argument.dependencies)
            try:
                ref = aN(argument, refs)
                status, returned = 'BOUND_REFERENCE', asdict(ref)
            except ValueError as error:
                ref, status, returned = None, 'MISSING_ARGUMENT', {'error':str(error)}
            trace.append({'position':i+1,'form':form,'operations':['d','aN'] if form=='daiin' else ['aN'],
                          'status':status,'actual_return':returned,
                          'licensed_later_meaningful_consumer':False})
            for consumer in water_consumers:
                expected_distance = 2 if consumer['operator']=='FIRST' else 1
                if consumer['position'] + expected_distance == i+1:
                    consumer['ref'] = ref
            values.append('aN' if form=='aiin' else 'd+aN')
        else:
            trace.append({'position':i+1,'form':form,'status':'UNKNOWN_WHOLE_RESIDUAL'})
            values.append('UNKNOWN')
    results = [{'position':c['position'], **consume_water(c['operator'],c['ref'])} for c in water_consumers]
    return {'status':'PARTIAL_NO_CAPACITY','trace':trace,'water_applications':results,
            'retained_references':[asdict(ref) for ref in refs],
            'quoted_reference_consumer':'NO_LICENSED_LATER_CONSUMER_OR_EXPLANATORY_RULE',
            'meaningful_content_sensitivity':'NOT_ESTABLISHED',
            'complete_connected_reading':False}
