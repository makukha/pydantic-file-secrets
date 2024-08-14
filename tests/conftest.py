from copy import copy
from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings

from pytest import fixture


# Settings

class DbSettings(BaseModel):
    user: str
    password: str | None = None


class RootSettings(BaseSettings):
    db: DbSettings
    app_key: str | None = None


@fixture()
def Settings() -> type[RootSettings]:
    return copy(RootSettings)


# secrets_dir

class SecretsDir(Path):
    def add_files(self, files: dict[str, str]) -> None:
        for path, content in files.items():
            f = self / path
            f.parent.mkdir(parents=True, exist_ok=True)  # allow child dirs in path
            f.write_text(content)

@fixture()
def secrets_dir(tmp_path) -> SecretsDir:
    yield SecretsDir(tmp_path)
