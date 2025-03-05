from pydantic import BaseModel, Secret
from pydantic_file_secrets import (
    BaseSource,
    BuiltinSources,
    FileSecretsSettingsSource,
    SettingsConfigDict,
    with_builtin_sources,
)
from pydantic_settings import BaseSettings


class DbSettings(BaseModel):
    passwd: Secret[str]


class Settings(BaseSettings):
    app_key: Secret[str]
    db: DbSettings

    model_config = SettingsConfigDict(
        secrets_dir='secrets',
        secrets_nested_delimiter='__',
    )

    @classmethod
    @with_builtin_sources
    def settings_customise_sources(cls, src: BuiltinSources) -> tuple[BaseSource, ...]:
        return (
            src.init_settings,
            src.env_settings,
            src.dotenv_settings,
            FileSecretsSettingsSource(src.file_secret_settings),
        )
