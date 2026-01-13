import json
import traceback
from sqlalchemy.orm import Session

from agent_ops.db import SessionLocal, engine
from agent_ops.models import Base, Run, RunStatus
from agent_ops.runner import run_task

Base.metadata.create_all(bind=engine)


def execute_run(run_id: str) -> None:
    db: Session = SessionLocal()
    try:
        run = db.get(Run, run_id)
        if not run:
            return

        run.status = RunStatus.running.value
        db.add(run)
        db.commit()

        spec = json.loads(run.spec_json or "{}")
        rr = run_task(spec)

        if rr.ok:
            run.status = RunStatus.succeeded.value
            run.result_json = json.dumps(rr.result)
            run.error = None
        else:
            run.status = RunStatus.failed.value
            run.result_json = json.dumps(rr.result or {})
            run.error = rr.error or "Unknown error"

        db.add(run)
        db.commit()
    except Exception:
        db.rollback()
        err = traceback.format_exc()
        run = db.get(Run, run_id)
        if run:
            run.status = RunStatus.failed.value
            run.error = err
            db.add(run)
            db.commit()
    finally:
        db.close()


def main():
    # RQ worker entrypoint
    from rq import Worker
    from agent_ops.queue import queue, redis_conn

    w = Worker([queue], connection=redis_conn)
    w.work(with_scheduler=False)


if __name__ == "__main__":
    main()
