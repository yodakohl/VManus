# V20 selection — one Herbal/Biological bridge deck

Date: 2026-08-21

Status: **concrete exploratory source expansion, not deciphered plaintext**.

## Question and answer

V19 deliberately refused to rewrite cards that occur in both Herbal and
Biological pages. V20 now reads all 136 occurrences of those 17 bridge cards
and asks whether one executable meaning can survive both registers.

The answer is provisionally **yes**. Thirteen existing meanings already work
without repair. Four vague defaults become more concrete:

| card family | events H/B | selected instruction |
|---|---:|---|
| CHTY | 1/1 | work it until evenly homogeneous |
| QOKAIIN | 1/8 | begin the next measured entry |
| AL/DAL | 1/9 | apply it at the place indicated by the drawing |
| OTCHEY | 1/1 | take the final indicated share |

These four revisions affect 23 events. They preserve exact-card identity and do
not assign meanings to glyph fragments.

## Resulting common workshop mini-language

The strongest bridge deck can now be read as a small practical instruction
inventory:

```text
BEGIN NEXT MEASURED ENTRY
THIS PRESENT PORTION
IN THE STATED MEASURE
FROM THE SAME / FOREGOING BATCH
WITH THE FOREGOING PREPARATION
COMBINE TWO PORTIONS
STIR UNTIL EVEN
WORK UNTIL HOMOGENEOUS
CONTINUE UNTIL CLEAR
WHILE STILL WARM
PREPARED LIQUID
WHEN READY
APPLY / USE THIS PORTION
APPLY AT THE PICTURED PLACE
TAKE THE FINAL INDICATED SHARE
BOIL GENTLY AND CLOSE
```

This is simpler than positing unrelated Herbal and Bio dictionaries. The
register supplies the omitted arguments: a Herbal picture contributes the
plant/part and a Biological diagram contributes vessel, channel or application
site. The cards express portable instructions over those arguments.

## Most informative changes

### QOKAIIN

Its old “take up the next portion or instruction” mixed object and discourse
functions. The new **begin the next measured entry** retains both: on f55v it
opens a measured broad-leaf preparation; in eight Bio occurrences it activates
the next short configuration entry. This is a source-level paraphrase, not the
claim that the card spells “begin”.

### AL/DAL

The old phrase merely located something “at the place indicated by the
drawing.” The Herbal occurrence on f56r and nine Bio occurrences become more
coherent if the card is an executable application instruction:

> **apply it at the place indicated by the drawing**

This remains risky: the weaker rival is a pure location relation with the
action inherited from its governing card.

### CHTY versus CTHY

V20 keeps two exact cards distinct:

- CHTY: **work it until evenly homogeneous**;
- CTHY: **when the preparation is ready**.

The former is a process endpoint; the latter introduces a ready-state
condition. This avoids collapsing similar surface forms into one guessed word.

### OTCHEY

The two occurrences are both treated as the marked terminal selection:
**take the final indicated share**. “Mark the following share” remains the
strongest notation-only rival.

## What this changes in the overall theory

The working system now looks less like a separate prose cipher plus unrelated
diagram labels and more like a teachable workshop register:

```text
picture or diagram supplies owner and location
  + portable action/reference/measure card
  + register-local rare payload cards
  + renderer and closure
```

The bridge deck is small, high-frequency and learnable by several scribes.
Rare Herbal cards can describe the plant dossier while the same common
instructions govern Bio apparatus/application records.

## Artifacts and limits

- `V20_CROSS_REGISTER_CARD_AUDIT.tsv`: all 17 decisions;
- `V20_136_OCCURRENCE_LEDGER.tsv`: every bridge occurrence;
- `V20_SELECTED_COMPLETE_DEFAULT_LEXICON.tsv`: complete 569-entry dictionary;
- `V20_SELECTED_COMPLETE_TRANSLATION_LEDGER.tsv`: complete 776-event reading.

The meanings remain forced working defaults. Nothing here establishes English,
Latin, a specific language, plaintext, a medical action or external referent.
f84 and f84r remained sealed.
