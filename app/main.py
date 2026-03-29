from time import perf_counter
import orjson
import uvicorn

from fastapi import Depends, FastAPI, Response
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
      select(Build.attrpath, Build.status)
      .where(Build.status != "success")
    ).all()

    output = [
        dict(attrpath=b.attrpath, status=b.status)
        for b in builds_rows
    ]

    return Response(orjson.dumps(output), media_type="application/json")


def main():
    app.mount("/", StaticFiles(directory="dist", html=True))

    uvicorn.run(app, host="0.0.0.0", port=8080)
