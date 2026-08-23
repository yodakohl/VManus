#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    forecast = rows("TWO_HUNDRED_SIXTY_FIFTH_TWELVE_UNSEEN_COMPOSITIONS.tsv")
    exercises = rows("TWO_HUNDRED_SIXTY_FIFTH_SIX_WRITING_EXERCISES.tsv")
    astro = rows("TWO_HUNDRED_SIXTY_FIFTH_TWO_ASTRO_MATCHES.tsv")
    checks = {
        "12_forecasts": len(forecast) == 12 and len({r["forecast_id"] for r in forecast}) == 12,
        "12_unique_recipes": len({r["component_recipe"] for r in forecast}) == 12,
        "ten_unseen_two_astro": sum(r["surface_status"] == "UNSEEN_ON_TEN_PAGES" for r in forecast) == 10 and sum(r["surface_status"] == "MATCHES_EXISTING_ASTRO_LABEL" for r in forecast) == 2,
        "two_astro_matches": len(astro) == 2 and {r["visible_surface"] for r in astro} == {"alaiin", "chedaiin"},
        "astro_matches_direct": all(r["composition_match"] == "DIRECT_MEANING_MATCH" and r["page"] == "f67r2" for r in astro),
        "confidence_6_4_2": sum(r["confidence"] == "HIGH" for r in forecast) == 6 and sum(r["confidence"] == "MEDIUM" for r in forecast) == 4 and sum(r["confidence"] == "LOW" for r in forecast) == 2,
        "six_exercises": len(exercises) == 6 and len({r["exercise_id"] for r in exercises}) == 6,
        "all_values_concrete": all(r["predicted_short_meaning_de"].strip() and r["expected_sentence_slot"].strip() for r in forecast),
        "all_have_analogies": all(r["closest_attested_analogies"].strip() for r in forecast),
        "no_prose_collision": all(r["surface_status"] != "ALREADY_IN_PROSE" for r in forecast),
        "sealed_pages_absent": all("f84" not in "\t".join(r.values()).lower() for r in forecast + exercises),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "VALIDATION.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        print(json.dumps(result, indent=2, ensure_ascii=False))
        raise SystemExit(1)
    print(f"PASS {sum(checks.values())}/{len(checks)}")


if __name__ == "__main__":
    main()
