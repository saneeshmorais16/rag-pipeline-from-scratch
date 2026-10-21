"""Run a small labelled retrieval/citation benchmark with no external LLM calls."""
import argparse
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from app.embeddings import HashingEmbedder, SentenceTransformerEmbedder
from app.rag import RAGPipeline
from app.retrieval import Retriever
from app.vector_store import SQLiteVectorStore


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", choices=["hashing", "semantic"], default="hashing")
    args = parser.parse_args()
    os.environ["LLM_PROVIDER"] = ""  # Explicit extractive mode; never spend API credits.
    embedder = HashingEmbedder() if args.backend == "hashing" else SentenceTransformerEmbedder("sentence-transformers/all-MiniLM-L6-v2")
    data = json.loads(Path("evaluation/dataset.json").read_text())
    chunks = [{"source":d["id"],"document_name":d["id"],"chunk_index":0,"text":d["text"],"start_char":0,"end_char":len(d["text"])} for d in data["documents"]]
    details=[]
    with TemporaryDirectory() as directory:
        store=SQLiteVectorStore(Path(directory)/"evaluation.sqlite3")
        store.add_chunks(chunks,embedder.embed_texts([c["text"] for c in chunks]))
        retriever=Retriever(embedder,store)
        pipeline=RAGPipeline(retriever)
        for case in data["queries"]:
            retrieved=retriever.retrieve(case["question"],top_k=3)
            answer=pipeline.answer(case["question"],top_k=3)
            cited=[s["document_name"] for s in answer["sources"]] if answer["is_supported"] else []
            details.append({**case,"top_documents":[s["document_name"] for s in retrieved],"cited_documents":cited,"answer":answer["answer"],"is_supported":answer["is_supported"]})
    answerable=[d for d in details if d["expected_document"] is not None]
    unsupported=[d for d in details if d["expected_document"] is None]
    citations=sum(len(d["cited_documents"]) for d in details)
    relevant=sum(d["cited_documents"].count(d["expected_document"]) for d in details)
    result={
        "backend":args.backend,"embedding_model":"hashing-384" if args.backend=="hashing" else "sentence-transformers/all-MiniLM-L6-v2",
        "dataset":"12 fictional policy documents, 24 answerable questions, 6 unanswerable questions; see dataset.json",
        "retrieval_top1_accuracy":sum(d["top_documents"][0]==d["expected_document"] for d in answerable)/len(answerable),
        "retrieval_hit_at_3":sum(d["expected_document"] in d["top_documents"] for d in answerable)/len(answerable),
        "citation_document_precision":relevant/citations if citations else 0.0,
        "citation_document_recall":sum(d["expected_document"] in d["cited_documents"] for d in answerable)/len(answerable),
        "unanswerable_rejection_rate":sum(not d["is_supported"] for d in unsupported)/len(unsupported),
        "citation_counts":{"relevant":relevant,"total":citations},
        "methodology":"Default relevance threshold 0.18; top_k=3; one chunk per document. Citation precision is expected-document membership, NOT semantic entailment. Rejected answers have no counted citations.",
        "limitations":"Small author-created diagnostic corpus; not held out from development. Lexical overlap and distinctive names make retrieval easier; similarity thresholds cannot establish answerability. No generative model evaluated.",
        "cases":details,
    }
    Path(f"evaluation/results-{args.backend}.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k!='cases'},indent=2))

if __name__ == "__main__":
    main()
