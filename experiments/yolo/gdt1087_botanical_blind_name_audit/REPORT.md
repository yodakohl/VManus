# GDT1087 — complete 23-image audit of a public plant-name list

**Decision: the published 23-name list supplies no usable word anchor.**
Under the preregistered two-diagnostic-trait rule, **0/23** asserted plants
receive visual support, **13/23** show a visible morphological conflict and
**10/23** remain undecidable. These are descriptive classifications of
stylized drawings, not a significance test or independent word confirmations.
The complete [joined result](artifacts/RESULTS.tsv) retains every first group,
blind observation, alternative, source canvas and image hash.

The visual annotator received only the 23 fixed folio IDs and official Yale
canvases. Its [23-row inventory](artifacts/BLIND_VISUAL.tsv) was frozen at
SHA-256 `3a0c973f0522027c4d18dfdb745a868eee90d2cd3732538e765a1659dac2aed9`
before the public names were joined. The names and botanical diagnostic
references were fixed separately. The root had previously seen the source
table and four GDT1063 image cases: f2v, f9v, f11r and f24v remain exposed
calibration cases. Source conditioning and stylization make this an
exploratory plausibility audit. The validator checks identity, scope and join,
not human botanical judgments.

| Folio | First group | Asserted plant | Decision | Key observation or limit |
|---|---|---|---|---|
| f2v | `kooiin` | BORAGO (borage) | CONFLICT | Visible organs differ from bristly-leaved, blue star-flowered Borago. |
| f3v | `koaiin` | ARUM | CONFLICT | Heads and foliage oppose the Arum spadix/spathe and simple arrow leaves. |
| f4v | `pchooiin` | MANDRAGORA (mandrake) | UNDECIDABLE | Inflated terminal organ and irregular tuber are not securely flower or fruit; mandrake traits cannot be scored. |
| f8r | `pshol` | VIOLA (violet) | UNDECIDABLE | Large sagittate leaf has no visible flower; single stylized leaf cannot rule in or out Viola. |
| f9v | `fochor` | JACEA (knapweed) | CONFLICT | Literal public knapweed expansion conflicts with the pansy-like flowers; bare historical Jacea is separately compatible. |
| f10v | `paiin` | MEUM (spignel) | CONFLICT | Meum has feathery divided foliage and umbels, unlike both depicted organs. |
| f11r | `tshol` | TILIA (linden) | CONFLICT | No woody tree, heart leaves or pale linden flower/bract complex is depicted. |
| f11v | `poldchody` | VERBENA | UNDECIDABLE | Cone-like mass has uncertain organ identity and cannot securely adjudicate Verbena. |
| f14r | `pchodaiin` | MENTHA (mint) | UNDECIDABLE | Single red head is composite-like, but its construction is too schematic for a decisive contrast with mint. |
| f15r | `tshor` | TIMO (thyme) | CONFLICT | These conspicuous organs oppose small woody thyme foliage and tubular whorls. |
| f19v | `pochaiin` | LINUM (flax) | UNDECIDABLE | Leaf units and tiny flowers are too stylized to decide flax morphology confidently. |
| f22r | `pol` | MORUS (mulberry) | UNDECIDABLE | Blue cups and red bead spikes may be differing organs; no reliable mulberry fruit or tree diagnosis. |
| f24v | `tchodar` | CICUTA (hemlock) | CONFLICT | Hemlock should have finely divided leaves and small white compound umbels. |
| f28r | `pchodar` | MENTA (mint, Occ.) | UNDECIDABLE | Apparent spadix-like cylinders lack a visible spathe; mint is not supported, but organ identity remains uncertain. |
| f28v | `kshol` | ALOE | CONFLICT | Aloe expects fleshy rosette leaves; depicted architecture is an erect slender-leaved herb. |
| f32r | `fchoiin` | FRAGARIA (strawberry) | CONFLICT | Neither trifoliate serrate leaves nor strawberry flower/aggregate fruit appears. |
| f38r | `tolor` | CARDO (thistle) | UNDECIDABLE | Toothed single blade could be a thistle leaf but no capitulum or second diagnostic feature is visible. |
| f42v | `tcho` | CICUTA (hemlock) | CONFLICT | Opposes fine hemlock leaves and compound white umbels. |
| f46v | `pody` | PAEONIA (peony) | CONFLICT | Multiple small bracted heads oppose a peony’s large bowl flowers and divided leaves. |
| f49r | `poshol` | MORUS (mulberry) | CONFLICT | Tuberous herb architecture opposes woody Morus and its catkins or aggregate fruit. |
| f50v | `tchy` | SENECIO (groundsel) | UNDECIDABLE | Heads are composite-like, compatible only at broad family level; groundsel species cannot be ruled in, and apparent b... |
| f53v | `tshor` | TIMO (thyme) | CONFLICT | Large ray-like heads oppose small tubular thyme flower whorls and tiny woody foliage. |
| f55r | `podaiin` | MEUM (spignel) | UNDECIDABLE | Broad leaves and red organs look unlike Meum, but the floral structure is too schematic for decisive exclusion. |

The source's advertised highlights do not survive the fixed rule:
f2v `kooiin=BORAGO` conflicts with the conspicuous organs, while f38r
`tolor=CARDO` has only a possibly thistle-like blade and no second diagnostic
feature or flower head. The exact `tshor` is assigned thyme on both f15r and
f53v, yet both drawings visibly conflict with thyme and differ from each
other in their flower heads. Both asserted hemlock pages (f24v/f42v) conflict.
The two Morus pages are undecidable/conflicting; the two Meum pages are
conflicting/undecidable. The mint spellings f14r/f28r remain undecidable.
No duplicate-name pair has two visually supported owners, and the sole
duplicate exact head has two conflicts.

The strongest botanical observation remains f9v's pansy-like *Viola*. The
published claim explicitly expands *Jacea* to knapweed, which conflicts with
the image; GDT1064 separately showed that bare historical *Jacea* could also
refer to a pansy. **`fochor` ≈ pansy/*Viola* remains a C0 complete-word
hypothesis**, conditional on first-head-as-name. Its exact form occurs once
on one page in each alternate reading of the 179-selector corpus; no second
independently bound same-taxon slot exists. `tshor=thyme` is disfavored as a
working gloss across its complete admitted contexts. The public source's
positional mappings, vowel stripping and retrospective plant IDs are not
validated by this audit. No confirmed name or decipherment follows.

The annotator resolved 23 unique official Yale canvas labels. Their scans
show thin neighboring-page edge slivers, incidentally seen but neither
analyzed nor admitted. f84/f84r and reserves stayed closed. No manuscript
text beyond the existing GDT1062 first-group results was opened. Root native
spot checks covered f2v, f3v, f9v, f15r, f32r, f38r and f53v. Sources:
[Yale manuscript manifest](https://collections.library.yale.edu/manifests/2002046),
[public name table](https://github.com/scott-schechter/voynich-decoded/blob/71f2f3c91e9113d285ab21e024f1dd70c1f43c44/publication/04-plant-identifications.md),
and the fixed [botanical references](src/BOTANICAL_REFERENCE.tsv).
