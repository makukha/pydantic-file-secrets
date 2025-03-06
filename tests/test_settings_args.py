from dirlay import Dir

from pydantic_file_secrets import SettingsConfigDict
from tests.sample import AppSettings


def test_secrets_dir_as_arg(monkeypatch, tmp_path):
    monkeypatch.setenv('DB__USER', 'user')
    secrets = Dir() | {
        'app_key': 'secret1',
        'db__passwd': 'secret2',
    }

    class Settings(AppSettings):
        model_config = SettingsConfigDict(
            env_nested_delimiter='__',
            secrets_nested_delimiter='__',
        )

    with secrets.mktree(tmp_path):
        assert Settings(_secrets_dir=tmp_path).model_dump() == {
            'app_key': 'secret1',
            'db': {'user': 'user', 'passwd': 'secret2'},
        }
