from typing import Optional

from pydantic import BaseModel
from pydantic_settings import BaseSettings

from pydantic_file_secrets import FileSecretsSettingsSource


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


class DbSettings(BaseModel):
    user: str
    passwd: Optional[str] = None


class AppSettings(BaseSettings):
    settings_customise_sources = classmethod(settings_customise_sources)
    db: DbSettings
    app_key: Optional[str] = None
