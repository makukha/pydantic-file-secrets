from pydantic_settings import SettingsConfigDict
import pytest


def test_delimited_name_fails(Settings, monkeypatch, secrets_dir):
    Settings.model_config = SettingsConfigDict(
        secrets_dir=secrets_dir,
        env_nested_delimiter='__',
    )
    monkeypatch.setenv('DB__USER', 'user')
    secrets_dir.add_files({
        'app_key': 'secret',
        'db__password': 'secret',  # file name with delimiter
    })
    conf = Settings()

    assert conf.app_key == 'secret'
    assert conf.db.password is None


def test_pure_name_fails(Settings, monkeypatch, secrets_dir):
    Settings.model_config = SettingsConfigDict(
        secrets_dir=secrets_dir,
        env_nested_delimiter='__',
    )
    monkeypatch.setenv('DB__USER', 'user')
    secrets_dir.add_files({
        'app_key': 'secret',
        'password': 'secret',  # file name matching nested option name
    })
    conf = Settings()

    assert conf.app_key == 'secret'
    assert conf.db.password is None


def test_subdir_fails(Settings, monkeypatch, secrets_dir):
    Settings.model_config = SettingsConfigDict(
        secrets_dir=secrets_dir,
        env_nested_delimiter='__',
    )
    monkeypatch.setenv('DB__USER', 'user')
    secrets_dir.add_files({
        'app_key': 'secret',
        'db/password': 'secret',  # file in nested subdirectory
    })
    with pytest.warns(UserWarning, match='attempted to load secret file .* but found a directory instead'):
        conf = Settings()

    assert conf.app_key == 'secret'
    assert conf.db.password is None
