# Retrieval and citation evaluation

Run `python -m evaluation.run` for hashing or `python -m evaluation.run --backend semantic` for sentence-transformer embeddings. Both use extractive answers with no paid LLM calls. The semantic runner fails if the model cannot load; it does not silently substitute hashing.

## Dataset and method

[dataset.json](../evaluation/dataset.json) contains 12 author-created fictional policy documents, 24 answerable questions, and 6 unanswerable questions. Each document is a single chunk. Queries use top_k=3 and the existing relevance threshold 0.18; these settings were not tuned to improve this report.

Top-1 accuracy measures whether the expected document ranks first on answerable queries. Hit@3 measures whether it appears among the first three results. Citation precision is expected-document citations divided by all citations, including those attached to unanswerable responses. Citation recall is the fraction of answerable queries citing the expected document. These are document relevance measures, not semantic entailment or answer accuracy.

| Measure | Hashing | Semantic MiniLM |
| --- | ---: | ---: |
| Top-1 retrieval accuracy | 87.50% | 100.00% |
| Retrieval hit@3 | 100.00% | 100.00% |
| Citation document precision | 75.00% | 85.71% |
| Citation document recall | 87.50% | 100.00% |
| Unanswerable rejection rate | 0.00% | 33.33% |

Raw outputs include every query, response, and cited document: [hashing](../evaluation/results-hashing.json), [semantic](../evaluation/results-semantic.json).

## Engineering changes and limitations

- SQLite connections are explicitly closed after transactions; a Windows evaluation exposed a leaked handle that prevented temporary database cleanup. A regression test checks closure.
- Extractive answers now use and cite only the highest-ranked qualifying document. Previously unused retrieval hits were also attached as citations.
- Explicit `EMBEDDING_MODEL=hashing` enables deterministic offline tests. If normal semantic model loading fails, a warning identifies fallback use.
- Semantic retrieval finds the correct document on all 24 answerable questions in this small corpus, but answers four of six unanswerable questions. Hashing rejects none. The similarity gate is not a reliable answerability classifier.
- Distinctive fictional names and lexical overlap make this corpus easier than realistic retrieval. It is a development diagnostic, not an independent held-out benchmark. No generative model, multi-document synthesis, or production accuracy claim is evaluated.
- The observed public MiniLM model revision was `1110a243fdf4706b3f48f1d95db1a4f5529b4d41`; the default model name can resolve to later revisions on future runs.
