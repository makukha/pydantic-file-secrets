from pathlib import Path
from typing import Tuple, Type, Union

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from pytest import fixture

from pydantic_file_secrets import FileSecretsSettingsSource


# Settings


class DbSettings(BaseModel):
    user: str
    password: Union[str, None] = None


class Settings(BaseSettings):
    db: DbSettings
    app_key: Union[str, None] = None


class SettingsMaker:
    def __call__(
        self,
        model_config: Union[SettingsConfigDict, dict, None],
    ) -> Type[Settings]:
        class TestSettings(Settings):
            @classmethod
            def settings_customise_sources(
                cls,
                settings_cls,
                init_settings,
                env_settings,
                dotenv_settings,
                file_secret_settings,
            ) -> tuple:
                return (
                    init_settings,
                    env_settings,
                    FileSecretsSettingsSource(file_secret_settings),
                )

        TestSettings.model_config = model_config or {}
        return TestSettings


@fixture()
def settings_model() -> SettingsMaker:
    return SettingsMaker()


# secrets_dir


class SecretsDir(type(Path())):
    def add_files(self, *files: Tuple[str, str]) -> None:
        for path, content in files:
            f = self / path
            f.parent.mkdir(parents=True, exist_ok=True)  # allow child dirs in path
            f.write_text(content)


@fixture()
def secrets_dir(tmp_path) -> SecretsDir:
    yield SecretsDir(tmp_path)
