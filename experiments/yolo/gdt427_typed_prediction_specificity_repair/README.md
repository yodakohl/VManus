# GDT427 — typed prediction specificity repair

GDT426 compressed the nine remaining page-local action cards, but its four
classes occupied every possible transition and therefore could not reject a
single unseen pair. GDT427 repairs that defect by comparing seven small class
partitions against both positive page-leaveout pairs and genuinely absent
ordered pairs.

The selected five-class gate keeps seven of the nine cards amber while leaving
`R>T` and `R<-EE` honestly local. See `REPORT.md`, `METHOD.md`, and the compact
tables in `artifacts/`.
