# GDT645 method

## Question

Can the five strongest exact whole surfaces on the GDT644/V21 one-hole
frontier receive concrete, compositional and replaceable readings that close
their source lines without freeing any substring component?

## Frozen source

- GDT644 V21 dictionary, exact glossary, line coverage, complete passages and
  one-hole frontier;
- the same 179-page allow-list;
- guarded projections of only `page,locus,token_index,eva,section,language,hand`
  and the required cross-reader line fields;
- no f1r, f84/f84r, new page or image.

The three transcription editions are alternate readings of one manuscript.
They are used only to mark exact, boundary-normalized and divergent target
positions.

## Ordered cards

The fixed sequence is `oky`, `otchor`, `ychair`, `cheaiin`, `cthom`. Each card
must:

1. occur as an exact ZL3b whole surface;
2. have at least one all-reader-exact target position;
3. close its declared V21 source line when inserted;
4. have a concrete meaning without generic work/process filler;
5. preserve all uncertain pieces as exact-whole-bound;
6. leave every reader variant and every newly exposed hole visible.

The builder replays V21 byte-for-byte, inserts one exact whole card per round,
rebuilds all 4,128 line states and records the cumulative dictionary hash. It
then audits every target occurrence against the untouched V21 companion
glosses. Family atlases include observed cells and four explicit absent held
cells; an absent cell is not a generated word.

## Reproduction

```bash
python3 experiments/yolo/gdt645_ranked_five_surface_completion/src/run.py
python3 experiments/yolo/gdt645_ranked_five_surface_completion/src/validate.py
```

The independent validator reruns the builder in a temporary directory,
byte-compares every generated artifact, independently recounts target and
family surfaces through guarded queries, replays the sequential dictionary
hash chain and checks all result/input/output hashes.

## Claim boundary

The five German readings are replaceable working defaults. `cthom=Handvoll`
is a deliberately bold exact-whole hypothesis informed by an approximately
contemporary `M=manipulus` comparator. It does not license free `m`, `om` or a
productive terminal-M rule. No plaintext language, phonetics, ingredient
identity or unrestricted substring semantics follows.
