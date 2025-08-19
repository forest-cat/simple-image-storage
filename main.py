import configparser
import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, Response

def read_config() -> dict:
    config = configparser.ConfigParser()
    config_name = "dev_config.ini" if os.path.exists("dev_config.ini") else "config.ini"
    config.read(config_name)
    config_values = {
        "db_filename" : config.get("Database", "filename")
    }
    return config_values



@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting up: {app.title}")
    read_config()
    yield
    logger.info(f"Shutting down: {app.title}")

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Simple Image Storage API",
    lifespan=lifespan,
    contact={
        "name": "Forestcat",
        "url": "https://forestcat.org",
        "email": "sis-api-contact@forestcat.org",
    },
    openapi_url=None, # Disable public API docs
)
@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

@app.post("/upload/")
async def upload_file(file: UploadFile):
    with open(file.filename, "wb") as f:
        f.write(await file.read())
    # return {"file": file.filename}
    return Response(status_code=200)
