# GDT216 — readable Wound Man terminal-key source audit

## Finding

A real medieval medical diagram supplies the missing mechanism-level positive
control for GDT215.  In Wellcome MS 49, fol. 35r (southern Germany, circa
1420–30), short phrases beside depicted injuries are followed by small red
numbers.  Each number directs the reader to the correspondingly numbered
paragraph in the forty-four-part *Wundarznei* on the preceding two folios.

The diagram phrase and the prose paragraph are not identical strings.  The
small terminal key, rather than the descriptive phrase, carries the exact
cross-reference.

## Sources

The institutional Wellcome catalogue identifies MS 49, the Wound Man text and
diagram on fols. 34r–35v, and the relevant manuscript images.  Jack Hartnell's
peer-reviewed study, “Wording the Wound Man” (2017), documents the numbered
catchphrases, the preceding forty-four-paragraph surgical treatise, and three
explicit key examples used by this freeze:

- key 14: a large-intestine/stomach/entrails injury points to treatment item
  14;
- key 19: an itchy/scabby condition points to item 19;
- key 41: snakebite/poisoning points to item 41.

Only those three author-described examples enter the positive-control table.
No manuscript text or image is re-transcribed by this experiment.

## Mechanism spectrum

The same study documents important alternatives:

- some MS 49 captions are unnumbered and contain treatment text directly;
- Copenhagen MS Ny Kgl. Saml. 84b replaces paragraph numbers with red lines
  directly joining injuries to blocks of curative text;
- the 1491 *Fasciculus medicinae* uses initials from `a` onward as paragraph
  indicators;
- the later Wellcome MS 290 Wound Man retains captions but lacks the linked
  treatise;
- later printed versions can use the image as an unkeyed visual herald.

Thus a medical diagram can support keyed reference, direct annotation, or no
recoverable key.  The target test must be allowed to fail without excluding a
mixed medical diagram architecture.

## Consequence for the Voynich test

GDT187 tested whole-group, PAGE_HOST, character, and compiler-bag similarity
between label inventories and page prose.  It did not test the source-native
positional analogue now motivated by the readable control:

```text
final compact element of a diagram label
    ->
initial compact element of a prose paragraph
```

GDT216 therefore freezes a narrow terminal-to-initial test before calculating
its target scores.  This is new mechanism data, not a repair of GDT187.

## Limits

The Wound Man is surgical, not balneological, and uses visible Arabic numerals
or alphabetic initials.  Voynich labels are not assumed to contain numbers,
letters, rubrics, wound descriptions, or paragraph indices.  A structural
match would identify only a possible compact reference field.

No Voynich source or image was accessed during this source audit.  No f84
artifact was accessed.
