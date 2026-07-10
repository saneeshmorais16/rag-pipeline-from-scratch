import pytest

from app.chunking import chunk_text, clean_text


def test_clean_text_normalizes_spacing():
    assert clean_text("A   sentence.\r\n\r\n\r\nNext") == "A sentence.\n\nNext"


def test_chunk_text_uses_overlap_and_indices():
    text = " ".join(f"word{i}" for i in range(80))
    chunks = chunk_text(text, chunk_size=80, overlap=15)
    assert len(chunks) > 1
    assert chunks[0].chunk_index == 0
    assert chunks[1].start_char < chunks[0].end_char


def test_chunk_text_rejects_invalid_overlap():
    with pytest.raises(ValueError):
        chunk_text("hello", chunk_size=10, overlap=10)
