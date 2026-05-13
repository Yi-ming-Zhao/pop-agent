from __future__ import annotations

from fastapi import FastAPI, HTTPException

from .config import load_settings
from .memory import MemoryStore
from .models import GenerationRequest, GenerationResult
from .orchestrator import GenerationService
from .storage import read_json

app = FastAPI(title="Pop Agent API", version="0.1.0")


@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/api/generate", response_model=GenerationResult)
async def generate(request: GenerationRequest) -> GenerationResult:
    return await GenerationService(load_settings()).generate(request)


@app.get("/api/runs/{run_id}")
async def get_run(run_id: str) -> dict:
    path = load_settings().data_dir / "runs" / run_id / "state.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail="run not found")
    return read_json(path)


@app.get("/api/users/{user_id}/memory")
async def get_memory(user_id: str, q: str | None = None) -> dict:
    store = MemoryStore(load_settings().data_dir)
    if q:
        return {"results": [item.model_dump() for item in store.search(user_id, q)]}
    return {"content": store.show(user_id)}
