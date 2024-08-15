from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from pytest import fixture

from pydantic_file_secrets import FileSecretsSettingsSource


# Settings


class DbSettings(BaseModel):
    user: str
    password: str | None = None


class Settings(BaseSettings):
    db: DbSettings
    app_key: str | None = None


class SettingsMaker:
    def __call__(
        self,
        model_config: SettingsConfigDict | dict | None,
    ) -> type[Settings]:
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
                    env_settings,
                    init_settings,
                    FileSecretsSettingsSource(settings_cls),
                )

        TestSettings.model_config = model_config or {}
        return TestSettings


@fixture()
def settings_model() -> SettingsMaker:
    return SettingsMaker()


# secrets_dir


class SecretsDir(Path):
    def add_files(self, *files: tuple[str, str]) -> None:
        for path, content in files:
            f = self / path
            f.parent.mkdir(parents=True, exist_ok=True)  # allow child dirs in path
            f.write_text(content)


@fixture()
def secrets_dir(tmp_path) -> SecretsDir:
    yield SecretsDir(tmp_path)
