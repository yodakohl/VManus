"""Finite countermodel to a proposed discriminator; no manuscript decoding."""
from itertools import product
from pathlib import Path
import hashlib
import json

BASE = Path('research_registry/proposals/production_origin_supply_20261003')
inputs = [BASE/'one_choice_course_scope.json', Path('research_registry/work_batches/ten_hours_20260915/TROTULA_IV15_V19_SOURCE_PACKET_20260920.md'), Path('experiments/yolo/gdt1018_transport_sufficient_instruction_audit/REPORT.md'), Path('experiments/yolo/gdt1153_prior_continuation_choice/REPORT.md')]
rows=[]
for stock_bits in product([False,True],repeat=2):
    stock={m for m,b in zip('AB',stock_bits) if b}
    global_traces=[]
    local_traces=[]
    for first in 'AB':
        prepared=stock|{first}
        # Global choice explicitly commits to the selected complete course.
        global_traces.append(first+first)
        # Local executor remembers no course label. Only actual material stock
        # determines which freshly chosen application can be executed.
        for second in 'AB':
            if second in prepared:
                local_traces.append(first+second)
    rows.append({'initially_prepared':''.join(sorted(stock)) or 'none','global_course':sorted(global_traces),'fresh_executable_choice':sorted(local_traces),'same_trace_set':set(global_traces)==set(local_traces)})
# Independently hand-derived table: matching material is newly prepared;
# a different material can be applied only if it was ready initially.
expected={'none':['AA','BB'],'A':['AA','BA','BB'],'B':['AA','AB','BB'],'AB':['AA','AB','BA','BB']}
for row in rows:
    assert row['fresh_executable_choice']==expected[row['initially_prepared']]
    assert row['global_course']==['AA','BB']
result={
 'status':'EMPTY_STOCK_TRACE_EQUIVALENCE_NO_SCOPE_IDENTIFICATION',
 'scope':'Exact finite semantic countermodel for IDEA912, not a historical or native observation.',
 'assumptions':['A/B abbreviate two invented material-specific preparation/application courses, not native signs or words.','Preparation makes its material available and leaves any other ready material available.','Application requires that material to have been prepared.','There are exactly two stages and no external preparation between them.','The global model commits to A or B once. The local model freshly chooses among executable applications, without a remembered course variable.','No historical initial stock or Voynich treatment subject is asserted.'],
 'cases':rows,
 'proof':'With empty initial stock, preparing X leaves only X available. Every executable second-stage choice is therefore X, yielding AA or BB in both models. The physical prepared-stock state encodes the consequence of the first action without an extra persistent grammatical choice. Any first-stage probability p gives identical full two-stage trace probabilities p and1-p under both models.',
 'contrast':'Both materials initially prepared gives four allowed local traces versus two global traces. This is a difference in permitted traces, not a claim that finite observed absence of mixed traces proves the global model.',
 'historical_limit':'The read Trotula packet attests nested alternatives but neither this two-course abstraction nor independent initial-stock or mixed-history prohibition. It cannot supply missing semantic premises.',
 'predecessors':'1018already distinguishes executable local options and instruction adequacy;1153refutes a different prior-occurrence selection rule. Both original decisions remain unchanged.',
 'decision':'Do not select a native912test from AA/BB persistence alone. A written scope/identity binding or independently justified opportunity for a mixed trace is needed; mere repetition or a new arbitrary connector value is insufficient.',
 'validation':'Four generated rows agree with a separately hand-derived truth table. Same author, no independent semantic validation.',
 'source_hashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
 'no_native_access':True,'confirmed_native_words_added':0
}
out=BASE/'COURSE912_AVAILABILITY_RESULT_20261007.json';out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':result['status'],'cases':rows},ensure_ascii=False))
