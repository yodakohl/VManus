#!/usr/bin/env python3
"""Render the winning anonymous source generator as a readable atlas."""

import csv, json
from pathlib import Path

from gdt001_core import ROOT


def main():
    bundle = json.loads((ROOT / "gdt001_context_axis_source_codebooks.json").read_text())
    codebook = next(x for x in bundle["codebooks"] if x["order"] == 2)
    alphabet = codebook["alphabet"]
    def symbol(index):
        if index == len(alphabet): return "^"
        if index == len(alphabet) - 1: return "<SPACE>"
        return alphabet[index]
    rows = []
    for rank, item in enumerate(codebook["selected_contexts"], 1):
        context = " ".join(symbol(i) for i in item["context"])
        for value, counts in sorted(item["counts_by_value"].items()):
            total = sum(counts); ordered = sorted(enumerate(counts), key=lambda x: (-x[1], x[0]))
            rows.append({"rank": rank, "context": context, "axis": item["axis"], "metadata_value": value,
                         "events": total, "top_next_symbols": " ".join(f"{symbol(i)}:{n}" for i, n in ordered if n)[:240],
                         "gross_context_gain_bits": item["gross_split_gain_bits"]})
    with (ROOT / "gdt001_context_axis_atlas.tsv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, list(rows[0]), delimiter="\t", lineterminator="\n"); writer.writeheader(); writer.writerows(rows)
    axis_counts = json.loads(json.loads((ROOT / "gdt001_context_axis_source_results.json").read_text())["best"]["axis_counts"])
    lines = ["# GDT001 anonymous context-axis source atlas", "",
             "Status: **exploratory; not a translation**.", "",
             "The current branch leader is a reversible second-order source generator. It removes only the seven rare `j/u/z` events into an explicit ordered side channel, then uses one shared character table except at 40 paid contexts. At each exception, a known metadata axis selects the next-character table.", "",
             f"Axis counts: {', '.join(f'{k}={v}' for k,v in sorted(axis_counts.items()))}.", "",
             "`^` is line start and `<SPACE>` is a retained manual separator. Contexts are literal two-symbol source histories. They are not words or meanings.", "",
             "## Strongest exceptional contexts", "",
             "| rank | context | axis | gross split gain (bits) |", "|---:|---|---|---:|"]
    for rank, item in enumerate(codebook["selected_contexts"][:20], 1):
        context = " ".join(symbol(i) for i in item["context"])
        lines.append(f"| {rank} | `{context}` | {item['axis']} | {item['gross_split_gain_bits']:.2f} |")
    lines += ["", "The largest contexts are `ch` by Currier, `y <SPACE>` by section, `he` by hand, and line start by prose/nonprose scope. This formalizes heterogeneous construction probabilities; it does not assign a value to any sign.", "",
              "## Specificity failure", "",
              "The gain is unchanged by a global source-symbol permutation and is larger in the frozen Timm copy/modify control. Accordingly this atlas is a stronger nonsemantic baseline, not a decipherment candidate.", ""]
    (ROOT / "GDT001_CONTEXT_AXIS_ATLAS.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"rows": len(rows), "contexts": len(codebook["selected_contexts"]), "axis_counts": axis_counts}))


if __name__ == "__main__":
    main()
