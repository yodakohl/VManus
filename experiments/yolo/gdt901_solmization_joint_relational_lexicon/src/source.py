#!/usr/bin/env python3
"""Complete fixed operational projection, independent of manuscript data."""
import json
from pathlib import Path

def compile_graph(graph):
    types={o['id']:o['cantus_type'] for o in graph['origins']}
    records=[]
    for row in graph['pitches']:
        pitch=row['id']
        origin=lambda h:'SELF' if h==pitch else 'PITCH:'+h
        sequence=['PITCH:'+pitch]
        for m in row['memberships']:
            sequence+=['VOICE:'+m['voice'],'CANTUS:'+types[m['origin']],origin(m['origin'])]
        mutations=[m for m in graph['mutations'] if m['pitch']==pitch]
        assert len(mutations)==row['mutation_count']
        for m in mutations:
            sequence+=['VOICE:'+m['from_voice'],'VOICE:'+m['to_voice'],
                       'DIRECTION:'+m['direction'],'CANTUS:'+types[m['to_origin']],origin(m['to_origin'])]
        if row['zero_explicit']:
            assert not mutations
            sequence+=['ZERO']
        records.append({'id':pitch,'head_atom':'PITCH:'+pitch,'sequence':sequence})
    return records

def load(path):
    packet=json.loads(Path(path).read_text())
    assert packet['schema']=='GDT901_FROZEN_OPERATIONAL_SOURCE_V1'
    assert len(packet['records'])==22
    assert compile_graph(packet['source_graph'])==packet['records']
    assert sorted(set(a for r in packet['records'] for a in r['sequence']))==packet['atoms']
    assert len(packet['atoms'])==35
    return packet
