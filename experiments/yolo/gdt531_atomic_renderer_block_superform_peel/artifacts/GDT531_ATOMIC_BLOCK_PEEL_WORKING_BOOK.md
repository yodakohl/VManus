# GDT531 atomic block-peel working book

## Current change

```text
saiis = S+A_ADDR+IIN+S
        WÄHLEN · HIER · STUFE · WÄHLEN
        “Wählen; hier die Stufe wählen.”
```

Certificate:

```text
old saiisol = S+A_ADDR+IIN+S+OL  (f77r, one event)
remove final ol / final OL
current saiis = S+A_ADDR+IIN+S
old right-edge ol/OL signature = 29/33
p = 0.830985915; reliability = 0.935483871
```

## Alternatives retained

1. `S+AIIN+S` (rank 2): exact tiling `saii|s`; `saii` occurs once and the
   same-recipe `saiin` family twenty times.
2. `S+IIN+S` (rank 3): previous visible atomization, now replaced.

The first alternative remains useful if later syntax prefers the fused `AIIN`
stage marker. It does not presently beat the exact whole-superform carrier.

## Edition state

- 159/159 current forms retain a default working recipe.
- 154 are now rank one, 158 lie within top two, and rank sum is 171.
- This pass changed only `saiis`; all GDT530 choices, including
  `chekchy=CH+K+Y`, are preserved.
- The `ol` removal is local and certified, not a global suffix rule.

## Remaining queue

```text
aiicthy       current rank 9
dairykodas    current rank 2
dalcheeeky    current rank 2
dsholdaiir    current rank 2
qef           current rank 2
```

Next preferred probe: test `dsholdaiir` as the exact-card sequence
`d | shol | daiir`, with special weight for the same-owner, same-block
`daiir=DA+IIN+R` carrier. Do not admit new pages for that test.
