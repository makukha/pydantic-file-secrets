"""
These tests show that the interface of original SecretsSettingsSource
declares features that are not working.
"""
from enum import StrEnum

from pydantic_settings import BaseSettings, SettingsConfigDict


def test_not_working_env_ignore_empty(monkeypatch, secrets_dir):

    class TestEnum(StrEnum):
        TEST = 'test'

    class Settings(BaseSettings):
        key_empty: str
        key_none: str
        key_enum: TestEnum

        model_config = SettingsConfigDict(
            secrets_dir=secrets_dir,
            # options below don't work
            env_ignore_empty=True,
            env_parse_none_str='null',
            env_parse_enums=False,
        )

    secrets_dir.add_files({
        'key_empty': '',
        'key_none': 'null',
        'key_enum': 'test',
    })

    conf = Settings()
    assert conf.key_empty == ''  # should be None if working
    assert conf.key_none == 'null'  # should be Null if working
    assert isinstance(conf.key_enum, TestEnum)  # should be True if working
