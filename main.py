import configparser
import json
import logging
import os
from contextlib import asynccontextmanager
from io import BytesIO
from typing import Annotated

from fastapi import FastAPI, UploadFile, Depends, Request, HTTPException
from sqlalchemy import LargeBinary
from sqlmodel import create_engine, Field, SQLModel, Session, Column
from starlette.responses import Response
from PIL import Image, UnidentifiedImageError

logger = logging.getLogger(__name__)


class SImage(SQLModel, table=True):
    id: int = Field(primary_key=True, nullable=False, index=True)
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
        "db_filename": config.get("Database", "filename"),
        "cr_token": config.get("Credentials", "token"),
        "st_imgsize": config.getint("Settings", "imgsize")
    }
    return config_values


async def verify_token(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or auth_header != f"Bearer {app.state.config['cr_token']}":
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing token",
        )


def remove_file_extension(filename: str) -> str:
    return os.path.splitext(filename)[0]

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


@app.get("/hello/{name}", dependencies=[Depends(verify_token)])
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.post("/upload/{id}", dependencies=[Depends(verify_token)])
async def upload_file(id: int, file: UploadFile, session: SessionDependency):
    try:
        content = await file.read()

        if len(content) > app.state.config["st_imgsize"] * 1024 * 1024:
            raise HTTPException(status_code=413, detail="File too large")
        image = Image.open(BytesIO(content))
        image.verify()

        image = Image.open(BytesIO(content))  # Reopen after verify
        image = image.convert("RGB")
        output = BytesIO()
        image.save(output, format="WEBP")
        output.seek(0) # reset BytesIO cursor after writing image


        img = SImage(id=id, filename=f"{remove_file_extension(file.filename)}.webp", content_type="image/webp", data=output.read())
        session.merge(img)
        session.commit()
        return Response(status_code=200, media_type="application/json", content=json.dumps({"id": img.id}))
    except UnidentifiedImageError:
        raise HTTPException(status_code=415, detail="Uploaded file is not a valid image")
    except HTTPException as e:
        if e.status_code == 413:
            raise HTTPException(status_code=413, detail="File too large")
    except Exception as e:
        logger.error(f"Unexpected: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error")


@app.get("/image/{id}")
async def download_file(id: int, session: SessionDependency) -> Response:
    img = session.get(SImage, id)
    if img is None:
        return Response(status_code=404)
    else:
        return Response(
            content=img.data,
            media_type=img.content_type,
            headers={"content-disposition": f"attachment; filename={img.filename}"},
            status_code=200)

