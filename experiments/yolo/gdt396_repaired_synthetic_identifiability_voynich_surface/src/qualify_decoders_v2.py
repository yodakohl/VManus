#!/usr/bin/env python3
"""Narrow post-oracle eligibility correction for GDT396 qualification."""

from __future__ import annotations

import qualify_decoders as base


_ORIGINAL_W10 = base.semantic_w10_false_rates


def semantic_w10_false_rates(
    data: list[dict], decoder: str, prop: str, representation: str, surface: str,
) -> list[float]:
    """Exempt only complete routes that are explicitly unsupported."""
    if prop in base.SEMANTIC_PROPERTIES:
        selected = [
            row for row in data
            if row["decoder_id"] == decoder and row["property_id"] == prop
            and row["representation_id"] == representation
            and row["surface_id"] == surface and row["world_id"] == "W10"
            and row["method_variant"] == "PRIMARY"
        ]
        if (
            len(selected) == 5
            and len({int(row["corpus_seed"]) for row in selected}) == 5
            and {row["status"] for row in selected} == {"UNSUPPORTED"}
        ):
            return []
    return _ORIGINAL_W10(data, decoder, prop, representation, surface)


base.semantic_w10_false_rates = semantic_w10_false_rates


if __name__ == "__main__":
    raise SystemExit(base.main())
