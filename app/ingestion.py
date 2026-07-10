from pathlib import Path
from typing import Iterable

from app.chunking import TextChunk, chunk_text


SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf"}


class UnsupportedFileTypeError(ValueError):
    pass


def discover_documents(path: Path) -> list[Path]:
    if path.is_file():
        return [path] if path.suffix.lower() in SUPPORTED_EXTENSIONS else []
    return sorted(p for p in path.rglob("*") if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS)


def extract_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".txt", ".md"}:
        return path.read_text(encoding="utf-8", errors="ignore")
    if suffix == ".pdf":
        return _extract_pdf(path)
    raise UnsupportedFileTypeError(f"Unsupported file type: {path.suffix}")


def prepare_chunks(paths: Iterable[Path], chunk_size: int, overlap: int) -> list[dict]:
    prepared: list[dict] = []
    for path in paths:
        text = extract_text(path)
        chunks = chunk_text(text, chunk_size=chunk_size, overlap=overlap)
        prepared.extend(_chunk_record(path, chunk) for chunk in chunks)
    return prepared


def _chunk_record(path: Path, chunk: TextChunk) -> dict:
    return {
        "source": str(path),
        "document_name": path.name,
        "chunk_index": chunk.chunk_index,
        "text": chunk.text,
        "start_char": chunk.start_char,
        "end_char": chunk.end_char,
    }


def _extract_pdf(path: Path) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError("Install pypdf to ingest PDF files.") from exc

    reader = PdfReader(str(path))
    return "\n\n".join(page.extract_text() or "" for page in reader.pages)
