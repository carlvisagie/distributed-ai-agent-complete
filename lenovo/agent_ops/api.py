import json
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from agent_ops.db import get_session, engine
from agent_ops.models import Base, Run, RunStatus
from agent_ops.queue import queue

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Agent Ops", version="1.0.0")


class RunCreate(BaseModel):
    prompt: str = Field(min_length=3)
    workspace: str | None = None
    meta: dict = Field(default_factory=dict)


class RunOut(BaseModel):
    id: str
    status: str
    created_utc: str
    result: dict = Field(default_factory=dict)
    error: str | None = None


@app.get("/healthz")
def healthz():
    return {"ok": True}


@app.post("/v1/runs", response_model=RunOut)
def create_run(payload: RunCreate, db: Session = Depends(get_session)):
    run = Run(
        status=RunStatus.queued.value,
        spec_json=json.dumps(payload.model_dump()),
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    # Enqueue execution
    queue.enqueue("agent_ops.worker.execute_run", run.id)

    return RunOut(
        id=run.id,
        status=run.status,
        created_utc=run.created_utc.isoformat() + "Z",
        result=json.loads(run.result_json or "{}"),
        error=run.error,
    )


@app.get("/v1/runs/{run_id}", response_model=RunOut)
def get_run(run_id: str, db: Session = Depends(get_session)):
    run = db.get(Run, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    return RunOut(
        id=run.id,
        status=run.status,
        created_utc=run.created_utc.isoformat() + "Z",
        result=json.loads(run.result_json or "{}"),
        error=run.error,
    )
