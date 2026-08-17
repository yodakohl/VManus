# GDT238 — stable label prefix to visible relation mode

## Result

**WEAK_PREFIX_RELATION_MODE_LEAD_LOW_CAPACITY**

The seven prefixes stable across all GDT237 section folds carry a small
cross-folio clue about the human-described geometric relation of a label.
Among 310 non-f84, family-covered exact label annotations, 68 rows carry a
stable prefix and have a prefix seen on another folio.  Prefix-modal prediction
gets 56/68 (`.824`) relation classes correct versus 51/68 (`.750`) for the
same-section modal baseline: five paired wins, zero losses, one-sided sign
tail `.03125`.

The relation inventory is highly asymmetric:

| relation class | rows |
|---|---:|
| PROXIMITY | 225 |
| ATTACHMENT | 73 |
| ENCLOSURE_OR_CONTACT | 7 |
| ARRAY_OR_GROUP | 5 |

Most stable-prefix occurrences are proximity descriptions.  The gain is only
five rows, so it is not evidence for a rich relation vocabulary.  Exact raw
families provide an important counterexample: on 112 cross-folio-covered rows
they score 65 correct versus 80 for the section baseline (`-.134`), with 6
paired wins and 21 losses.

## Interpretation

The result refines, rather than reverses, GDT235–237.  Some transferred label
prefixes appear to participate in a graphical **relation/rendering mode** that
is more stable than the full family.  The full family still does not carry a
portable relation or object key.  A conservative working decomposition is:

```text
PARTIAL LABEL/RELATION RENDERER + REGISTER-BOUND OPAQUE RESIDUAL
```

“Relation renderer” here means only that a source-family prefix weakly predicts
the catalogue's visible attachment/proximity class.  It does not say the
prefix means “near,” “attached,” “inside,” or any other relation.  Proximity is
not ownership, and the source descriptions are not independent repetitions of
an authorial semantic category.

## Claim ceiling

This is a low-capacity exploratory geometric-association result.  It establishes
no authorial ownership, relation word, object name, morpheme, sound, language,
plaintext, or translation.  No f84 row was retained, joined, or scored, and no
new f84 access occurred.
