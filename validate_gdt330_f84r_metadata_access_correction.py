#!/usr/bin/env python3
"""Validate fixed GDT330 disclosure bytes without opening any source table."""
import hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent;P=R/'gdt330_result.json';OUT=R/'gdt330_validation.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def can(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def main():
 v=json.loads(P.read_text());s=v.pop('content_sha256');checks={'content':s==can(v),'status':v['status']=='F84R_PUBLIC_METADATA_ROW_TRANSIENTLY_PARSED_NO_VALUE_DISPLAYED_OR_USED','parse_disclosed':v['access']['global_page_annotation_tables_iterated_before_whitelist'] and v['access']['f84r_public_metadata_row_transiently_materialized'],'no_value_display':not v['access']['f84r_value_printed_or_manually_inspected'],'no_science_use':not v['access']['f84r_row_retained_selected_joined_scored_or_written'],'no_formal_access':not v['access']['f84r_transcription_family_page_host_grammar_or_formal_result_opened'],'prior_results_clean':not v['access']['gdt328_gdt329_scientific_inputs_contain_f84'],'document_hash':all(sha(R/n)==h for n,h in v['documents'].items()),'implementation_hash':all(sha(R/n)==h for n,h in v['implementation'].items()),'prohibition':'NO_FURTHER_F84R_ACCESS' in v['continuing_prohibition']};assert all(checks.values()),checks;q={'schema':'GDT330_VALIDATION_V1','status':'PASS','scope':'FIXED_DISCLOSURE_CONTENT_DOCUMENT_IMPLEMENTATION_NO_SOURCE_TABLE_OPENED','checks_passed':len(checks),'result_sha256':sha(P)};q['content_sha256']=can(q);OUT.write_text(json.dumps(q,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(checks)},sort_keys=True))
if __name__=='__main__':main()
