from app.tools.runbooks import chunk


def test_chunk_size():
    text = "a" * 1000
    chunks = chunk(text, size=400, overlap=50)
    for c in chunks:
        assert len(c) <= 400, f"chunk length {len(c)} > 400"


def test_chunk_overlap():
    text = "abcdefghij" * 100  # 1000 chars
    chunks = chunk(text, size=400, overlap=50)
    if len(chunks) >= 2:
        # The last 50 chars of chunk[0] should be the first 50 of chunk[1]
        assert chunks[0][-50:] == chunks[1][:50], "overlap not correct"


def test_chunk_single():
    text = "short"
    chunks = chunk(text, size=400, overlap=50)
    assert len(chunks) == 1
    assert chunks[0] == "short"


def test_chunk_empty():
    chunks = chunk("", size=400, overlap=50)
    assert len(chunks) == 0
