from dataclasses import dataclass
import re


@dataclass(frozen=True)
class TextChunk:
    text: str
    chunk_index: int
    start_char: int
    end_char: int


def clean_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk_text(text: str, chunk_size: int = 900, overlap: int = 150) -> list[TextChunk]:
    cleaned = clean_text(text)
    if not cleaned:
        return []
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    chunks: list[TextChunk] = []
    start = 0
    index = 0

    while start < len(cleaned):
        target_end = min(start + chunk_size, len(cleaned))
        end = _nearest_boundary(cleaned, start, target_end)
        piece = cleaned[start:end].strip()
        if piece:
            actual_start = start + (len(cleaned[start:end]) - len(cleaned[start:end].lstrip()))
            chunks.append(TextChunk(text=piece, chunk_index=index, start_char=actual_start, end_char=end))
            index += 1
        if end >= len(cleaned):
            break
        start = max(0, end - overlap)

    return chunks


def _nearest_boundary(text: str, start: int, target_end: int) -> int:
    if target_end >= len(text):
        return len(text)
    window = text[start:target_end]
    for marker in ("\n\n", ". ", "\n", " "):
        boundary = window.rfind(marker)
        if boundary >= int(len(window) * 0.55):
            return start + boundary + len(marker)
    return target_end
