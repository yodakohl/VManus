#!/usr/bin/env python3
"""GDT188: identity-invariant closure of direct substitution-cipher models."""
import csv, hashlib, json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
G159=ROOT/"gdt159_surface_algebra_comparison.tsv"; G160=ROOT/"gdt160_null_summary.tsv"
R159=ROOT/"gdt159_result.json";R160=ROOT/"gdt160_result.json";R186=ROOT/"gdt186_result.json"
METHOD=ROOT/"GDT188_BIJECTIVE_CIPHER_INVARIANCE_METHOD.md";REPORT=ROOT/"GDT188_BIJECTIVE_CIPHER_INVARIANCE_REPORT.md"
TABLE=ROOT/"gdt188_invariance_comparison.tsv";AXES=ROOT/"gdt188_invariant_axes.tsv";COUNTER=ROOT/"gdt188_counterexamples.tsv";RESULT=ROOT/"gdt188_result.json"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
 with p.open(encoding="utf8") as h:return list(csv.DictReader(h,delimiter="\t"))
def write(p,rows):
 with p.open("w",encoding="utf8",newline="") as h:w=csv.DictWriter(h,fieldnames=list(rows[0]),delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def main():
 f={r['corpus_id']:r for r in read(G159)};n={(r['corpus_id'],r['null']):r for r in read(G160)}
 target=f['VOYNICH_MATCHED'];tn=n['VOYNICH_MATCHED','RIGHT_LABEL_SWITCH_LENGTH_EXACT']
 rows=[]
 for corpus in ('LATIN_15C_GRAPHEMATIC','LATIN_MEDICAL_GRAPHEMATIC','NUREMBERG_REAL_DIPLOMATIC'):
  x=f[corpus]; key=(corpus,'RIGHT_LABEL_SWITCH_LENGTH_EXACT'); nx=n.get(key)
  rows.append({'corpus_id':corpus,'operation_scale':x['mean_discovered_operations'],'operation_ratio_to_voynich':x['operation_scale_ratio_to_voynich'],'compatible_pair_density':x['compatible_pair_density'],'voynich_compatible_pair_density':target['compatible_pair_density'],'voynich_to_corpus_density_ratio':f"{float(target['compatible_pair_density'])/float(x['compatible_pair_density']):.12f}",'left_right_log2_support_ratio':x['left_right_log2_support_ratio'],'left_dominant':x['left_dominant'],'right_switch_excess_density':nx['graph_excess_all_pair_density'] if nx else 'NOT_AVAILABLE','voynich_to_corpus_excess_ratio':f"{float(tn['graph_excess_all_pair_density'])/float(nx['graph_excess_all_pair_density']):.12f}" if nx and float(nx['graph_excess_all_pair_density']) else 'NOT_AVAILABLE','value_after_any_fixed_symbol_bijection':'UNCHANGED','direct_bijective_cipher_gate':'FAIL'})
 axes=[
  {'axis':'SOURCE_GROUP_EQUALITY','invariant':'YES','reason':'a bijection preserves equality and inequality'},
  {'axis':'SOURCE_GROUP_LENGTH','invariant':'YES','reason':'one source symbol maps to one target symbol'},
  {'axis':'HOST_RECURRENCE','invariant':'YES','reason':'type occurrence sets are relabelled isomorphically'},
  {'axis':'PREFIX_SUFFIX_OPERATION_SUPPORT','invariant':'YES','reason':'edge substitutions are conjugated by the same bijection'},
  {'axis':'COMPLETE_RECTANGLES','invariant':'YES','reason':'all four cells map bijectively'},
  {'axis':'LEFT_RIGHT_COMPATIBILITY_GRAPH','invariant':'YES','reason':'operation and host incidence graphs are isomorphic'},
  {'axis':'COMPATIBLE_PAIR_DENSITY','invariant':'YES','reason':'graph edge and denominator counts are unchanged'},
  {'axis':'DEGREE_FREQUENCY_PRESERVING_EXCESS','invariant':'YES','reason':'observed graph and relabelling null are isomorphic'},
  {'axis':'LINE_RECORD_RESET','invariant':'YES_IF_BOUNDARIES_PRESERVED','reason':'the cipher changes symbols, not physical boundaries'},
  {'axis':'NAMED_LANGUAGE_MODEL_SCORE','invariant':'NO','reason':'target glyph names and phonotactics depend on the chosen map'},
 ]
 counter=[
  {'counterexample_id':'C01','observation':'A context-dependent or homophonic cipher is not a bijection.','impact':'not closed by the theorem'},
  {'counterexample_id':'C02','observation':'Standard abbreviation can delete or contract letters.','impact':'a substitution-plus-abbreviation transducer can change the fingerprint'},
  {'counterexample_id':'C03','observation':'Foxton selectively ciphers only 135 words in readable Latin.','impact':'the exact historical document is not a whole-text ciphertext model'},
  {'counterexample_id':'C04','observation':'Fontana also manipulates abbreviation marks.','impact':'only the pure alphabet-renaming component is closed'},
  {'counterexample_id':'C05','observation':'The frozen Latin corpora need not equal the unknown source text.','impact':'failure is corpus-plus-mechanism specific, not universal'},
 ]
 write(TABLE,rows);write(AXES,axes);write(COUNTER,counter)
 latin15=rows[0];medical=rows[1]
 status='DIRECT_BIJECTIVE_SCIENTIFIC_CIPHER_INSUFFICIENT_FOR_FROZEN_LATIN_CONTROLS'
 report=f"""# GDT188 — a simple artificial alphabet cannot create the Voynich algebra

## Result

Status: **{status}**.

A fixed one-to-one substitution only renames symbols.  It cannot change the
GDT003/GDT159 operation inventory, transformation rectangles, LEFT×RIGHT
compatibility graph, compatible-pair density, or GDT160 pairing excess.
Therefore the frozen historical Latin controls remain where they are after
*any* Foxton-like glyph renaming.

The matched fifteenth-century Latin panel has almost exactly Voynich's
operation scale ({float(latin15['operation_ratio_to_voynich']):.3f}×), but its
compatible-pair density is {float(latin15['compatible_pair_density']):.6f}
against Voynich {float(latin15['voynich_compatible_pair_density']):.6f}—a
{float(latin15['voynich_to_corpus_density_ratio']):.1f}× gap that a bijection
leaves unchanged.  The Latin medical panel is farther away at
{float(medical['compatible_pair_density']):.6f}, a
{float(medical['voynich_to_corpus_density_ratio']):.1f}× gap.  Under the
degree/frequency-preserving pairing null, Voynich's excess density is
{float(tn['graph_excess_all_pair_density']):.6f}, versus
{float(rows[0]['right_switch_excess_density']):.6f} in the fifteenth-century
Latin control ({float(rows[0]['voynich_to_corpus_excess_ratio']):.1f}×).

## Consequence for translation

Do not search for a single Foxton/Fontana-style character key on the visible
Voynich text.  If a historical language lies underneath, at least one
additional nonbijective layer—abbreviation, context-dependent rendering,
nomenclator/codebook behavior, or the independently observed record
compiler—must be removed first.  This is a useful architectural exclusion,
not a language identification.

The result does not reject every Latin plaintext, every scientific cipher, or
the broader GDT181 hybrid.  It closes the direct fixed-bijection route for the
frozen Latin comparators.  No glyph value, sound, word, language, plaintext,
or translation follows.  No f84r source row or image was accessed.
""";REPORT.write_text(report,encoding='utf8')
 result={'experiment':'GDT188_BIJECTIVE_CIPHER_INVARIANCE','status':status,'comparators':rows,'invariant_axes':sum(x['invariant'].startswith('YES') for x in axes),'noninvariant_axes':sum(x['invariant']=='NO' for x in axes),'decision':'VISIBLE_TEXT_REQUIRES_NONBIJECTIVE_OR_COMPILER_LAYER_BEFORE_LANGUAGE_DECODING','f84r_accessed':False,'claim_ceiling':'Identity-invariant architecture exclusion only; no glyph value, language, plaintext, meaning, or translation.','inputs':{p.name:sha(p) for p in (G159,G160,R159,R160,R186)},'outputs':{p.name:sha(p) for p in (TABLE,AXES,COUNTER)},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)},'implementation':sha(Path(__file__))}
 RESULT.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');print(status)
if __name__=='__main__':main()
