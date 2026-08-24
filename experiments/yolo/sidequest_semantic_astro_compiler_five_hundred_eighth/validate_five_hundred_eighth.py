#!/usr/bin/env python3
import csv,json
from pathlib import Path
H=Path(__file__).resolve().parent
def r(n):
 with (H/n).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def main():
 g=r('FIVE_HUNDRED_EIGHTH_395_ASTRO_GROUP_COMPILER_TRACES.tsv');l=r('FIVE_HUNDRED_EIGHTH_142_ASTRO_LOCUS_LOOPS.tsv');p=r('FIVE_HUNDRED_EIGHTH_THREE_ASTRO_PAGE_WORKFLOWS.tsv');u=r('FIVE_HUNDRED_EIGHTH_776_TEN_PAGE_COMPILER_LEDGER.tsv');m=r('FIVE_HUNDRED_EIGHTH_124_ITEM_TEN_PAGE_MANUAL.tsv');pd={x['page']:x for x in p}
 checks={'groups395':len(g)==395 and len({x['group_serial'] for x in g})==395,'loci142':len(l)==142 and len({x['locus'] for x in l})==142,'group_sum395':sum(int(x['group_count']) for x in l)==395,'namespaces13':len({x['namespace_id'] for x in l})==13,'pages3':len(p)==3,'f67_74_190':(pd['f67r2']['loci'],pd['f67r2']['groups'])==('74','190'),'f68_37_65':(pd['f68r1']['loci'],pd['f68r1']['groups'])==('37','65'),'f69_31_140':(pd['f69v']['loci'],pd['f69v']['groups'])==('31','140'),'unified776':len(u)==776 and sum(x['domain']=='PROSE' for x in u)==381 and sum(x['domain']=='ASTRO' for x in u)==395,'no_orientation':all(x['orientation']=='NONE' for x in g+l),'no_join':all(x['crosspage_join']=='NONE' for x in g) and all(x['cross_instrument_join']=='NONE' for x in l),'no_prose_import':all(x['prose_primitive_import']=='NONE' for x in g),'manual124':len(m)==124,'namespace_rows13':sum(x['layer']=='L2_ASTRO_NAMESPACE' for x in m)==13,'old_astro_owner_rows_removed':not any(x['layer']=='L2_OWNER_CLASS' and x['scope']=='ASTRO' for x in m),'seal_absent':all(not x['page'].lower().startswith('f84') for x in u)}
 z={'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks};(H/'FIVE_HUNDRED_EIGHTH_VALIDATION.json').write_text(json.dumps(z,indent=2)+'\n');[print(f"{k}\t{'PASS' if v else 'FAIL'}") for k,v in checks.items()]
 if not all(checks.values()):raise SystemExit(1)
if __name__=='__main__':main()
