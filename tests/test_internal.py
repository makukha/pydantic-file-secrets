from pydantic_file_secrets import FileSecretsSettingsSource
from pydantic_settings import BaseSettings, SecretsSettingsSource, SettingsConfigDict


def test_repr(tmp_path):
    class Settings(BaseSettings):
        model_config = SettingsConfigDict(
            secrets_dir=tmp_path,
        )

    src = FileSecretsSettingsSource(SecretsSettingsSource(Settings))
    assert f'{src!r}'.startswith(f'{src.__class__.__name__}(')
