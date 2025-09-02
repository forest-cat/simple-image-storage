import configparser
import json
import logging
import os
from contextlib import asynccontextmanager
from io import BytesIO
from typing import Annotated

import uvicorn
from fastapi import FastAPI, UploadFile, Depends, Request, HTTPException
from sqlmodel import create_engine, Session
from starlette.responses import Response
from PIL import Image, UnidentifiedImageError

from config import load_config
from sql import get_session, create_db_and_tables, SImage
from utils import verify_token, remove_file_extension

logger = logging.getLogger(__name__)

SessionDependency = Annotated[Session, Depends(get_session)]


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting up: {app.title}")
    app.state.settings = load_config()
    app.state.engine = create_engine(
        f"sqlite:///{app.state.settings.db_filename}",
        connect_args={"check_same_thread": False}
    )
    create_db_and_tables(app.state.engine)
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

        if len(content) > app.state.settings.img_size * 1024 * 1024:
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
        raise HTTPException(status_code=404, detail="Image does not exist")
    else:
        return Response(
            content=img.data,
            media_type=img.content_type,
            headers={"content-disposition": f"attachment; filename={img.filename}"},
            status_code=200)



if __name__ == "__main__":
    settings = load_config()

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.port,
        log_config="log_conf.yaml",
        log_level=settings.log_level.lower(),
    )