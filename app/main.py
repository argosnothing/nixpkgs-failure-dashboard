import uvicorn

from fastapi import Depends, FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from .db import get_db
from .models import Build


LIMIT_PER_PAGE = 100


app = FastAPI()
app.mount("/build-logs", StaticFiles(directory="build-logs"))


@app.get("/api/builds")
def list_builds(
    db: Session = Depends(get_db),
    page: int = 1,
):
    base_query = db.query(Build).filter()

    total = base_query.count()
    builds = (
        base_query
        .offset((page - 1) * LIMIT_PER_PAGE)
        .limit(LIMIT_PER_PAGE)
        .all()
    )

    return {
        "total": total,
        "results": builds,
    }


def main():
    app.mount("/", StaticFiles(directory="dist", html=True))

    uvicorn.run(app, host="0.0.0.0", port=8080)
