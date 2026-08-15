#!/usr/bin/env python3
"""GDT072: assemble HPR3 and freeze prospective non-f84 tests."""
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent;METHOD=ROOT/"GDT072_HPR3_BEHAVIORAL_CONTENT_CLASS_METHOD.md";REPORT=ROOT/"GDT072_HPR3_BEHAVIORAL_CONTENT_CLASS_REPORT.md";EVIDENCE=ROOT/"gdt072_hpr3_evidence.tsv";PRED=ROOT/"gdt072_hpr3_predictions.tsv";MODEL=ROOT/"gdt072_hpr3_model.json";RESULT=ROOT/"gdt072_result.json"
INPUTS=[f"gdt{i:03d}_result.json"for i in range(59,72)]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def write(p,rows,fields):
 with Path(p).open("w",encoding="utf-8",newline="")as h:w=csv.DictWriter(h,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def main():
 prior={n:json.loads((ROOT/n).read_text())for n in INPUTS};assert all(not any(x["f84r"].values())for x in prior.values())
 evidence=[
 {"evidence_id":"E01","layer":"PAGE_HOST","status":"INTERNAL_INVARIANCE_SUPPORTED","measurement":"cross-wrapper same-host context gain +0.004256; 373/619 cells positive","source":"GDT064_V2","ceiling":"internal page ecology only"},
 {"evidence_id":"E02","layer":"O_OT","status":"POSITIONAL_RENDERER_STRONG_CONTEXT_WEAK","measurement":"unseen-host O-early/OT-later inherited; context gain +0.007490, sign p .0534","source":"GDT054;GDT055;GDT065","ceiling":"record placement, no content preservation"},
 {"evidence_id":"E03","layer":"RIGHT_FAMILY","status":"REGISTER_CONDITIONED_RENDERER_WITH_MODULATION","measurement":"register saves 350.054 held bits; different-renderer host context gain +0.005499 but below same-renderer by .006747","source":"GDT062;GDT066","ceiling":"not proven content-neutral"},
 {"evidence_id":"E04","layer":"DY","status":"FOLLOWING_WRAPPER_CHECKPOINT","measurement":"DY-only host gain absorbed by following wrapper; full residual -291.689 bits","source":"GDT060;GDT061","ceiling":"no reset meaning or content transition"},
 {"evidence_id":"E05","layer":"B3","status":"PROBABILISTIC_LINE_CLOSER_CONTENT_NEUTRALITY_UNKNOWN","measurement":"formal closer inherited; same-host context 12/20 positive, p .503","source":"GDT045;GDT052;GDT067","ceiling":"not punctuation or semantic emptiness"},
 {"evidence_id":"E06","layer":"PAGE_HOST_IDENTITY","status":"EXTERNAL_LOCALIZATION_NOT_SUPPORTED","measurement":"raw char3 beats PAGE_HOST locally; compiler/right/B3 match page-content signal","source":"GDT059","ceiling":"negative localization result"},
 {"evidence_id":"E07","layer":"HOST_BEHAVIOR_PROFILE","status":"POSTSELECTED_EXTERNAL_LEAD","measurement":"section-stratified profile +103.124 bits versus raw +71.172; positive 9/12 cells","source":"GDT068;GDT070","ceiling":"archived correlated outcomes only"},
 {"evidence_id":"E08","layer":"HOST_BEHAVIOR_CLASSES","status":"POSTSELECTED_CLASS_LEVEL_LEADS","measurement":"9/9 GDT069 directions survive every repeated exact-host deletion","source":"GDT069;GDT071","ceiling":"all-atlas adjusted p=1; prospective hypotheses only"},
 {"evidence_id":"E09","layer":"Q2","status":"CONTEXT_CONDITIONED_RECORD_ENTRY","measurement":"early initial display-t/Q2 versus later internal A1-Q2/display-ot bifurcation inherited","source":"GDT057;GDT058","ceiling":"no invariant q/t meaning"}]
 write(EVIDENCE,evidence,list(evidence[0]))
 predictions=[
 {"prediction_id":"HPR3_P01","future_target":"FRESH_NON_F84_ENCLOSURE_CONTRAST_PANEL","formal_predictor":"target-folio-excluded PAGE_HOST rate R=aiin >= 0.25","predicted_relation":"positive association with provenance-native REL_ENCLOSURE","capacity":"at least 30 mapped loci; >=3 positive and negative; >=2 positive and negative folios","primary_test":"folio-by-human-unit conditional effect > 0 after deleting d and ok","kill":"effect <=0 or sign reverses after any repeated exact-host deletion","status":"FROZEN_NOT_RUN"},
 {"prediction_id":"HPR3_P02","future_target":"FRESH_NON_F84_ATTACHMENT_CONTRAST_PANEL","formal_predictor":"target-folio-excluded PAGE_HOST wrapper rate W=sh >= 0.25","predicted_relation":"positive association with provenance-native REL_EXPLICIT_ATTACHMENT","capacity":"same as P01","primary_test":"folio-by-human-unit conditional effect > 0","kill":"effect <=0 or exact-host deletion reverses direction","status":"FROZEN_NOT_RUN"},
 {"prediction_id":"HPR3_P03","future_target":"FRESH_NON_F84_ENCLOSURE_CONTRAST_PANEL","formal_predictor":"target-folio-excluded PAGE_HOST O-frame rate >= 0.10","predicted_relation":"positive association with provenance-native REL_ENCLOSURE","capacity":"same as P01","primary_test":"effect >0 independently of P01","kill":"effect <=0 or d deletion reverses direction","status":"FROZEN_NOT_RUN"},
 {"prediction_id":"HPR3_P04","future_target":"FRESH_NON_F84_MULTI_AXIS_PANEL","formal_predictor":"fixed SELF+NEIGHBOR PAGE_HOST profile without position","predicted_relation":"beats RAW_CHAR3 for enclosure and array/group axes but not explicit attachment","capacity":"each axis mixed within section/Currier and at least five held-folio neighbours","primary_test":"held-folio codelength difference with unchanged GDT070 model","kill":"profile does not beat raw on enclosure/array or spuriously leads attachment","status":"FROZEN_NOT_RUN"}]
 write(PRED,predictions,list(predictions[0]))
 model={"schema":"GDT072_HPR3_BEHAVIORAL_CONTENT_CLASS_MODEL_V1","name":"HPR3_PAGE_HOST_BEHAVIORAL_RECORD_COMPILER","generator":{"page":"choose register-conditioned PAGE_HOST inventory and latent formal behavior classes","line":"Q2_ENTRY? FIELD (DY_CHECKPOINT FIELD)* B3_CLOSE?","field":"WRAPPER? INNER_D? POSITION_FRAME? PAGE_HOST RIGHT_FAMILY?","Q2_ENTRY":"context-conditioned early initial state; internal A1-Q2 is distinct","WRAPPER":"host-licensed renderer with cross-wrapper PAGE_HOST context preservation","POSITION_FRAME":"O/OT placement contrast; external content preservation weak/unknown","PAGE_HOST":"reusable formal key; exact identity external localization failed","HOST_BEHAVIOR_CLASS":"distribution over compiler and neighbor states; current best content-bearing candidate layer","RIGHT_FAMILY":"PAGE_HOST- and register-conditioned rendering that still modulates ecology","DY_CHECKPOINT":"predicts following wrapper ecology, not an independent host transition","B3_CLOSE":"probabilistic line closer; semantic neutrality unknown"},"candidate_classes":{"HCLASS_RAIIN_HIGH":{"definition":"target-folio-excluded R=aiin rate >=.25","external_lead":"REL_ENCLOSURE","evidence_state":"POSTSELECTED_ARCHIVED_HYPOTHESIS_ONLY"},"HCLASS_WSH_HIGH":{"definition":"target-folio-excluded W=sh rate >=.25","external_lead":"REL_EXPLICIT_ATTACHMENT","evidence_state":"POSTSELECTED_ARCHIVED_HYPOTHESIS_ONLY"},"HCLASS_FO_ACTIVE":{"definition":"target-folio-excluded O-frame rate >=.10","external_lead":"REL_ENCLOSURE","evidence_state":"POSTSELECTED_ARCHIVED_HYPOTHESIS_ONLY"}},"rejected_or_downgraded":{"PAGE_HOST_as_confirmed_semantic_layer":"GDT059 negative localization","DY_as_content_transition":"following wrapper absorbs host signal","B3_as_content_neutral_punctuation":"external ecology and low internal capacity","O_OT_as_confirmed_content_preserving_pair":"internal lead misses threshold; external exact capacity zero","RIGHT_FAMILY_as_empty_suffix":"register renderer supported, independent payload not excluded"},"f84r":"SEALED_NOT_TARGETED"};MODEL.write_text(json.dumps(model,indent=2,sort_keys=True)+"\n")
 status="HPR3_BEHAVIORAL_CONTENT_CLASS_MODEL_FROZEN_FOR_PROSPECTIVE_ACQUISITION";report=f"""# GDT072 — HPR3 behavioral content-class synthesis

## Outcome

**{status}**

The best current generator is a layered record compiler whose reusable
PAGE_HOST has a learned formal behavior class.  Exact PAGE_HOST identity is
not externally localized, but a target-folio-excluded distribution over
wrappers, frames, right families, DY/B3, and neighbouring compiler states is
the current strongest content-bearing candidate.  This is a sharper claim
than HPR2: content, if present, may live in **classes of host behavior**, not in
one literal core or one removable suffix.

The formal line model is:

    Q2_ENTRY? FIELD (DY_CHECKPOINT FIELD)* B3_CLOSE?
    FIELD := WRAPPER? INNER_D? POSITION_FRAME? PAGE_HOST RIGHT_FAMILY?

O/OT chiefly changes placement; RIGHT_FAMILY changes register-conditioned
rendering; DY predicts the next wrapper ecology; B3 closes probabilistically.
None is proven semantically empty.  Four prospective, non-f84 predictions are
frozen.  They test three explicit class thresholds and one fixed full-profile
comparison without retuning.

Archived annotation effects remain hypothesis-generation only, every adjusted
p-value remains as published, and no semantic class, role, gloss, word,
morpheme, POS, sound, language, plaintext, meaning, or translation is assigned.
f84r was not opened, retained, queried, joined, scored, or named as a target.
""";REPORT.write_text(report,encoding="utf-8")
 result={"schema":"GDT072_HPR3_BEHAVIORAL_CONTENT_CLASS_RESULT_V1","status":status,"evidence_rows":len(evidence),"frozen_predictions":len(predictions),"model_name":model["name"],"leading_theory":"PAGE_HOST behavior class is the best current content-bearing candidate inside a layered technical-record compiler; external association remains unconfirmed.","claim_ceiling":"Generative formal hypothesis and prospective class predictions only; no semantic class, role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation.","f84r":{"opened":False,"retained":False,"queried":False,"joined":False,"scored":False,"targeted":False},"inputs":{n:sha(ROOT/n)for n in INPUTS},"implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{EVIDENCE.name:sha(EVIDENCE),PRED.name:sha(PRED),MODEL.name:sha(MODEL)},"documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result["result_content_sha256"]=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"evidence":len(evidence),"predictions":len(predictions),"model":model["name"]},sort_keys=True))
if __name__=="__main__":main()
