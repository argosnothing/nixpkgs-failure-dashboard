import uvicorn

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles


app = FastAPI()
app.mount("/build-logs", StaticFiles(directory="build-logs"))


def main():
    uvicorn.run(app, host="0.0.0.0", port=8080)
