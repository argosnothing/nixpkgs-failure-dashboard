import uvicorn
from fastapi import Depends, FastAPI
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from .db import get_db
from .models import Build


app = FastAPI()
app.mount("/build-logs", StaticFiles(directory="build-logs"))


@app.get("/api/builds")
def list_builds(db: Session = Depends(get_db)):
    builds = db.query(Build).filter(Build.status != "success").all()
    return list(builds)


def main():
    app.mount("/", StaticFiles(directory="dist", html=True))

    uvicorn.run(app, host="0.0.0.0", port=8080)
