from pydantic_file_secrets import FileSecretsSettingsSource
from pydantic_settings import BaseSettings, SecretsSettingsSource, SettingsConfigDict


def test_repr(secrets_dir):
    class Settings(BaseSettings):
        model_config = SettingsConfigDict(
            secrets_dir=secrets_dir,
        )

    src = FileSecretsSettingsSource(SecretsSettingsSource(Settings))
    assert f'{src!r}'.startswith(f'{src.__class__.__name__}(')
