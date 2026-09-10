#!/usr/bin/env python3
"""Globally shared grammatical-role alternatives, fixed before model fitting."""
import itertools
PITCH_PARTITIONS=[(0,0),(0,1)]
VOICE_PARTITIONS=[(0,0,0),(0,0,1),(0,1,0),(0,1,1),(0,1,2)]
CASES=[{'pitch':list(p),'voice':list(v)} for p,v in itertools.product(PITCH_PARTITIONS,VOICE_PARTITIONS)]

def compile_case(source,case):
    graph=source['source_graph'];types={o['id']:o['cantus_type'] for o in graph['origins']}
    records=[];forms={}
    def morph(family,value,role):
        block=case['pitch' if family=='PITCH' else 'voice'][role]
        roleclass=family+':'+str(block)
        key=roleclass+':'+value
        forms[key]={'family':family,'root':value,'roleclass':roleclass}
        return key
    def plain(kind,value=None):
        key=kind+(':'+value if value is not None else '')
        forms[key]={'family':None,'root':None,'roleclass':None}
        return key
    for p in graph['pitches']:
        pitch=p['id'];head=morph('PITCH',pitch,0);seq=[head]
        def origin(h):return plain('SELF') if h==pitch else morph('PITCH',h,1)
        for m in p['memberships']:
            seq += [morph('VOICE',m['voice'],0),plain('CANTUS',types[m['origin']]),origin(m['origin'])]
        for m in graph['mutations']:
            if m['pitch']!=pitch:continue
            seq += [morph('VOICE',m['from_voice'],1),morph('VOICE',m['to_voice'],2),
                    plain('DIRECTION',m['direction']),plain('CANTUS',types[m['to_origin']]),origin(m['to_origin'])]
        if p['zero_explicit']:seq += [plain('ZERO')]
        records.append({'id':pitch,'head_atom':head,'sequence':seq})
    return {'records':records,'atoms':sorted(forms),'forms':forms,'role_partition':case}
