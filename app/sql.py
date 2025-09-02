import logging
from typing import Any, Generator

from fastapi import Request
from sqlalchemy import Column, LargeBinary
from sqlmodel import SQLModel, Field, Session

from config import load_config

settings = load_config()
logger = logging.getLogger(__name__)
logger.setLevel(settings.log_level)


class SImage(SQLModel, table=True):
    id: int = Field(primary_key=True, nullable=False, index=True)
    filename: str = Field(nullable=False, index=True)
    content_type: str = Field(nullable=False, index=True)
    data: bytes = Field(sa_column=Column(LargeBinary, nullable=False))


def create_db_and_tables(engine) -> None:
    SQLModel.metadata.create_all(engine)
    logger.debug("Created initial database tables")


def get_session(request: Request) -> Generator[Session, Any, None]:
    with Session(request.app.state.engine) as session:
        yield session
        logger.debug("Yielding session")

