import pathlib
import subprocess
from contextlib import asynccontextmanager

import orjson
import uvicorn
from fastapi import FastAPI, Query, Response
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select

from .db import get_db
from .models import Build

state = {}


@asynccontextmanager
async def lifespan(_: FastAPI):
    state["commit"] = orjson.loads(
        pathlib.Path("last-commit.json").read_text()
    )

    with next(get_db()) as session:
        rows = session.execute(
            select(
                Build.attrpath,
                Build.hydra_id,
                Build.tag,
                Build.error_line_number,
            )
        ).all()

    state["builds"] = [
        {
            "attrpath": b.attrpath,
            "hydra_id": b.hydra_id,
            "tag": b.tag,
            "error_line_number": b.error_line_number,
        }
        for b in rows
    ]

    print("Loaded", len(state["builds"]), "builds into the state")
    yield
    state.clear()


app = FastAPI(lifespan=lifespan)
app.mount("/build-logs", StaticFiles(directory="build-logs"))


@app.get("/api/builds")
async def list_builds() -> Response:
    return Response(
        orjson.dumps({"commit": state["commit"], "builds": state["builds"]}),
        media_type="application/json",
    )


@app.get("/api/search")
def search_logs(q: str = Query(..., min_length=3, max_length=100)):
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
