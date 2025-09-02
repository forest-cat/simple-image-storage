import os
import argparse
import yaml
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    db_filename: str = Field("database.db", validation_alias="DATABASE_FILENAME")
    port: int = Field(8000, validation_alias="PORT")
    log_level: str = Field("info", validation_alias="LOG_LEVEL")
    config_file: str = Field(..., validation_alias="CONFIG_FILENAME")
    token: str = Field(..., validation_alias="ACCESS_TOKEN")
    img_size: int = Field(5, validation_alias="IMG_SIZE")
    model_config = {
        "populate_by_name": True
    }


def load_config() -> Settings:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db-filename", type=str)
    parser.add_argument("--port", type=int)
    parser.add_argument("--log-level", type=str)
    parser.add_argument("--config-file", type=str, default="config.yaml")
    parser.add_argument("--token", type=str)
    parser.add_argument("--img-size", type=int)
    args = parser.parse_args()

    # YAML Args
    yaml_data = {}
    if os.path.exists(str(args.config_file)):
        with open(args.config_file) as f:
            yaml_data = yaml.safe_load(f) or {}

    data = {}

    if args.db_filename or os.getenv("SIS_DATABASE_FILENAME") or yaml_data.get("db_filename"):
        data["db_filename"] = args.db_filename or os.getenv("SIS_DATABASE_FILENAME") or yaml_data.get("db_filename")

    if args.port or os.getenv("SIS_PORT") or yaml_data.get("port"):
        data["port"] = args.port or os.getenv("SIS_PORT") or yaml_data.get("port")

    if args.log_level or os.getenv("SIS_LOG_LEVEL") or yaml_data.get("log_level"):
        data["log_level"] = args.log_level or os.getenv("SIS_LOG_LEVEL") or yaml_data.get("log_level")

    if args.config_file or os.getenv("SIS_CONFIG_FILENAME"):
        data["config_file"] = args.config_file or os.getenv("SIS_CONFIG_FILENAME")

    if args.token or os.getenv("SIS_ACCESS_TOKEN") or yaml_data.get("token"):
        data["token"] = args.token or os.getenv("SIS_ACCESS_TOKEN") or yaml_data.get("token")

    if args.img_size or os.getenv("SIS_IMG_SIZE") or yaml_data.get("img_size"):
        data["img_size"] = args.img_size or os.getenv("SIS_IMG_SIZE") or yaml_data.get("img_size")

    # pydantic validation
    return Settings(**data)
