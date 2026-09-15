#!/usr/bin/env python3
"""Source-only Harley 978 f11v inventory and explicitly conditional executions.
No Voynich data, target format, vocabulary, or inference is read or constructed.
Run from any directory; writes the adjacent ROTA_SOURCE_EVENTS.json.
"""
from pathlib import Path
from fractions import Fraction
from itertools import combinations
import hashlib
import json
import math

STAVES = [
 ('M1','F4 E4 D4 E4 F4 F4 E4 D4 C4 A3 A3 Bb3 G3 A3 R F3 A3 G3 Bb3 A3 A3', 'L b L b L b t b b L b L b L R L b L b L b'),
 ('M2','G3 F3 A3 C4 D4 D4 C4 R F4 D4 F4 R C4 A3 Bb3 G3 A3 C4', 'L b L b L b L R L L L R L b L b L b'),
 ('M3','Bb3 A3 F3 A3 G3 E3 F3 R A3 A3 G3 Bb3 C4 C4 D4 E4', 'L b L b L b L R L b L b L b L b'),
 ('M4','F4 E4 D4 E4 F4 R C4 D4 C4 Bb3 A3 F3 A3 Bb3 G3 A3 Bb3 C4 A3', 'L b L b L R L L L l l L b L b L u b L'),
 ('M5','C4 G3 E3 F3 R', 'b L b L R'),
 ('P1','F3 G3 F3 G3 A3 C4 Bb3 C4 R', 'L L L l l L L L R'),
 ('P2','C4 Bb3 C4 R F3 G3 F3 G3 A3', 'L L L R L L L l l'),
]
# Editorial normalization only: breve = 1, perfect longa = 3.
# These 24 groups are modern time groupings, NOT source barlines/paragraphs.
GROUPS = [
 'F4:2 E4:1 D4:2 E4:1', 'F4:2 F4:1 E4:1 D4:1 C4:1',
 'A3:2 A3:1 Bb3:2 G3:1', 'A3:3 R:3',
 'F3:2 A3:1 G3:2 Bb3:1', 'A3:2 A3:1 G3:2 F3:1',
 'A3:2 C4:1 D4:2 D4:1', 'C4:3 R:3', 'F4:3 D4:3', 'F4:3 R:3',
 'C4:2 A3:1 Bb3:2 G3:1', 'A3:2 C4:1 Bb3:2 A3:1',
 'F3:2 A3:1 G3:2 E3:1', 'F3:3 R:3', 'A3:2 A3:1 G3:2 Bb3:1',
 'C4:2 C4:1 D4:2 E4:1', 'F4:2 E4:1 D4:2 E4:1', 'F4:3 R:3',
 'C4:3 D4:3', 'C4:3 Bb3:2 A3:1', 'F3:2 A3:1 Bb3:2 G3:1',
 'A3:3 Bb3:2 C4:1', 'A3:2 C4:1 G3:2 E3:1', 'F3:3 R:3',
]
SHAPES = {
 'L':'filled approximately square head with descending stem',
 'b':'filled untailed head, lozenge/oblique form; not a modern duration symbol',
 't':'lozenge at start of descending ternary group, with descending oblique tractus',
 'l':'member of joined two-note group; individual duration not read directly from head',
 'u':'approximately horizontal square head without a clear stem; near erased area',
 'R':'upright pause stroke, not a modern barline',
}
DIATONIC = {'C':0,'D':1,'E':2,'F':3,'G':4,'A':5,'B':6}
CHROMATIC = {'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11}

def pitch_info(p):
    if p == 'R': return None
    letter, octv = p[0], int(p[-1])
    flat = 'b' in p
    return {'diatonic_steps_above_c_reference': DIATONIC[letter]+7*(octv-4),
            'conventional_pitch':p, 'midi_under_c4_octave_convention':12*(octv+1)+CHROMATIC[letter]-flat}

def digest(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def events():
    out=[]; counters={}; rests={}
    for stave, pitches, shapes in STAVES:
        part='M' if stave.startswith('M') else stave
        assert len(pitches.split())==len(shapes.split())
        local_n=0
        for ordinal,(p,shape) in enumerate(zip(pitches.split(),shapes.split()),1):
            if p=='R':
                rests[part]=rests.get(part,0)+1
                eid=f'{part}R{rests[part]:02d}'; n=None
            else:
                counters[part]=counters.get(part,0)+1; n=counters[part]; local_n+=1
                eid=f'{part}N{n:03d}'
            e={'id':eid,'part':part,'physical_stave':stave,
               'written_event_ordinal_on_stave':ordinal,
               'written_note_ordinal_on_stave':local_n if n else None,
               'note_ordinal_in_part':n,'kind':'pause' if p=='R' else 'note',
               'visible_mark_class':shape,'visible_mark_description':SHAPES[shape],
               'pitch_reading':pitch_info(p)}
            if part=='M' and n in (7,8,9): e['joined_group']='M_LIGATURE_TERNARY_1'
            if part=='M' and n in (60,61): e['joined_group']='M_LIGATURE_BINARY_1'
            if part=='P1' and n in (4,5): e['joined_group']='P1_LIGATURE_BINARY_1'
            if part=='P2' and n in (7,8): e['joined_group']='P2_LIGATURE_BINARY_1'
            if eid=='MN002':e['native_layer_note']='Current pitch E; Rockstro reports erased prior F. Prior reading not silently substituted.'
            if eid in ('MN067','MN068'):
                e['native_layer_note']='Local shape/edition attribution unresolved: current reading locates clear stemless square at MN067; Hurry p28 says penultimate note of stave4, which is MN068. Preserve both statements.'
            out.append(e)
    assert counters=={'M':73,'P1':8,'P2':8} and rests=={'M':6,'P1':1,'P2':1}
    return out

EVENTS=events()
PARTS={p:[e for e in EVENTS if e['part']==p] for p in ('M','P1','P2')}
base_tokens=[t.split(':') for g in GROUPS for t in g.split()]
assert [x[0] for x in base_tokens]==[e['pitch_reading']['conventional_pitch'] if e['kind']=='note' else 'R' for e in PARTS['M']]
BASE={e['id']:int(x[1]) for e,x in zip(PARTS['M'],base_tokens)}
BASE.update({e['id']:d for e,d in zip(PARTS['P1'],[3,3,3,2,1,3,3,3,3])})
BASE.update({e['id']:d for e,d in zip(PARTS['P2'],[3,3,3,3,3,3,3,2,1])})
assert len(BASE)==97

RULES=[
 {'id':'R01','owner':'black ruled instruction box, opening clause','latin_normalized':'Hanc rotam cantare possunt quatuor socii.','meaning':'Four companions may sing the rota.','content':'selected_upper_voice_count_4','qualification':'The clause says four can sing; it does not prohibit human doubling or prove an absolute maximum.'},
 {'id':'R02','owner':'same box, second clause','latin_normalized':'A paucioribus autem quam a tribus vel saltem duobus non debet dici, preter eos qui dicunt pedem.','meaning':'It should not be sung by fewer than three, or at least two, apart from those who sing the pes.','content':'upper_voices_2_3_4_plus_pes','collation':'Meeus prints aut where native expansion is read vel; operational alternative unchanged.'},
 {'id':'R03','owner':'same box, Canitur autem sic / Tacentibus clause','latin_normalized':'Canitur autem sic. Tacentibus ceteris, unus inchoat cum hiis qui tenent pedem.','meaning':'With the others silent, one begins together with those who sustain the pes.','content':'rota_voice_1_and_both_pes_start_together','collation':'Independent audit expands Cantatur; producer/Meeus Canitur. No operative distinction claimed.'},
 {'id':'R04','owner':'same box, Et cum venerit clause; red cross in main stave1','latin_normalized':'Et cum venerit ad primam notam post crucem, inchoat alius, et sic de ceteris.','meaning':'When that singer reaches the first note after the cross, another begins; likewise the others.','content':'successive_upper_voice_delay_equals_time_to_MN010','marker':'X01'},
 {'id':'R05','owner':'same box, final Singuli clause','latin_normalized':'Singuli vero repausent ad pausaciones scriptas et non alibi, spacio unius longe note.','meaning':'Each pauses at the written pauses and nowhere else, for one long note.','content':'written_pauses_only_duration_one_longa','scope_qualification':'Immediate boxed context is rota singers; extension of its numeric realization to pes pauses is an explicit shared-scope assumption.','duration_limit':'This says longa, not an independently specified modern beat count.'},
 {'id':'R06','owner':'red instruction immediately right/below upper pes','latin_normalized':'Hoc repetat unus quociens opus est, faciens pausacionem in fine.','meaning':'One repeats this as often as needed, making a pause at the end.','content':'P1_repeats_with_ending_pause','collation':'Independent audit and Meeus print repetit; initial producer expansion repetat is retained as a provisional alternative; repeat behavior unchanged.'},
 {'id':'R07','owner':'red instruction to right/below lower pes','latin_normalized':'Hoc dicat alius pausans in medio et non in fine, set immediate repetens principium.','meaning':'The other sings this, pausing in the middle and not at the end, but immediately repeating the beginning.','content':'P2_pause_after_third_note_no_end_pause_immediate_repeat','collation':'Independent audit and Meeus print dicit; initial producer expansion dicat is retained as a provisional alternative; non is retained.'},
]

# Freeze these documentary branches and three rivals before evaluation.
# No claim that any is a complete authoritative editorial reading of the native page.
BRANCHES=[
 {'id':'C0_local_current_conditional','changes':{},'status':'conditional composite, NOT a certified complete historical edition',
  'conditions':['Current native pitches and head classification.', 'Ternary group 1+1+1 following Hurry p31.', 'MN067 is the stemless longa, duration2; MN066=3 and MN068=1.', 'Main written pauses are perfect longae3; extending the boxed longa prescription to both pes pauses is a declared shared-scope assumption.', 'Binary groups interpreted2+1, following the owned modern scores.']},
 {'id':'C1_rockstro_ternary_conditional','changes':{'MN007':'3/2','MN008':'1/2'},'status':'C0 sensitivity using Rockstro explicit ternary rhythm; not full Grove score collation'},
 {'id':'C2_hurry_pes_prose_countercase','changes':{'P1N004':'1','P2N007':'1'},'status':'C0 sensitivity preserving Hurry prose both-minims claim against owned score; not an endorsed performance'},
 {'id':'C3_ordinal_missing_stem_sensitivity','changes':{'MN066':'2','MN067':'1','MN068':'3'},'status':'C0 sensitivity to Hurry penultimate-note ordinal: stemless longa assigned to MN068; other lengths from his perfect/imperfect rule. This is a constructed documentary alternative, not an attested complete edition.'},
]
RIVALS=[
 {'id':'entry_shift_plus_one_breve','mutation':'Upper entries at successive multiples of d+1, instead of d; written part events unchanged.'},
 {'id':'upper_pes_rest_phase_swap','mutation':'Swap P1 ending pause with immediately preceding note as duration-carrying events; all notes, durations and pause counts retained.'},
 {'id':'reverse_main_event_cycle','mutation':'Reverse the complete main event order, including pauses, retaining each pitch-duration pair; hold entry delay d fixed.'},
]

def durations(branch):
    d={k:Fraction(v) for k,v in BASE.items()}
    for k,v in branch['changes'].items(): d[k]=Fraction(v)
    return d

def expand(part,ds,ids=None):
    byid={e['id']:e for e in PARTS[part]}
    ids=ids or list(byid)
    stream=[]
    for i in ids:
        e=byid[i]; ticks=ds[i]*2
        assert ticks.denominator==1 and ticks>0
        pitch=e['pitch_reading']['midi_under_c4_octave_convention'] if e['kind']=='note' else None
        stream.extend([pitch]*int(ticks))
    return stream

def performance(streams,k,delay,t0,n):
    voices=[]
    for v in range(k):
        voices.append([streams['M'][(t-v*delay)%len(streams['M'])] if t>=v*delay else None for t in range(t0,t0+n)])
    for p in ('P1','P2'): voices.append([streams[p][t%len(streams[p])] for t in range(t0,t0+n)])
    return list(map(list,zip(*voices)))

def difference(a,b):
    pitch_cells=rest_cells=interval_cells=0; first=None
    for ti,(x,y) in enumerate(zip(a,b)):
        for vi,(p,q) in enumerate(zip(x,y)):
            if p!=q:
                pitch_cells+=1
                if first is None:first={'sample_tick':ti,'voice_index':vi,'base_midi_or_rest':p,'rival_midi_or_rest':q}
            rest_cells+=(p is None)!=(q is None)
        for i,j in combinations(range(len(x)),2):
            u=None if x[i] is None or x[j] is None else x[j]-x[i]
            v=None if y[i] is None or y[j] is None else y[j]-y[i]
            interval_cells+=(u!=v)
    return {'different_pitch_or_rest_cells':pitch_cells,'different_rest_mask_cells':rest_cells,'different_signed_interval_or_undefined_cells':interval_cells,'first_difference':first,'rival_output_sha256':digest(b)}

def execute(branch):
    ds=durations(branch); streams={p:expand(p,ds) for p in PARTS}
    entry=sum(ds[e['id']] for e in PARTS['M'][:9]); assert entry==12
    dt=int(entry*2); period=math.lcm(*(len(s) for s in streams.values()))
    results=[]
    for k in (2,3,4):
        # Includes no pre-entry silence: complete common steady-state period.
        # Warm-up also covers latest entry for the +1 rival.
        t0=(k-1)*(dt+2)
        base=performance(streams,k,dt,t0,period)
        cases=[]
        for rival in RIVALS:
            ss=dict(streams); delay=dt
            if rival['id']=='entry_shift_plus_one_breve':delay+=2
            elif rival['id']=='upper_pes_rest_phase_swap':
                ids=[e['id'] for e in PARTS['P1']];ids[-2:]=ids[-2:][::-1];ss['P1']=expand('P1',ds,ids)
            else:ss['M']=expand('M',ds,[e['id'] for e in PARTS['M']][::-1])
            rr=performance(ss,k,delay,t0,period)
            cases.append({'rival':rival['id'],**difference(base,rr)})
        results.append({'upper_voices':k,'pes_voices':2,'start_tick':t0,'period_ticks':period,'tick_unit_breve':'1/2','source_branch_output_sha256':digest(base),'rivals':cases})
    p1,p2=streams['P1'],streams['P2']
    rotations=[i for i in range(len(p1)) if p1[i:]+p1[:i]==p2]
    return {'branch':branch['id'],'written_part_lengths_breves':{p:str(sum(ds[e['id']] for e in PARTS[p])) for p in PARTS},'entry_delay_breves':str(entry),'pes2_equals_pes1_rotation_ticks':rotations,'execution':results}

if __name__=='__main__':
    out={
      'schema':'source-event-inventory/1','source':'British Library Harley MS978 f11v','date':'2026-09-15',
      'scope':'Complete current written note/rest sequence and operative performance rules; no complete lyric transcription, no Voynich reading or target format.',
      'status':'COMPLETE_PITCH_AND_MARK_INVENTORY_WITH_UNRESOLVED_EDITORIAL_DURATION_ATTRIBUTION; conditional execution only',
      'sources':[
        {'id':'BL_NATIVE','url':'https://live.staticflickr.com/2826/12458897473_6530558074_o.jpg','owner_metadata_url':'https://www.flickr.com/photos/britishlibrary/12458897473','sha256':'f0dca799f0e46f419b0918b7be6e4443e8cda74ea53ea5a1cf97246f92bb7668','bytes':981730,'role':'Native full folio actually inspected, including all seven staves; crops used only as viewing aids.'},
        {'id':'HURRY1914','url':'https://archive.org/download/sumerisicumenin00hurruoft/sumerisicumenin00hurruoft.pdf','sha256':'b6064c7ce7b72c740e8a0bfdc2ea7d6c8c3d22577fcce95dac0548d8afc1070a','bytes':3197963,'pages_read':'printed28–35; modern score pp32–35 actually viewed','role':'Public-domain scholarly edition with acknowledged liberties and internal prose/score discrepancy.'},
        {'id':'ROCKSTRO_GROVE','url':'https://en.wikisource.org/w/index.php?title=A_Dictionary_of_Music_and_Musicians/Sumer_is_icumen_in&oldid=12180580','sha256':None,'role':'Named original manuscript study, explicit duration conventions and erasure report. Web prose read; score images NOT independently collated.'},
        {'id':'MEEUS','url':'http://nicolas.meeus.free.fr/MusiqueAncienne/3Sumer.pdf','sha256':'b0c78c8ff0c2b030ae0ff1c0334bc6a61d19bdac71441e0128c18999f9c0b1d5','bytes':591529,'role':'Named scholarly teaching edition following Davison–Apel no42. Complete p2 score/rules actually viewed. Different corrected-layer pitches; not substituted for native inventory.'}
      ],
      'pitch_conventions':{'native_reference':'C clef and B rotundum on each stave','absolute_octave':'C4 chosen as an explicit modern reference, not a source numeral; global transposition remains equivalent for intervals','staff_line_count':'Main staves six; upper pes seven including extra upper ruling; lower pes six. Upper-pes correction was prompted by independent reviewer message, then checked natively.','c_reference_line':'third red ruling from top, with the extra upper-pes ruling counted; named pitches derive from diatonic spacing and B-flat sign','visual_limit':'Irregular head tilt and erasure/show-through do not license extra notes or silent restoration of earlier layers.'},
      'written_counts':{'main_notes':73,'main_pauses':6,'upper_pes_notes':8,'upper_pes_pauses':1,'lower_pes_notes':8,'lower_pes_pauses':1,'all_written_events':97},
      'independent_comparison':{'own_event_matrix_precomparison_sha256':'2ff05f993c8ffcba901184bf811557ad604f4e497f785a5d80fedce3b37163fd','independent_json_sha256':'c943edac727035ff20e52785389f195ded3d6d4419189cf7c058dfd935d423a8','independent_md_sha256':'77a11f3833d49f6b6ad0f872f5a5856786faddaaf9ce846d04f89748d8fc0c86','read_after_own_matrix_written_utc':'2026-09-15 12:49:33 UTC','agreement':'All 18 pes note/pause event positions; eight notes each; rising paired ligatures; current pitch steps; operative rule semantics. Neither independent audit nor collation certifies every numeric duration.','corrections_and_qualifications':['Upper pes seven-ruling correction was prompted by reviewer message before own matrix seal and checked natively; not independent discovery.','Producer initially classified upper stray cluster as noncurrent; independent audit leaves exact ink status unresolved. Preserve unresolved status; no ninth note inserted.','Producer treats upper end stroke as pause; independent audit qualifies adjacent box-edge separation while agreeing end pause is explicitly required by red prose.','Cantatur/Canitur, repetit/repetat, dicit/dicat are retained expansion alternatives, not semantic repairs.']},
      'pes_full_event_relation':{'A':['P1N001','P1N002','P1N003','P1N004','P1N005'],'B':['P1N006','P1N007','P1N008','P1R01'],'upper':'AB','lower':'BA','native_scope':'Pitch positions, classified square/stem forms, corresponding rising binary ligature, and required pause; isolated irregular ink and end-stroke classification caveats retained.','duration_theorem':'If the same rotation-equivariant interpretation assigns duration to corresponding notational events in their circular contexts, P2 is exactly a timed rotation of P1. This does not require A and B to have equal lengths.','numeric_scope':'C0/C1/C3: A=12,B=12; C2: A=11,B=12. None is independently certified as the complete historical rhythm.'},
      'markers':[{'id':'X01','kind':'red entry cross','owner':'main physical stave1','after':'MN009','before':'MN010','meaning_owner':'R04','not_a_sounding_event':True},{'id':'PES_LABEL','kind':'red pes label and enclosing mark','owner':'the two lower notated parts','not_a_sounding_event':True}],
      'events':EVENTS,'rules':RULES,
      'baseline_conditional_duration_breves':{k:str(v) for k,v in BASE.items()},
      'documentary_duration_branches':BRANCHES,
      'branch_policy':'C0 is a declared composite local reading, not proof that all duration ambiguity is solved. C1–C3 change one documented uncertainty at a time; they are not asserted exhaustive and their Cartesian product is not claimed historically licensed. No branch was chosen for target convenience.',
      'preregistered_source_only_rivals':RIVALS,
      'executions':[execute(b) for b in BRANCHES],
      'initialization_check_status':'NOT_SEPARATELY_COMPARED: output receipts cover complete steady periods after all baseline and rival entries; tick0-to-warmup transient is not part of the reported comparisons.',
      'claim_ceiling':['Exact executions demonstrate temporal consequences conditional on explicit source readings.','A rival differs from a known score; this is not a calibrated null or proof that unknown text is music.','No universal consonance rule, optimality claim, key signature semantics beyond pitch interpretation, or fit score is imposed.','Main repetition is the rota interpretation; total performance duration and stopping procedure are not fixed by the written instructions.','English and Latin lyrics and syllable alignment are outside the declared music-content subset.','The MN067/MN068 discrepancy must be settled or retained as a finite explicit uncertainty before a complete certified temporal contract is claimed.'],
      'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    path=Path(__file__).with_name('ROTA_SOURCE_EVENTS.json')
    path.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({'written_counts':out['written_counts'],'event_matrix_sha256':digest(EVENTS),'branches':[{'id':x['branch'],'lengths':x['written_part_lengths_breves'],'pes_rotation_ticks':x['pes2_equals_pes1_rotation_ticks']} for x in out['executions']],'json_sha256':hashlib.sha256(path.read_bytes()).hexdigest()},indent=2))
