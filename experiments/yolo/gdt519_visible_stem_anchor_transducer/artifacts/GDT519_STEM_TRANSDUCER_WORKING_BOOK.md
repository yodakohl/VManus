# GDT519 compact stem-transducer working book

## Current architecture

- candidate generator: GDT517 residual-closure compiler;
- base ordering: GDT518 visible-form signature + old rank + small neighbor term;
- anchor deck: 45 canonical atom stems, 287 learned 2-/3-atom renderer
  sequences, 332 sequences and 473 surface options in the full old model;
- selected alignment: monotone full-surface partition, renderer width 1–3,
  anchor weight 1.0;
- lookup precedence: exact event > unique known surface/domain option > GDT519
  top candidate.

## Metrics

Four-fold old-form rehearsal (1,441/1,558 truths generated):

- compiler: 1,000 top-1, 1,395 top-5, rank sum 2,609, deepest 69;
- form decoder: 1,054 top-1, 1,395 top-5, rank sum 2,374, deepest 35;
- stem transducer: 1,082 top-1, 1,418 top-5, rank sum 2,152, deepest 23.

Current 159 old-base-new forms:

- GDT517: 117 top-1, 157 top-5, rank sum 281, deepest 56;
- GDT518: 134 top-1, 158 top-5, rank sum 212, deepest 14;
- GDT519: 138 top-1, 158 top-5, rank sum 192, deepest 8;
- GDT518→519: eight errors corrected, four hits lost, one wrong choice changed.

## Renderer admission

- minimum support: 10;
- one-atom share: at least 0.70;
- two-/three-atom share: at least 0.60;
- at most five aliases per sequence;
- at most canonical length + 2 visible characters;
- alias penalty: `0.25*weighted_edit + 0.10*(-log share)`;
- edit costs: extra visible char 1, missing claimed anchor 2, substitution 1.

Anchors are spelling handles, not German meanings. Short learned renderers are
part of the model, not noise: `chek~CH+K` is the clearest current example.

## Remaining route

Twenty-one current top-1 errors remain. Separate them into:

1. productive atom versus learned renderer boundary (`chekeey`, `okedals`,
   `saiis`, `dsholdaiir`);
2. `DY` versus `D_ADDR+Y` versus `Y`;
3. `OL` versus `O+L`;
4. local-character versus renderer-shell attachment;
5. the two deeper long forms, led by `aiicthy` now at rank 8.

The next closed-page pass should learn positional renderer licenses for those
families from the full older paradigms and preserve a finite alternative when
the license is tied. Do not open another page for that pass.
