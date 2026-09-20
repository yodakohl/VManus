"""Source-only explicit content decomposition; no Voynich inputs or old glosses."""
import json,hashlib
from pathlib import Path
D=Path(__file__).resolve().parent
src=D/'CENNINI_PROCESS_PRODUCT_SOURCE_20260920.json'
rows=[]
def f(c,subject,predicate,obj,mode='DIRECTIVE',scope='MAIN'):
    rows.append(dict(id='F'+str(len(rows)+1).zfill(3),clause='C'+str(c).zfill(2),scope=scope,modality=mode,subject=subject,predicate=predicate,object=obj))
def choice(c,subject,predicate,objects,scope):
    for obj in objects:f(c,subject,predicate,obj,'ALTERNATIVE',scope)
# C01: all introductory discourse, not another performed workshop event.
f(1,'SPEAKER','JUDGE_SUFFICIENT','PREVIOUS_COLORING_ACCOUNT','ASSERTION')
f(1,'SPEAKER','INTRODUCE','IMPRINTING_ART','DISCOURSE')
f(1,'IMPRINTING_ART','UTILITY','HIGH','ASSERTION')
f(1,'IMPRINTING_ART','BRINGS_CREDIT_TO','PRACTITIONER_IN_DRAWING','ASSERTION')
f(1,'IMPRINTING_ART','REPRESENTS','NATURAL_THINGS','ASSERTION')
f(1,'IMPRINTING_ART','CALLED','IMPRINTING','ASSERTION')
# C02: person choice and difficulty/shaving qualification.
f(2,'WORKER','DESIRES','FACE_LIKENESS','QUESTION','MODEL_SELECTION')
choice(2,'MODEL','SEX',['MAN','WOMAN'],'MODEL_SELECTION')
f(2,'MODEL','CONDITION','ANY','ALLOWANCE','MODEL_SELECTION')
choice(2,'MODEL','EXAMPLE',['YOUNG_PERSON','WOMAN','OLD_PERSON'],'MODEL_SELECTION')
f(2,'MODELING','DIFFICULT_OBJECT','BEARD','ASSERTION');f(2,'MODELING','DIFFICULT_OBJECT','HEAD_HAIR','ASSERTION')
f(2,'WORKER','SHAVE','MODEL_BEARD')
# C03: brush/oil and head covering.
f(3,'WORKER','ACQUIRE','ROSE_OIL');f(3,'ROSE_OIL','QUALITY','FRAGRANT','REQUIREMENT')
f(3,'WORKER','OIL','MODEL_FACE',scope='OILING_FACE');f(3,'OILING_FACE','MATERIAL','ROSE_OIL','REQUIREMENT')
f(3,'OILING_FACE','TOOL','BRUSH1','REQUIREMENT');f(3,'BRUSH1','MATERIAL','SQUIRREL_HAIR','REQUIREMENT');f(3,'BRUSH1','SIZE','SUBSTANTIAL','REQUIREMENT')
f(3,'WORKER','COVER','MODEL_HEAD',scope='HEAD_COVER');choice(3,'HEAD_COVER','TOOL',['CAP','HOOD'],'HEAD_COVER')
# C04: cloth dimensions and seam endpoints.
f(4,'WORKER','ACQUIRE','CLOTH1');f(4,'CLOTH1','WIDTH','ONE_SPAN','REQUIREMENT')
f(4,'CLOTH1','LENGTH','SHOULDER_TO_SHOULDER','REQUIREMENT')
f(4,'CLOTH1','ROUTE','HEAD_TOP_OVER_COVER','REQUIREMENT')
f(4,'WORKER','SEW','CLOTH1_EDGE',scope='SEAM1');f(4,'SEAM1','ATTACH_TO','HEAD_COVER','REQUIREMENT');f(4,'SEAM1','FROM','EAR1','REQUIREMENT');f(4,'SEAM1','TO','EAR2','REQUIREMENT')
# C05: cotton and same-cloth return routing; mirrored shoulder operation retained.
f(5,'WORKER','INSERT','COTTON',scope='EAR_PROTECTION');f(5,'EAR_PROTECTION','LOCATION','BOTH_EAR_OPENINGS','REQUIREMENT');f(5,'EAR_PROTECTION','AMOUNT','SMALL','REQUIREMENT')
f(5,'WORKER','DRAW','CLOTH1_EDGE');f(5,'WORKER','SEW','CLOTH1',scope='SEAM2');f(5,'SEAM2','START','COLLAR_BEGINNING','REQUIREMENT')
f(5,'SEAM2','TURN_AMOUNT','HALF','REQUIREMENT');f(5,'SEAM2','VIA','SHOULDER1_MIDDLE','REQUIREMENT');f(5,'SEAM2','RETURN_TO','FRONT_BUTTONS','REQUIREMENT')
f(5,'WORKER','REPEAT_METHOD','SEAM2',scope='SEAM3');f(5,'SEAM3','ON','SHOULDER2','REQUIREMENT');f(5,'SEAM3','END_AT','CLOTH1_BEGINNING','RESULT')
# C06: support and iron ring, no tubes yet.
f(6,'WORKER','RECLINE','MODEL');f(6,'MODEL','ON','CARPET','REQUIREMENT');choice(6,'CARPET','ON',['TABLE','BOARD'],'SUPPORT_CHOICE')
f(6,'WORKER','ACQUIRE','RING');f(6,'RING','MATERIAL','IRON','REQUIREMENT')
choice(6,'RING','WIDTH',['ONE_FINGER','TWO_FINGERS'],'RING_WIDTH');f(6,'RING','HAS','UPPER_TEETH','REQUIREMENT');f(6,'UPPER_TEETH','LIKE','SAW','COMPARISON')
f(6,'RING','SURROUNDS','MODEL_FACE','REQUIREMENT');choice(6,'RING','EXCESS_LENGTH_OVER_FACE',['TWO_FINGERS','THREE_FINGERS'],'RING_LENGTH')
# C07: ring assistant, cloth mounting and enclosure clearance.
f(7,'ASSISTANT','HOLD','RING');f(7,'RING','ABOVE','MODEL_FACE','REQUIREMENT');f(7,'RING','TOUCH','MODEL','PROHIBITION')
f(7,'WORKER','DRAW_AROUND','CLOTH1');f(7,'CLOTH1_FREE_EDGE','ON','RING_TEETH','REQUIREMENT');f(7,'CLOTH1_FREE_EDGE','IS','SEWN','PROHIBITION')
f(7,'WORKER','FIX','CLOTH1',scope='ENCLOSURE');f(7,'CLOTH1','BETWEEN','FACE_AND_RING','REQUIREMENT');f(7,'RING','OUTSIDE','CLOTH1','REQUIREMENT')
choice(7,'ENCLOSURE','FACE_GAP',['TWO_FINGERS','SLIGHTLY_LESS'],'GAP_CHOICE');f(7,'ENCLOSURE','GAP_ACCORDING_TO','DESIRED_PASTE_IMPRINT','PURPOSE')
# C08: prospective reference; not an additional actual pour.
f(8,'FIRST_FILL','DESTINATION','ENCLOSURE','PROSPECTIVE');f(8,'SPEAKER','EMPHASIZE','FIRST_FILL_DESTINATION','DISCOURSE')
# C09: tube maker, pair, material alternatives, geometry.
f(9,'WORKER','COMMISSION','GOLDSMITH');f(9,'GOLDSMITH','MAKE','TUBES');f(9,'TUBES','COUNT','TWO','REQUIREMENT')
choice(9,'TUBES','MATERIAL',['BRASS','SILVER'],'TUBE_MATERIAL');f(9,'TUBES','TOP_SHAPE','ROUND','REQUIREMENT');f(9,'TUBES','TOP_WIDER_THAN','BOTTOM','REQUIREMENT');f(9,'TUBES','LIKE','TRUMPET','COMPARISON')
f(9,'EACH_TUBE','LENGTH','NEAR_ONE_SPAN','REQUIREMENT');f(9,'EACH_TUBE','THICKNESS','ONE_FINGER','REQUIREMENT');f(9,'TUBES','WEIGHT','AS_LIGHT_AS_POSSIBLE','REQUIREMENT')
# C10: fitting, perforation and lower connection.
f(10,'TUBE_BOTTOMS','SHAPE_LIKE','NOSTRIL_OPENINGS','REQUIREMENT');f(10,'TUBE_BOTTOMS','SIZE','SLIGHTLY_SMALLER_THAN_OPENINGS','REQUIREMENT');f(10,'TUBES','FIT','NOSTRILS','REQUIREMENT')
f(10,'INSERTION','EXPAND','NOSE','PROHIBITION');f(10,'TUBES_UPPER_HALF','HAS','HOLES','REQUIREMENT');f(10,'HOLES','SIZE','SMALL','REQUIREMENT');f(10,'HOLES','FREQUENCY','DENSE','REQUIREMENT')
f(10,'WORKER','JOIN','TUBES_BOTTOMS');f(10,'TUBES_BOTTOM_JOIN','ALLOW_SPACE','FLESH_BETWEEN_NOSTRILS','REQUIREMENT')
# C11: actor identity explicitly MODEL, not new MODEL_SELF.
f(11,'WORKER','RECLINE','MODEL');f(11,'WORKER','INSERT','TUBES',scope='TUBE_PLACEMENT');f(11,'TUBE_PLACEMENT','DESTINATION','MODEL_NOSTRILS','REQUIREMENT');f(11,'MODEL','HOLD_BY_HAND','TUBES')
# C12: first preparation; small part taken later need not equal whole batch.
f(12,'WORKER','PREPARE','BATCH1',scope='MIX1');f(12,'BATCH1','MATERIAL_CLASS','GYPSUM','REQUIREMENT','MIX1');choice(12,'BATCH1','GYPSUM_ORIGIN',['BOLOGNA','VOLTERRA'],'GYPSUM_ORIGIN')
for prop in ['COOKED','FRESH','SIFTED']:f(12,'BATCH1_GYPSUM','QUALITY',prop,'REQUIREMENT','MIX1')
f(12,'MIX1','MEDIUM','WATER1','REQUIREMENT');f(12,'WATER1','TEMPERATURE','WARM','REQUIREMENT');f(12,'WATER1','IN','BASIN1','REQUIREMENT')
f(12,'WORKER','ADD_GYPSUM_TO','WATER1',scope='MIX1');f(12,'MIX1','SPEED','QUICK','REQUIREMENT');f(12,'BATCH1','SETS','QUICKLY','STATED_REASON','MIX1')
f(12,'BATCH1','TOO','FLUID','PROHIBITION','MIX1');f(12,'BATCH1','TOO','STIFF','PROHIBITION','MIX1')
# C13: actual instructed fill plus natural body posture, eyes last.
f(13,'WORKER','ACQUIRE','GLASS');f(13,'WORKER','TAKE_SOME','BATCH1',scope='POUR1');f(13,'POUR1','TOOL','GLASS','REQUIREMENT');f(13,'POUR1','DESTINATION','ENCLOSURE','REQUIREMENT')
f(13,'POUR1','DISTRIBUTION','EVEN','REQUIREMENT');f(13,'POUR1','COVER_LAST','MODEL_EYES','REQUIREMENT');f(13,'WORKER','CAUSE','MODEL_CLOSING',scope='CLOSING');f(13,'MODEL','CLOSE','MOUTH',scope='CLOSING');f(13,'MODEL','CLOSE','EYES',scope='CLOSING')
f(13,'CLOSING','FORCE','EXCESSIVE','PROHIBITION');f(13,'CLOSING','LIKE','SLEEP','COMPARISON')
# C14: level and first setting.
f(14,'POUR1','LEVEL_ABOVE_NOSE','ONE_FINGER','REQUIREMENT');f(14,'WORKER','REST','POURED1',scope='SET1');f(14,'SET1','DURATION','SHORT','REQUIREMENT');f(14,'SET1','UNTIL','SET_ENOUGH','REQUIREMENT')
# C15: explicit retroactive qualification of MIX1, not new WATER2 after first setting.
f(15,'SPEAKER','REMIND','MIX1_MEDIUM','DISCOURSE');f(15,'MODEL','STATUS','HIGH','CONDITION','HIGH_STATUS_MIX1')
for ex in ['LORD','KING','POPE','EMPEROR']:f(15,'HIGH_STATUS','EXAMPLE',ex,'EXAMPLE','HIGH_STATUS_MIX1')
f(15,'WATER1','KIND','ROSE_WATER','REQUIREMENT','HIGH_STATUS_MIX1');f(15,'WATER1','TEMPERATURE','WARM','REQUIREMENT','HIGH_STATUS_MIX1')
f(15,'MODEL','STATUS','OTHER','CONDITION','OTHER_STATUS_MIX1');choice(15,'WATER1','KIND',['SPRING_WATER','WELL_WATER','RIVER_WATER'],'OTHER_STATUS_MIX1');f(15,'WATER1','TEMPERATURE','WARM','SUFFICIENCY','OTHER_STATUS_MIX1')
# C16: dryness gate, cut cloth and withdraw same tubes.
f(16,'POURED1','STATE','DRY','CONDITION','RELEASE1');choice(16,'RELEASE1','CUTTING_TOOL',['PENKNIFE','KNIFE','SCISSORS'],'RELEASE1_TOOL')
f(16,'WORKER','CUT_AROUND','CLOTH1',scope='RELEASE1');f(16,'RELEASE1','MANNER','GENTLE','REQUIREMENT');f(16,'WORKER','REMOVE_FROM_NOSE','TUBES',scope='RELEASE1');f(16,'TUBE_REMOVAL','MANNER','GENTLE','REQUIREMENT')
# C17: working parse, source uncertainty retained in metadata instead of invented text symbols.
f(17,'WORKER','CAUSE_RISE','MODEL',scope='RELEASE1');choice(17,'MODEL','POSTURE',['SEATED','STANDING'],'RELEASE1_POSTURE')
f(17,'MODEL','SUPPORT_BY_HAND','MASK1','DIRECTIVE','RELEASE1');f(17,'MODEL_FACE','FREE_FROM','MASK1','DIRECTIVE','RELEASE1');f(17,'FACE_RELEASE','MANNER','GENTLE','REQUIREMENT');f(17,'MASK1','MADE_FROM','POURED1','REFERENCE')
# C18: unchanged first mask preserved.
f(18,'WORKER','PUT_AWAY','MASK1');f(18,'WORKER','PRESERVE','MASK1');f(18,'PRESERVING','MANNER','CAREFUL','REQUIREMENT')
# C19: new band, old mold.
f(19,'WORKER','ACQUIRE','BAND2');f(19,'BAND2','KIND','CHILD_BAND','REQUIREMENT');f(19,'WORKER','SURROUND','MASK1',scope='BANDING2');f(19,'BANDING2','TOOL','BAND2','REQUIREMENT');f(19,'BAND2','EXCEEDS_MOLD_EDGE','TWO_FINGERS','REQUIREMENT')
# C20: new oil choice/cavity, source faulty wording preserved as explicit purpose assumption.
f(20,'WORKER','ACQUIRE','BRUSH2');f(20,'BRUSH2','MATERIAL','SQUIRREL_HAIR','REQUIREMENT');f(20,'BRUSH2','SIZE','THICK','REQUIREMENT')
f(20,'OIL2','KIND','ANY_CHOSEN','ALLOWANCE');f(20,'WORKER','OIL','MASK1_CAVITY',scope='OILING2');f(20,'OILING2','MATERIAL','OIL2','REQUIREMENT');f(20,'OILING2','TOOL','BRUSH2','REQUIREMENT');f(20,'OILING2','MANNER','CAREFUL','REQUIREMENT');f(20,'OILING2','AVOID','DAMAGE_TO_WORK','PURPOSE')
# C21: call earlier METHOD, new batch, optional improvement.
f(21,'WORKER','PREPARE','BATCH2',scope='MIX2');f(21,'MIX2','REUSE_METHOD','MIX1','REFERENCE');f(21,'BATCH2','MATERIAL_CLASS','GYPSUM','REFERENCE')
f(21,'WORKER','ADD','BRICK_POWDER','OPTION','BRICK_OPTION');f(21,'BRICK_POWDER','STATE','CRUSHED','REQUIREMENT','BRICK_OPTION');f(21,'BRICK_OPTION','INTO','BATCH2','REQUIREMENT');f(21,'BRICK_OPTION','IMPROVES','BATCH2','SOURCE_CLAIM');f(21,'BRICK_OPTION','IMPROVEMENT_DEGREE','HIGH','SOURCE_CLAIM')
# C22: second pour and simultaneous support.
f(22,'WORKER','TAKE_SOME','BATCH2',scope='POUR2');f(22,'POUR2','TOOL','GLASS','REQUIREMENT');f(22,'POUR2','TOOL','BOWL','REQUIREMENT');f(22,'POUR2','DESTINATION','MASK1','REQUIREMENT');f(22,'WORKER','HOLD','MASK1',scope='SUPPORT2');f(22,'MASK1','ON','BENCH','REQUIREMENT','SUPPORT2');f(22,'SUPPORT2','WHILE','POUR2','TEMPORAL')
# C23: action while pouring, analogy not performed wax casting.
f(23,'WORKER','TAP','BENCH',scope='TAP2');f(23,'TAP2','WHILE','POUR2','TEMPORAL');f(23,'TAP2','HAND','OTHER_HAND','REQUIREMENT');f(23,'TAP2','MANNER','GENTLE','REQUIREMENT')
f(23,'TAP2','ENABLE','FILL_EVERYWHERE','PURPOSE');f(23,'FILL_EVERYWHERE','MATERIAL','POURED2','REFERENCE');f(23,'FILL_EVERYWHERE','DESTINATION','ALL_MASK1_CAVITIES','PURPOSE');f(23,'FILL_EVERYWHERE','LIKE','WAX_IN_SEAL','COMPARISON');f(23,'TAP2','AVOID','BUBBLES','PURPOSE');f(23,'TAP2','AVOID','BLISTERS','PURPOSE')
# C24: filled-state gate and duration bounds as stated alternative interval.
f(24,'MASK1','STATE','FILLED','CONDITION','REST2');f(24,'WORKER','REST','MASK1',scope='REST2');f(24,'REST2','DURATION','HALF_DAY','DIRECTIVE');f(24,'REST2','MAX_DURATION','ONE_DAY','ALLOWANCE')
# C25: destroy outer first mold, protect distinct inner representation.
f(25,'WORKER','ACQUIRE','SMALL_HAMMER');f(25,'WORKER','TAP_AND_BREAK','OUTER_SHELL',scope='BREAK1');f(25,'BREAK1','TOOL','SMALL_HAMMER','REQUIREMENT');f(25,'BREAK1','MANNER','GENTLE','REQUIREMENT')
f(25,'OUTER_SHELL','IDENTITY','MASK1','REFERENCE');f(25,'BREAK1','BREAK','CAST2_NOSE','PROHIBITION');f(25,'BREAK1','BREAK','ANY_CAST2_PART','PROHIBITION')
# C26: purpose and explicit BEFORE, not a discovered difficulty conditional.
f(26,'WORKER','ACQUIRE','SAW_PIECE',scope='SAW1');f(26,'WORKER','SAW','MASK1_EXTERIOR',scope='SAW1');f(26,'SAW1','AT','SEVERAL_PLACES','REQUIREMENT');f(26,'SAW1','BEFORE','POUR2','TEMPORAL')
f(26,'SAW1','MAKE_EASIER','BREAK1','PURPOSE');f(26,'SAW1','CUT_THROUGH','MASK1','PROHIBITION');f(26,'CUT_THROUGH_MASK1','EFFECT','HARMFUL','SOURCE_CLAIM');f(26,'MASK1','STATE','FILLED','CONDITION','SAW1_EXPECTED_EFFECT')
f(26,'BREAK1','REQUIRES','SMALL_BLOW','EXPECTED_EFFECT','SAW1_EXPECTED_EFFECT');f(26,'BREAK1','MANNER','SKILFUL','EXPECTED_EFFECT','SAW1_EXPECTED_EFFECT')
# C27: result naming and representation, not physical person identity.
f(27,'WORKER','OBTAINS','CAST2','RESULT');
for name in ['EFFIGY','LIKENESS','IMPRINT']:f(27,'CAST2','CALLED',name,'RESULT')
f(27,'CAST2','REPRESENTS','MODEL','RESULT');f(27,'CAST2','APPLICATION','EACH_GREAT_LORD','SOURCE_CLAIM')
# C28: incomplete downstream possibility retains explicit first-form reference.
f(28,'METAL_CASTING','BASIS','FIRST_FORM','REFERENCE');f(28,'WORKER','HAS','FIRST_FORM','CONDITION','METAL_CASTING');f(28,'SPEAKER','INFORM','METAL_POSSIBILITY','DISCOURSE');f(28,'WORKER','CAN_COMMISSION','METAL_CASTING','POSSIBILITY');f(28,'METAL_CASTING','REPRESENTATION','SAID_IMPRINT','REFERENCE')
choice(28,'METAL_CASTING','MATERIAL',['COPPER','METAL','BRONZE','GOLD','SILVER','LEAD','ANY_DESIRED_METAL'],'METAL_OPTIONS')
# C29: capability requirement; no invented foundry steps.
f(29,'WORKER','ENSURE_AVAILABLE','FOUNDER_MASTERS');f(29,'FOUNDER_MASTERS','SKILL','SUFFICIENT','REQUIREMENT');f(29,'FOUNDER_MASTERS','UNDERSTAND','MELTING','REQUIREMENT');f(29,'FOUNDER_MASTERS','UNDERSTAND','CASTING','REQUIREMENT')

out=dict(schema='cennini_source_fact_records.v1',status='ROOT_WORKING_CONTENT_ACCOUNT_SOURCE_UNCERTAINTIES_RETAINED',source_packet=src.name,source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),fields=['scope','modality','subject','predicate','object'],records=rows,source_bins={c['id']:c['content'] for c in json.loads(src.read_text())['full_content_inventory']},uncertainties=[dict(clause='C17',detail='MODEL supports the compound is an explicit working parse, compatible with1859but not a unique resolution of corrupt1821wording; no reader certainty asserted.'),dict(clause='C20',detail='Purpose avoid work failure follows context and1859guasto, while1821questo niente is transmitted corruptly; explicit content assumption.'),dict(clause='C28',detail='FIRST_FORM reference is retained as a designation, without asserting a unique physical antecedent or present availability after BREAK1.')],identity_policy='MODEL_SELF=MODEL; different batches/portions/molds/results are not silently identified. MASK1 is the first outer shell; CAST2 survives. No actual breath-function claim from editorial headings.',epistemic_policy='All records preserve discourse modality; directives and conditional/possible claims are not observed executions. Compound scalar/relational values such as ONE_FINGER are explicit finite semantic values, not a claim to morphemic indivisibility. C01–C29 are provenance bins, not code terminals.',no_voynich_inputs=True)
out['entity_definitions']={'WORKER':'instructional addressee, distinct role from author/speaker and sitter','BATCH1':'prepared mixed first gypsum batch; BATCH1_GYPSUM is its ingredient, not the batch itself','POURED1':'unspecified portion of BATCH1 used around the face','MASK1':'first hardened form resulting from POURED1; later outer shell','BATCH2':'new mixed gypsum batch made by reference to MIX1 method','POURED2':'portion of BATCH2 entering MASK1','CAST2':'analytic identifier for the second formed representation protected during BREAK1 and subsequently called effigy/likeness/imprint; not an additional source-named object','SPEAKER':'source discourse speaker; not automatically the worker','FIRST_FORM':'source designation in ambiguous later metal possibility; physical antecedent deliberately not equated by this fact writer'}
out['uncertainties'].append(dict(clause='C06',detail='Carpet on table/board is the selected support layering; treating carpet/table/board as three alternatives is another reading of the punctuation, not settled by the source.'))
assert set(x['clause'] for x in rows)==set(out['source_bins'])
(D/'CENNINI_SOURCE_FACTS_20260920.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
print(json.dumps(dict(status=out['status'],records=len(rows),values=len(set(x[k] for x in rows for k in out['fields'])),clause_bins=len(out['source_bins']))))
