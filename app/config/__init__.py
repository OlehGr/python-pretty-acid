import os

from dotenv import load_dotenv

load_dotenv()


def get_not_empty_env(key: str) -> str:
    value = os.environ.get("DATABSE_URL")

    if value is None:
        raise ValueError(f"{key} not exist in enviroment")

    return value


DATABASE_URL = get_not_empty_env("DATABSE_URL")
DB_NAME = DATABASE_URL.split("/").pop()
