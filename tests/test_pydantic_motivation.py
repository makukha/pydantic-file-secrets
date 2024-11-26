"""
These tests show that nested secrets problem exists.
"""

from typing import Union

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
import pytest


def test_delimited_name_fails(monkeypatch, secrets_dir):
    class DbSettings(BaseModel):
        user: str
        password: Union[str, None] = None

    class Settings(BaseSettings):
        db: DbSettings
        app_key: Union[str, None] = None
        model_config = SettingsConfigDict(
            secrets_dir=secrets_dir,
            env_nested_delimiter='__',
        )

    monkeypatch.setenv('DB__USER', 'user')
    secrets_dir.add_files(
        ('app_key', 'secret'),
        ('db__password', 'secret'),  # file name with delimiter
    )

    conf = Settings()
    assert conf.app_key == 'secret'
    assert conf.db.password is None


def test_pure_name_fails(monkeypatch, secrets_dir):
    class DbSettings(BaseModel):
        user: str
        password: Union[str, None] = None

    class Settings(BaseSettings):
        db: DbSettings
        app_key: Union[str, None] = None
        model_config = SettingsConfigDict(
            secrets_dir=secrets_dir,
            env_nested_delimiter='__',
        )

    monkeypatch.setenv('DB__USER', 'user')
    secrets_dir.add_files(
        ('app_key', 'secret'),
        ('password', 'secret'),  # file name matching nested option name
    )

    conf = Settings()
    assert conf.app_key == 'secret'
    assert conf.db.password is None  # not loaded


def test_subdir_fails(monkeypatch, secrets_dir):
    class DbSettings(BaseModel):
        user: str
        password: Union[str, None] = None

    class Settings(BaseSettings):
        db: DbSettings
        app_key: Union[str, None] = None
        model_config = SettingsConfigDict(
            secrets_dir=secrets_dir,
            env_nested_delimiter='__',
        )

    monkeypatch.setenv('DB__USER', 'user')
    secrets_dir.add_files(
        ('app_key', 'secret'),
        ('db/password', 'secret'),  # file in nested subdirectory
    )

    with pytest.warns(UserWarning):
        conf = Settings()
    assert conf.app_key == 'secret'
    assert conf.db.password is None  # not loaded
