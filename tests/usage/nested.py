from pydantic import BaseModel, Secret
from pydantic_file_secrets import FileSecretsSettingsSource, SettingsConfigDict
from pydantic_settings import BaseSettings
from pydantic_settings.sources import PydanticBaseSettingsSource


class DbSettings(BaseModel):
    passwd: Secret[str]


class Settings(BaseSettings):
    app_key: Secret[str]
    db: DbSettings

    model_config = SettingsConfigDict(
        secrets_dir='secrets',
        secrets_nested_subdir=True,
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            FileSecretsSettingsSource(file_secret_settings),
        )
