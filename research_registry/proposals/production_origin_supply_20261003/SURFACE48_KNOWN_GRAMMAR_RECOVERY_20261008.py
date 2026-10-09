"""Compact recovery of the already executed845/847literal48-cell result."""
import hashlib,itertools,json
from pathlib import Path
R=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
SOURCE='experiments/yolo/gdt845_extended_form_grid_discovery/artifacts/CELLS.json'
def main():
 cells=json.loads((R/SOURCE).read_text());kept=sorted((x for x in cells if x['e']<=1),key=lambda x:x['word'])
 expected={w+h+m+('e' if e else '')+('d' if d else '')+'y' for w,h,m,e,d in itertools.product(['','o','qo'],['k','t'],['ch','sh'],[0,1],[0,1])}
 assert len(expected)==len(kept)==48 and {x['word'] for x in kept}==expected
 summary={r:{'occupied_cells':sum(x['counts'][r]>0 for x in kept),'raw_occurrences':sum(x['counts'][r] for x in kept)} for r in ['ZL3b','IT2a','RF1b']}
 assert summary=={'ZL3b':{'occupied_cells':48,'raw_occurrences':816},'IT2a':{'occupied_cells':48,'raw_occurrences':836},'RF1b':{'occupied_cells':48,'raw_occurrences':655}}
 assert sum(x['shared_locus_multiplicity']>0 for x in kept)==48 and sum(x['shared_locus_multiplicity'] for x in kept)==605
 out={'status':'OLD_LITERAL_SURFACE_LATTICE_RETAINED','scope':'Recovery of previously executed845/847results, no new native census or held prediction','source':SOURCE,'source_sha256':hashlib.sha256((R/SOURCE).read_bytes()).hexdigest(),'pattern':'(?:qo|o)?[kt](?:ch|sh)e?d?y','cells':kept,'summary':summary,'shared_locus_cells':48,'shared_locus_minimum_sum':605,'old_count_reconciliation':'829cleanedZL=816literalraw+10bracketcollapses+2braceannotationremovals+1inline_metadataremoval(847).','limits':['Surface generator, not mental construction order or translated morphology','All48e0/1cells occupied does not forbid e2 or other forms','Common-locus minimum is not general exact group alignment','Readers are alternative observations, not independent replications','Old thermal/moisture/e/d glosses not adopted']}
 (B/'SURFACE48_KNOWN_GRAMMAR_RESULT_20261008.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(summary));print('48sharedlocuscells;605minimumsum; no newcensus')
if __name__=='__main__':main()
