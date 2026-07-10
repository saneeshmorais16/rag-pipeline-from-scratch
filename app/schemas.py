from pydantic import BaseModel, Field


class IngestRequest(BaseModel):
    path: str = Field("data/sample_docs", description="File or folder path to ingest")


class IngestResponse(BaseModel):
    documents_found: int
    chunks_added: int


class QueryRequest(BaseModel):
    question: str
    top_k: int = Field(4, ge=1, le=12)


class Source(BaseModel):
    document_name: str
    source: str
    chunk_index: int
    text: str
    score: float


class QueryResponse(BaseModel):
    answer: str
    sources: list[Source]
    is_supported: bool


class HealthResponse(BaseModel):
    status: str
    chunks_indexed: int
