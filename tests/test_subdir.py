from dirlay import Dir
from pydantic_settings.sources import SettingsError
import pytest

from pydantic_file_secrets import SettingsConfigDict
from tests.sample import AppSettings


def test_subdir(monkeypatch, tmp_path):
    monkeypatch.setenv('DB__USER', 'user')
    secrets = Dir() | {
        'app_key': 'secret1',
        'db/passwd': 'secret2',  # file in subdir
    }

    class Settings(AppSettings):
        model_config = SettingsConfigDict(
            secrets_dir=tmp_path,
            env_nested_delimiter='__',
            secrets_nested_subdir=True,
        )

    with secrets.mktree(tmp_path):
        assert Settings().model_dump() == {
            'app_key': 'secret1',
            'db': {'user': 'user', 'passwd': 'secret2'},
        }


def test_invalid_options(tmp_path):
    class Settings(AppSettings):
        model_config = SettingsConfigDict(
            secrets_dir=tmp_path,
            env_nested_delimiter='__',
            secrets_nested_subdir=True,
            secrets_nested_delimiter='__',
        )

    with pytest.raises(SettingsError, match='mutually exclusive'):
        Settings()
