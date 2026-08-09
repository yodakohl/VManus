# Source-separator transcription correction

Status: **PASS_SOURCE_SEPARATOR_TRANSCRIPTION_LOSS_ACCOUNTED**

The three frozen human IVTFF sources contain **15,985** reading
rows, **115,470** source-separated groups, and
**99,485** explicit source boundaries.  The old
pre-grounding `surface` exactly reconstructs its own **118,011**
ASCII fragments, but it is not a complete representation of those sources.

- **173** source groups produce no ASCII token;
  **25** whole reading rows
  disappear for this reason.
- **2,688** single source groups produce multiple
  ASCII fragments, creating **2,714**
  boundaries that no transcriber marked.
- Only **112,609** source groups map one-to-one to an
  old ASCII token.

The new atlas stores every source group, its exact left/right separator state,
and its complete mapping to the legacy fragments.  Extended `@number;` entities
and uncertain/alternative forms remain verbatim; none is guessed or expanded.

The source separators comprise 93,660
confident apparent spaces, 3,425
uncertain small spaces, 2,394
drawing interruptions, and
6 unaligned
drawing interruptions.

This corrects the representation boundary.  It does not decide which spaces
are authorial and supplies no sound, word, role, lexeme, plaintext, language,
or translation.
