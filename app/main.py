from pathlib import Path
import shutil
from tempfile import NamedTemporaryFile

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.embeddings import get_embedder
from app.ingestion import SUPPORTED_EXTENSIONS, discover_documents, prepare_chunks
from app.rag import RAGPipeline
from app.retrieval import Retriever
from app.schemas import HealthResponse, IngestRequest, IngestResponse, QueryRequest, QueryResponse
from app.vector_store import SQLiteVectorStore


settings = get_settings()
embedder = get_embedder(settings.embedding_model)
vector_store = SQLiteVectorStore(settings.vector_store_path)
retriever = Retriever(embedder, vector_store)
rag_pipeline = RAGPipeline(retriever, min_relevance_score=settings.min_relevance_score)

app = FastAPI(title="RAG Pipeline From Scratch", version="0.1.0")
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(Path(__file__).parent / "static" / "index.html")


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", chunks_indexed=vector_store.count_chunks())


@app.get("/documents")
def documents() -> dict:
    return {"documents": vector_store.documents()}


@app.post("/ingest", response_model=IngestResponse)
def ingest(request: IngestRequest) -> IngestResponse:
    path = Path(request.path)
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Path not found: {request.path}")
    return _ingest_paths(discover_documents(path))


@app.post("/ingest/upload", response_model=IngestResponse)
def ingest_upload(file: UploadFile = File(...)) -> IngestResponse:
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only .txt, .md, and .pdf files are supported.")
    settings.upload_path.mkdir(parents=True, exist_ok=True)
    destination = settings.upload_path / Path(file.filename or "uploaded_document").name
    with NamedTemporaryFile(delete=False) as temp_file:
        shutil.copyfileobj(file.file, temp_file)
        temp_path = Path(temp_file.name)
    temp_path.replace(destination)
    return _ingest_paths([destination])


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest) -> dict:
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question is required.")
    return rag_pipeline.answer(request.question, top_k=request.top_k)


def _ingest_paths(paths: list[Path]) -> IngestResponse:
    chunks = prepare_chunks(paths, settings.chunk_size, settings.chunk_overlap)
    if not chunks:
        return IngestResponse(documents_found=len(paths), chunks_added=0)
    embeddings = embedder.embed_texts([chunk["text"] for chunk in chunks])
    added = vector_store.add_chunks(chunks, embeddings)
    return IngestResponse(documents_found=len(paths), chunks_added=added)
