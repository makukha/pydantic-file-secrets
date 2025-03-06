from typing import Optional, Tuple

from pydantic import BaseModel
from pydantic_settings import BaseSettings

from pydantic_file_secrets import (
    BaseSource,
    BuiltinSources,
    FileSecretsSettingsSource,
    with_builtin_sources,
)


class DbSettings(BaseModel):
    user: str
    passwd: Optional[str] = None


class AppSettings(BaseSettings):
    app_key: Optional[str] = None
    db: DbSettings

    @classmethod
    @with_builtin_sources
    def settings_customise_sources(cls, src: BuiltinSources) -> Tuple[BaseSource, ...]:
        return (
            src.init_settings,
            src.env_settings,
            FileSecretsSettingsSource(src.file_secret_settings),
        )
