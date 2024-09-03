"""
These tests show that the interface of original SecretsSettingsSource
declares features that are not working.
"""

from enum import StrEnum

from pydantic_settings import BaseSettings, SettingsConfigDict


def test_not_working_env_ignore_empty(secrets_dir):
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

    secrets_dir.add_files(
        ('key_empty', ''),
        ('key_none', 'null'),
        ('key_enum', 'test'),
    )

    conf = Settings()
    assert conf.key_empty == ''  # should be None if working
    assert conf.key_none == 'null'  # should be Null if working
    assert isinstance(conf.key_enum, TestEnum)  # should be True if working


def test_str_strip_whitespace_not_specified(secrets_dir):
    class Settings(BaseSettings):
        key: str

        model_config = SettingsConfigDict(
            secrets_dir=secrets_dir,
            # str_strip_whitespace not specified
        )

    secrets_dir.add_files(
        ('key', ' value '),
    )

    conf = Settings()
    assert conf.key == 'value'  # spaces are stripped by SecretsSettingsSource


def test_str_strip_whitespace_not_respected(secrets_dir):
    class Settings(BaseSettings):
        key: str

        model_config = SettingsConfigDict(
            secrets_dir=secrets_dir,
            str_strip_whitespace=False,
        )

    secrets_dir.add_files(
        ('key', ' value '),
    )

    conf = Settings()
    assert conf.key == 'value'  # str_strip_whitespace not respected
