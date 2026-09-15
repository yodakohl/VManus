# Independent 23-group root-trace capacity receipt

2026-09-15. **PASS: the fixed IT2a intake has exactly three eligible complete
23-group paragraphs, on physical leaves 24, 103 and 114.** ZL3b has one eligible
frame on leaf 114; RF1b has no complete boundary-marked paragraph. This establishes
the declared format capacity for IT2a only. No numeric reading, code, shared key,
arithmetic fit or semantic success was tested.

The result contains **14 candidate rows**, six ZL3b and eight IT2a, rather than
13. Their complete metadata and exclusion reasons reconcile independently.
Alternate readings are versions of one manuscript; the shared f114v identifier
does not add a fourth independent record.

## Independent reconstruction and ownership

I read the current route, the prospective [decision](ROOT_TRACE_DECISION.md),
the capacity script/result, the unchanged GDT928 loader and the prior independent
latitude reconstruction. I then reconstructed frames directly from all six
already guarded GDT915 caches without importing either the GDT928 loader or
the new capacity script.

The independent parser locates each paragraph start and its first closing
marker before another start. It requires consecutive locus numbers, preserving
every group within the resulting frame. Line eligibility separately requires
at least two groups, literal `[a-z]+` throughout, consecutive source-group
indices and definite internal separators. No candidate word or substring was
displayed. Numeric hypotheses were not evaluated.

All eight GDT928 preregistration bindings matched. Every cache line belongs to
the inherited 179-selector allowlist; f84-prefixed and f116v selectors are
excluded. There are no duplicate prose-line identities across the two cache
phases. The independent result matches every reported complete/literal length
histogram bin, every denominator, every candidate row in its original order,
all ineligible loci, physical leaves and the three-leaf capacity flag.

“Complete” here is ownership under the inherited transcription's start/end
markers and gap rule. It is not an independent identification of authorial
sentences, calculations or paragraph meanings.

| Edition | Prose lines | Complete frames | Eligible frames, all lengths | Gapped frames | Complete 23-group frames | Eligible 23-group frames | Eligible leaves |
|---|---:|---:|---:|---:|---:|---:|---|
| ZL3b | 3,768 | 659 | 31 | 6 | 6 | 1 | 114 |
| IT2a | 3,767 | 690 | 523 | 7 | 8 | 3 | 24, 103, 114 |
| RF1b | 3,768 | 0 | 0 | 0 | 0 | 0 | none |

The inherited eligible-line counts within complete frames also match:
1,430 for ZL3b and 3,129 for IT2a. RF's absent denominator keys retain the
parent's sparse Counter convention rather than supplying new paragraph evidence.

## All candidate metadata

Every row below contains exactly 23 groups. N = NONLITERAL_GROUP;
S = UNDEFINITE_SEAM; F = TOO_FEW_GROUPS. No candidate has a
NONCONSECUTIVE_GROUP_INDEX failure. Group sequences count all lines in each
complete frame, including an ineligible line.

| Edition | Complete frame ID | Groups by line | Eligible | Failing loci and reason |
|---|---|---|---|---|
| ZL3b | f114r\|f114r.1-f114r.3 | 9,13,1 | no | f114r.1 N; f114r.2 S; f114r.3 F |
| ZL3b | f114v\|f114v.23-f114v.25 | 8,9,6 | yes | none |
| ZL3b | f17r\|f17r.4-f17r.6 | 9,9,5 | no | f17r.4 N+S; f17r.5 S; f17r.6 S |
| ZL3b | f44r\|f44r.5-f44r.7 | 8,9,6 | no | f44r.6 N+S; f44r.7 N |
| ZL3b | f45r\|f45r.5-f45r.7 | 10,8,5 | no | f45r.5 S |
| ZL3b | f49r\|f49r.1-f49r.3 | 9,8,6 | no | f49r.1 N+S; f49r.2 N; f49r.3 S |
| IT2a | f103v\|f103v.12-f103v.13 | 12,11 | yes | none |
| IT2a | f114v\|f114v.23-f114v.25 | 8,9,6 | yes | none |
| IT2a | f22r\|f22r.7-f22r.9 | 9,9,5 | no | f22r.7 S; f22r.8 S |
| IT2a | f24v\|f24v.6-f24v.11 | 3,4,4,4,4,4 | yes | none |
| IT2a | f37r\|f37r.4-f37r.7 | 7,5,6,5 | no | f37r.4 S; f37r.6 S |
| IT2a | f37v\|f37v.8-f37v.13 | 4,5,5,4,4,1 | no | f37v.13 F |
| IT2a | f3r\|f3r.15-f3r.17 | 8,9,6 | no | f3r.15 S; f3r.16 S |
| IT2a | f49r\|f49r.1-f49r.3 | 8,8,7 | no | f49r.3 S |

The one-group final line of IT2a f37v is an eligibility failure under the
unchanged parent rule. Calling every excluded frame “nonliteral” would conceal
that distinction. Ineligible 23-group frames remain outside the exact channel,
rather than becoming arithmetic contradictions. RF's missing complete paragraph
boundaries likewise establish no content refutation.

## Timing correction and hashes

The decision contains an incorrect manually stated selection minute, 11:59 UTC,
although the result records execution at 11:55:14 UTC. I flagged that inconsistency
before registration. Root preserved the original decision bytes and added
[ROOT_TRACE_TIMING_CORRECTION.md](ROOT_TRACE_TIMING_CORRECTION.md). The correction
records the decision-then-preflight tool sequence and identifies 11:59 as an
erroneous estimate. Local file timestamps are consistent with decision/script
creation preceding result creation by about 0.27 seconds; they are supporting
workspace metadata, not an independent publication timestamp. The original
decision hash remains exactly the one bound by the result.

| Artifact | SHA256 |
|---|---|
| ROOT_TRACE_DECISION.md | `95e1ad3596f552d4c75faca2fce9ef636e33b96ad04514656e94334552cf599f` |
| root_trace_capacity.py | `c440e37ff228b3b453c9a1db9c98cc43f2f95199ef2ee9d16cf4b680c69b49bd` |
| ROOT_TRACE_CAPACITY.json | `f1bedc91e3fa2a0839113f577a8bb2a39b823eb5c41f8340480bdd7fc5fb8d5c` |
| ROOT_TRACE_TIMING_CORRECTION.md | `415a3919288eb3dee91172b607aa998e4b546020d5c29b0d91ffbff3a0be2010` |

The six cache hashes are the unchanged hashes recorded in the prior
[LATITUDE_CAPACITY_REVIEW.md](LATITUDE_CAPACITY_REVIEW.md). The independent code
below checks the parent bindings and emits those hashes again. The earlier
latitude histogram had exposed aggregate length counts, as the decision
discloses; this preflight is not an independent held-data discovery.

## Reproduce

Run from repository root. This block prints metadata and booleans only. It does
not import the producer, inspect any image, fit numbers or print target strings.

```python
from pathlib import Path
from collections import Counter, defaultdict
import hashlib,json,re
R=Path.cwd();P=R/'experiments/yolo/gdt915_terminal_lr_phrase_transfer';S=R/'research_registry/work_batches/ten_hours_20260915'
lock=json.loads((R/'experiments/yolo/gdt928_multi_anchor_complete_paragraphs/PREREG_LOCK.json').read_text())['files']
for name,h in lock.items():assert hashlib.sha256((R/name).read_bytes()).hexdigest()==h,name
allowed=set(json.loads((P/'src/SPEC.json').read_text())['allowed_selectors']);assert len(allowed)==179
assert not any(p.startswith(('f84','f116v')) for p in allowed)
claimed=json.loads((S/'ROOT_TRACE_CAPACITY.json').read_text())
assert claimed['required_groups']==23 and claimed['required_distinct_physical_leaves']==3
assert claimed['decision_sha256']==hashlib.sha256((S/'ROOT_TRACE_DECISION.md').read_bytes()).hexdigest()
answer={};parents={}
for ed in ('ZL3b','IT2a','RF1b'):
 pages=defaultdict(list);seen=set();den=Counter();reason_rows=[]
 for phase in ('DISCOVERY','EVALUATION'):
  path=P/'artifacts'/f'SOURCE_{phase}_{ed}.json';parents[path.relative_to(R).as_posix()]=hashlib.sha256(path.read_bytes()).hexdigest()
  data=json.loads(path.read_text());ix={name:i for i,name in enumerate(data['group_columns'])}
  for raw in data['lines']:
   m=raw['metadata'];assert m['page'] in allowed
   if m['kind']!='P':continue
   identity=(m['page'],m['locus'],m['source_row_index']);assert identity not in seen;seen.add(identity)
   gs=raw['groups'];reasons=[]
   if len(gs)<2:reasons.append('TOO_FEW_GROUPS')
   if any(re.fullmatch('[a-z]+',g[ix['ivtff_group_raw']]) is None for g in gs):reasons.append('NONLITERAL_GROUP')
   if any(int(v[ix['source_group_index']])!=int(u[ix['source_group_index']])+1 for u,v in zip(gs,gs[1:])):reasons.append('NONCONSECUTIVE_GROUP_INDEX')
   if any(u[ix['right_separator']]!='DEFINITE_SPACE' or v[ix['left_separator']]!='DEFINITE_SPACE' for u,v in zip(gs,gs[1:])):reasons.append('UNDEFINITE_SEAM')
   pages[m['page']].append(dict(row=int(m['source_row_index']),locus=m['locus'],number=int(m['locus'].rsplit('.',1)[1]),start=m['paragraph_start']=='1',end=m['paragraph_end']=='1',groups=len(gs),eligible=not reasons,reasons=reasons))
   den['P_lines']+=1
 frames=[]
 for page,lines in sorted(pages.items()):
  lines.sort(key=lambda line:line['row']);starts=[i for i,line in enumerate(lines) if line['start']]
  for k,first in enumerate(starts):
   limit=starts[k+1] if k+1<len(starts) else len(lines)
   last=next((i for i in range(first,limit) if lines[i]['end']),None)
   if last is None:
    den['unclosed_start' if k+1<len(starts) else 'unclosed_end']+=1
    continue
   block=lines[first:last+1];numbers=[line['number'] for line in block]
   if numbers!=list(range(numbers[0],numbers[0]+len(numbers))):
    den['gapped_paragraphs']+=1;continue
   den['complete_paragraphs']+=1;den['anchor_lines']+=sum(line['eligible'] for line in block)
   frame=dict(id=page+'|'+block[0]['locus']+'-'+block[-1]['locus'],page=page,leaf=int(re.match(r'f(\d+)',page)[1]),groups=sum(line['groups'] for line in block),eligible=all(line['eligible'] for line in block),ineligible_lines=[line['locus'] for line in block if not line['eligible']])
   frames.append(frame)
   if frame['groups']==23:
    reason_rows.append(dict(id=frame['id'],line_reasons=[dict(locus=line['locus'],reasons=line['reasons'],groups=line['groups']) for line in block],start_locus=block[0]['locus'],end_locus=block[-1]['locus']))
 hist={str(n):v for n,v in Counter(f['groups'] for f in frames).items()}
 literal_hist={str(n):v for n,v in Counter(f['groups'] for f in frames if f['eligible']).items()}
 rows=[f for f in frames if f['groups']==23];leaves=sorted({f['leaf'] for f in rows if f['eligible']})
 own=dict(complete=len(frames),literal=sum(literal_hist.values()),all_length_histogram=hist,literal_length_histogram=literal_hist,candidate_rows=rows,eligible_physical_leaves=leaves,three_leaf_capacity=len(leaves)>=3)
 assert own==claimed['panels'][ed],ed
 assert dict(den)==claimed['denominators'][ed],(ed,dict(den),claimed['denominators'][ed])
 answer[ed]=dict(complete=len(frames),literal=own['literal'],candidate_rows=rows,eligible_physical_leaves=leaves,three_leaf_capacity=own['three_leaf_capacity'],candidate_line_reasons=reason_rows)
assert sum(len(v['candidate_rows']) for v in answer.values())==14
assert claimed['independent_meaning_confirmation_capacity']==0
print(json.dumps(dict(status='PASS',parent_bindings_checked=len(lock),parents=parents,panels=answer),sort_keys=True,indent=2))

```

The eligible IT2a capacity justifies proceeding to the separately registered
finite model if root selects it. It does not predict that a single local case
or a shared three-record interpretation will survive. No target code fitting
occurred in this review, and no source or global file was changed.
