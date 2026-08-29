# GDT620 Stage-B result

Status: `TEN_SOURCE_PAGES_ACQUIRED__SOURCE_READING_UNOPENED__TARGET_UNOPENED`

The exact GDT620 deck ran once from public registration commit
`61a253ce2756ad06a6c69c620e702500f5e640ef`. All ten requests returned HTTP
200 from their literal URL with zero redirects. The acquirer received
13,178,909 body bytes, fully decoded ten one-frame JPEGs, and reproduced every
registered stored-pixel dimension. The complete public-safe result is
`artifacts/STAGE_B_RESULT.json`, SHA-256
`f14976f54fd4ea0424ada9f23d19e7f02424beff739f5b4943dd3b0329ae378e`.

| Seq. | Candidate | Witness | Bytes | Pixels | Raw SHA-256 |
|---:|---|---|---:|---:|---|
| 1 | DEV01 Balsamus | Clm 28531 | 654,233 | 1707x2466 | `82b476a028ad94ba7392520a4cba527c9dc521a577207bbec5842d0f7e266c50` |
| 2 | DEV02 Cerfolium | Clm 28531 | 590,262 | 1707x2581 | `e0c56b10b19e823c7b0247881d1cf27a1302cced0bd432956b98c47aab78746f` |
| 3 | DEV03 Liquiritia | Clm 28531 | 616,531 | 1707x2562 | `4d87c0f033236b88abbb0ce6a5fe24a3664d63660080e15e0763642d9444aee0` |
| 4 | DEV04 Cucurbita | Clm 28531 | 562,974 | 1707x2591 | `f5a112fd194f45db72518e1a146f05bd2eec239e346a1b137cba7f1eab24e035` |
| 5 | DEV05 Diptamus | Clm 28531 | 481,123 | 1707x2581 | `808ff7b43c074ee0e67770cf51d7a38f683254c1a11883bf799bc9deeee1f4a8` |
| 6 | DEV01 Balsamus | Latin 6823 | 2,399,224 | 3302x4581 | `a12f51056ad4e18ae4ed40739987dae3924618787ebbaac1c481ac0b2976ef2a` |
| 7 | DEV02 Cerfolium | Latin 6823 | 1,815,181 | 3451x4553 | `470aca9b7d6cdfd9aa3cb321d165f86b01e15f8de8193e50d8a9dbb722c71b11` |
| 8 | DEV03 Liquiritia | Latin 6823 | 2,242,239 | 3284x4557 | `01397d43449619b004fcee6fdacc3e236dfb3523f689ef0c51d0ff550f30b6b4` |
| 9 | DEV04 Cucurbita | Latin 6823 | 1,896,600 | 3333x4388 | `055dd108bbec73ca7a8b80f9cfa3c467b3ca560ef9650015f05aaffd2e28ca8d` |
| 10 | DEV05 Diptamus | Latin 6823 | 1,920,542 | 3346x4574 | `8091ac2ac1939ac11e88d314501c4ef68d0015e6c38b89ad08a07a30521e0a4a` |

Requests 2–10 each received the registered fresh four-second pause. Their
observed UTC wall-clock completion-to-start deltas range from
4.0105509757995605 to 4.0349719524383545 seconds. The first request began at
07:38:48.044624 UTC and the tenth response completed at 07:39:40.936547 UTC.
The five BSB bodies use Content-Length; the five Gallica bodies arrived with
chunked transfer and no Content-Length, within the same streaming cap.

No page was displayed or read. No OCR, crop, classifier, caption, source
transcription, or Voynich target was opened. The JPEGs and private state remain
outside the repository. This result establishes source-byte acquisition only;
it assigns no Voynich sign, word, language, plant, plaintext, operation, or
meaning. A separately public GDT621 registration must precede manual reading.
