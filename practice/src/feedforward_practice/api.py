"""HTTP API for FeedForward Desktop (the Electron shell's sidecar).

lens-contract standard surface (/health, /manifest, bearer auth via
FEEDFORWARD_PRACTICE_AUTH_TOKEN) plus the practice routes. Feedback runs
are asynchronous jobs (the family's 202-and-poll pattern) because model
calls can take minutes on local hardware.
"""

import threading
import uuid
from typing import Any

from fastapi import FastAPI, HTTPException
from lens_contract import add_auth, add_contract_routes, add_cors
from pydantic import BaseModel, Field

from feedforward_practice.manifest import MANIFEST
from feedforward_practice.providers import (
    ProviderConfig,
    ProviderError,
    list_models,
)
from feedforward_practice.run import practice_feedback

app = FastAPI(title=MANIFEST["name"], version=MANIFEST["version"])
add_contract_routes(app, MANIFEST)
add_auth(app, env_prefix="FEEDFORWARD_PRACTICE")  # before add_cors
add_cors(app, env_prefix="FEEDFORWARD_PRACTICE")


class ProviderIn(BaseModel):
    base_url: str = ""
    api_key: str = ""
    model: str = ""


class FeedbackRequest(BaseModel):
    rubric: dict
    draft_text: str
    num_runs: int = Field(default=1, ge=1, le=5)
    provider: ProviderIn = ProviderIn()


_jobs: dict[str, dict[str, Any]] = {}
_jobs_lock = threading.Lock()


def _run_job(job_id: str, req: FeedbackRequest) -> None:
    provider = ProviderConfig.from_env().merged(req.provider.model_dump())
    try:
        result = practice_feedback(req.rubric, req.draft_text, provider, req.num_runs)
        update = {"status": "done", "result": result}
    except Exception as e:  # surfaced to the UI as a friendly failure
        update = {"status": "error", "error": str(e)}
    with _jobs_lock:
        _jobs[job_id].update(update)


@app.post("/practice/feedback", status_code=202)
def start_feedback(req: FeedbackRequest):
    job_id = uuid.uuid4().hex
    with _jobs_lock:
        _jobs[job_id] = {"status": "running"}
    threading.Thread(target=_run_job, args=(job_id, req), daemon=True).start()
    return {"id": job_id, "status": "running"}


@app.get("/practice/feedback/{job_id}")
def get_feedback(job_id: str):
    with _jobs_lock:
        job = _jobs.get(job_id)
        if job is None:
            raise HTTPException(status_code=404, detail="Unknown job")
        return {"id": job_id, **job}


@app.post("/practice/models")
def models(provider: ProviderIn):
    cfg = ProviderConfig.from_env().merged(provider.model_dump())
    try:
        return {"models": list_models(cfg)}
    except ProviderError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e
