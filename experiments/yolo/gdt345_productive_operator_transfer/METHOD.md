# GDT345 method — productive formal-operator transfer

Date: 2026-08-19

Status: `FROZEN_BEFORE_OPERATOR_SCORING`

## Question

Can a formal change operator learned on other manuscript events be selected from
the source state and independently observable physical boundary/layout context,
then applied to reconstruct the next formal state on an unseen folio? This is a
predictive successor test, not GDT344's target-conditioned path description.

No semantic alignment is performed. Exact GDT327 joint tuples remain atomic;
PAGE_HOST is never factored or inspected as a string.

## Source and seal

The complete f84-free GDT327 joint-tuple interlinear is joined one-to-one to
GDT278 by `(page,locus,group_index)`. Every raw selector beginning `f84` is
rejected before the remainder of its row is parsed. Adjacent events are formed
only within one physical page and in frozen source order.

## Canonical source and target states

Each state has exactly six nominal coordinates:

1. `local_frame`;
2. `inner_d`;
3. `right_family`;
4. `dy_closure`;
5. `b3`;
6. canonical wrapper.

The supported renderer effects `s@LINE_START` and `q@POST_DY` are mapped to
canonical wrapper `NONE`; every other wrapper value remains distinct. No other
normalization, tuple merge, substring feature, or PAGE_HOST operation is
allowed.

For each coordinate, the target delta is `KEEP` if its value is unchanged and
`SET:<target-value>` otherwise. The complete text-side operator is the ordered
six-delta vector. Its registered full identity also records independently
observable `SAME_FIELD/FIELD_BOUNDARY/LINE_RESET/RECORD_RESET`, field-order and
reset state. Boundary/layout is therefore part of the operator occurrence but
is supplied as prediction context; no target formal coordinate is supplied.

Applying the predicted operator means applying each predicted `KEEP` or `SET`
to the source's six-coordinate state. Exact recovery requires equality to the
actual six-coordinate next state.

## Allowed context and forbidden leakage

All models may see only:

- physical boundary scope and field order;
- target line-entry status, within-field position, and physical-line quartile;
- source-side formal information licensed for that model.

They never see target wrapper, target coordinate ID, target joint-tuple ID, a
target-derived signature, PAGE_HOST, or target surface characters.

## Fixed models

All models predict the same six delta components with a product categorical
code. Global component counts use Jeffreys `0.5`; the layout table is shrunk to
global with fixed concentration 64 and source-conditioned tables are shrunk to
layout with fixed concentration 32. Nothing is tuned on held data.

1. `PLACEMENT`: boundary/layout only.
2. `EXACT_PREDECESSOR`: layout plus exact atomic source `joint_tuple_id`.
3. `SOURCE_STATE_TABLE`: layout plus the complete six-coordinate source state.
4. `FACTORIAL_OPERATOR`: for each delta coordinate separately, layout plus only
   the corresponding source-coordinate value. This is the productive model:
   it can combine learned coordinate operations on an unseen full state.

An event is codelength-eligible only when every true delta label occurs in the
training fold. The decisive recombination subset additionally requires the
full source state and full registered operator to occur in training while that
exact source-state×operator combination does not.

## Held transfer

The primary analysis leaves one physical folio out. Three additional transfer
families leave out an entire section, register, or hand. A category is powered
at 50 eligible events. Alternative transcriptions are not replicated samples;
GDT327's frozen consensus/joint state is the sole event layer.

The productive claim requires `FACTORIAL_OPERATOR` to:

- beat `PLACEMENT`, `EXACT_PREDECESSOR`, and `SOURCE_STATE_TABLE` in aggregate
  LOFO held codelength and exact next-state recovery;
- beat both required baselines on the unseen source-state×operator subset;
- beat `EXACT_PREDECESSOR` on at least 60% of powered folios;
- have positive aggregate gain and at least 60% positive powered held
  categories in each of the section, register, and hand split families; and
- have max-two inclusive p <= .05.

The fixed-prediction null shuffles complete true text-side operator vectors
within held folio × exact observable layout context, preserving source states,
prediction vectors, boundary opportunities, and marginal operators. It tests
exact-recovery gain of `FACTORIAL_OPERATOR` and `SOURCE_STATE_TABLE` over
`EXACT_PREDECESSOR`; 4,096 worlds and their max-two statistic are frozen. It is
an alignment diagnostic rather than a refitted model-selection null.

## Decisions

- `PRODUCTIVE_FORMAL_OPERATOR_TRANSFER_SUPPORTED`
- `LOCAL_OR_LEXICAL_OPERATOR_DEPENDENCE_ONLY`
- `NO_PRODUCTIVE_OPERATOR_TRANSFER`
- `INSUFFICIENT_CAPACITY`

## Claim ceiling

At most GDT345 can establish that independently learned formal-coordinate
change operations productively reconstruct held next formal states beyond
layout and exact-predecessor baselines. It cannot establish a morpheme,
linguistic morphology, semantic event, word, meaning, sound, language,
plaintext, translation, or any f84 result.
