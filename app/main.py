import orjson
import subprocess
import uvicorn

from fastapi import Depends, FastAPI, Query, Response
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import select

from .db import get_db
from .models import Build


app = FastAPI()
app.mount("/build-logs", StaticFiles(directory="build-logs"))


@app.get("/api/builds")
def list_builds(db: Session = Depends(get_db)):
    builds_rows = db.execute(
      select(Build.attrpath, Build.status, Build.hydra_id)
      .where(Build.status == "failed")
    ).all()

    output = [
        dict(attrpath=b.attrpath, status=b.status, hydra_id=b.hydra_id)
        for b in builds_rows
    ]

    return Response(orjson.dumps(output), media_type="application/json")


@app.get("/api/search")
def search_logs(q: str = Query(..., min_length=2, max_length=100)):
    cmd = (
        "rg",
        "--fixed-strings",
        "--files-with-matches",
        q,
        "build-logs",
    )

    proc = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
    )

    return [
        f.removeprefix("build-logs/").removesuffix(".log")
        for f in (proc.stdout or "").splitlines()
    ]


def main():
    app.mount("/", StaticFiles(directory="dist", html=True))

    uvicorn.run(app, host="0.0.0.0", port=8080)
