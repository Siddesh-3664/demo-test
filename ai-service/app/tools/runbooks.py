import logging
from pathlib import Path

import httpx

from app.config import settings
from app.schemas import RunbookHits, RunbookHit

log = logging.getLogger("runbooks")
COLLECTION = "runbooks"


def client():
    import chromadb
    return chromadb.PersistentClient(path=settings.chroma_path)


def chunk(text: str, size: int = 400, overlap: int = 50) -> list[str]:
    """Split text into overlapping chunks of approximately `size` characters."""
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        chunks.append(text[start:end])
        if end >= len(text):
            break
        start = end - overlap
    return chunks


async def embed(texts: list[str]) -> list[list[float]]:
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            f"{settings.ollama_url}/api/embed",
            json={"model": settings.embed_model, "input": texts},
        )
        resp.raise_for_status()
        return resp.json()["embeddings"]


async def index(dir: str = "runbooks") -> int:
    """Index all runbook .md files into ChromaDB. Skip if already indexed."""
    db = client()
    coll = db.get_or_create_collection(COLLECTION)
    if coll.count() > 0:
        log.info("runbooks already indexed: %d chunks", coll.count())
        return coll.count()

    runbook_dir = Path(dir)
    if not runbook_dir.is_absolute():
        runbook_dir = Path(__file__).parent.parent.parent / dir

    all_chunks = []
    all_embeddings = []
    all_metadata = []
    all_ids = []

    for md_file in sorted(runbook_dir.glob("*.md")):
        text = md_file.read_text()
        title = text.split("\n")[0].replace("# ", "").strip()
        chunks = chunk(text)
        embeddings = await embed(chunks)
        for i, (c, e) in enumerate(zip(chunks, embeddings)):
            all_chunks.append(c)
            all_embeddings.append(e)
            all_metadata.append({"title": title, "file": md_file.name, "idx": i})
            all_ids.append(f"{md_file.stem}_{i}")

    if all_chunks:
        coll.add(
            ids=all_ids,
            embeddings=all_embeddings,
           documents=all_chunks,
            metadatas=all_metadata,
        )

    log.info("indexed %d runbook chunks", len(all_chunks))
    return len(all_chunks)


async def search(query: str, n: int = 2) -> RunbookHits:
    """Search runbooks by semantic similarity."""
    db = client()
    coll = db.get_or_create_collection(COLLECTION)
    if coll.count() == 0:
        return RunbookHits(hits=[])

    query_emb = await embed([query])
    results = coll.query(query_embeddings=query_emb, n_results=n)

    hits = []
    metadatas = results.get("metadatas", [[]])[0]
    documents = results.get("documents", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for meta, doc, dist in zip(metadatas, documents, distances):
        title = meta.get("title", "Unknown")
        snippet = doc[:300]
        score = round(1 - dist, 2)
        hits.append(RunbookHit(title=title, snippet=snippet, score=score))

    return RunbookHits(hits=hits)
