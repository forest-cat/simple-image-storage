import configparser
import json
import logging
import os
from uuid import uuid4
from typing import Annotated, Any, Coroutine
from sqlalchemy import LargeBinary
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, Response, Depends
from sqlmodel import create_engine, Field, SQLModel, Session, Column
from starlette.responses import Response, StreamingResponse

logger = logging.getLogger(__name__)

class SImage(SQLModel, table=True):
    id: str = Field(primary_key=True, nullable=False, default_factory=lambda: str(uuid4()), index=True)
    filename: str = Field(nullable=False, index=True)
    content_type: str = Field(nullable=False, index=True)
    data: bytes = Field(sa_column=Column(LargeBinary, nullable=False))


def create_db_and_tables():
    SQLModel.metadata.create_all(app.state.engine)

def get_session():
    with Session(app.state.engine) as session:
        yield session

def read_config() -> dict:
    config = configparser.ConfigParser()
    config_name = "dev_config.ini" if os.path.exists("dev_config.ini") else "config.ini"
    config.read(config_name)
    config_values = {
        "db_filename" : config.get("Database", "filename")
    }
    return config_values

SessionDependency = Annotated[Session, Depends(get_session)]


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting up: {app.title}")
    app.state.config = read_config()
    app.state.engine = create_engine(
        f"sqlite:///{app.state.config['db_filename']}",
        connect_args={"check_same_thread": False}
    )
    create_db_and_tables()
    yield
    logger.info(f"Shutting down: {app.title}")
    app.state.engine.dispose()



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
async def upload_file(file: UploadFile, session: SessionDependency):
    img = SImage(filename=file.filename, content_type=file.content_type, data=await file.read())
    session.add(img)
    session.commit()
    return Response(status_code=200, media_type="application/json", content=json.dumps({"uuid": img.id}))

@app.get("/image/{uuid}")
async def download_file(uuid: str, session: SessionDependency) -> Response:
    img = session.get(SImage, uuid)
    if img is None:
        return Response(status_code=404)
    else:
        return Response(content=img.data,
            media_type=img.content_type,
            headers={"content-disposition": f"attachment; filename={img.filename}"},
            status_code=200
        )