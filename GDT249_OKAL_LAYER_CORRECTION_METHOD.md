# GDT249 — `okal` layer correction method

GDT248 compared each exact GDT247 source-group surface directly with the
GDT165 PAGE_HOST manifest. This is valid for `okaly` and `olky`, whose HPR2
hosts preserve the whole group, but not for `okal`.

This correction reconstructs the label parse from the f84-free GDT080 BFE
join and the prose parse from the f84-free GDT241 f82r field inventory. Both
independently give:

```text
source group okal = PAGE_HOST ok + RIGHT_FAMILY al
```

It then replaces the invalid global PAGE_HOST `okal` lookup with the published
PAGE_HOST `ok` distribution. No new model or semantic search is run. No f84
input was read, retained, joined, or scored and no new f84 access occurred.
