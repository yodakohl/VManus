# Reproducing the Greek source receipt check

Run from the repository root:

```sh
python3 research_registry/proposals/laufenberg_f85r2_20260926/source_supply_20260929/validate_gd_greek_word_alignment.py
```

The four original Allen page rasters and the219v source metadata receipt are
published at their existing bound paths under
`research_registry/work_batches/seven_hours_20260914/greek1364_cache/`.
They reproduce exactly the images the observers used, without dependence on a
PDF renderer version. Allen1890 is the historical publication, not a new corpus.
The large original PDF/text and native images remain external source assets.
For a fresh checkout, fetch the five missing original files with the following
explicit source recipe, which opens no Voynich data. Existing files are not
replaced; the validator checks exact SHA256 values before crediting them.

```python
from pathlib import Path
import json
import urllib.request
base = Path("research_registry/work_batches/seven_hours_20260914/greek1364_cache")
base.mkdir(parents=True, exist_ok=True)
packet = json.loads(Path("research_registry/work_batches/seven_hours_20260914/GREEK1364_SOURCE_RESULT.json").read_text())
urls = {
    "journalofhelleni10soci.pdf": packet["pdf_url"],
    "journalofhelleni10soci_djvu.txt": "https://archive.org/download/journalofhelleni10soci/journalofhelleni10soci_djvu.txt",
}
for entry in packet["images"]:
    if entry["exact_label"] in {"219v", "265v", "284r"}:
        urls["reg181_" + entry["exact_label"] + ".jpg"] = entry["url"]
for name, url in urls.items():
    dest = base / name
    if not dest.exists():
        urllib.request.urlretrieve(url, dest)
```

This fetch recipe was not reexecuted during the new pilot: all original bytes
were already cached and their hashes verified. An unavailable or changed URL
is an acquisition failure, not permission to substitute bytes. The validator
checks bookkeeping and supplied annotation equations only. It does not inspect
pixels, recover a complete writer, test the continuation or certify a meaning.
The optional inspection crop is specified in GD_GREEK_POSTFREEZE_VIEW.json;
it adds no new source pixels and is not an input to the receipt check.
