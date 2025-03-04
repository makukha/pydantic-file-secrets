"""
These tests show that the interface of original SecretsSettingsSource declares features
that are not working:

    - env_ignore_empty
    - env_parse_none_str
    - env_parse_enums
    - str_strip_whitespace
"""

from enum import Enum
from typing import Optional

from dirlay import Dir
from pydantic_settings import BaseSettings, SettingsConfigDict
from pytest import mark


class SampleEnum(str, Enum):
    TEST = 'test'


class Settings(BaseSettings):
    some_str: Optional[str] = None
    some_enum: Optional[SampleEnum] = None


@mark.parametrize(
    'secrets_dir,conf,expected',
    (
        ({'some_str': ''}, dict(env_ignore_empty=True), {'some_str': ''}),
        ({'some_str': 'null'}, dict(env_parse_none_str='null'), {'some_str': 'null'}),
        ({'some_enum': 'test'}, dict(env_parse_enums=False), {'some_enum': SampleEnum.TEST}),
        # whitespace is always stripped on secrets
        ({'some_str': 'value '}, dict(), {'some_str': 'value'}),
        ({'some_str': 'value '}, dict(str_strip_whitespace=False), {'some_str': 'value'}),
    ),
)  # fmt: skip
def test_not_working(secrets_dir, conf, expected, tmp_path):
    class MySettings(Settings):
        model_config = SettingsConfigDict(secrets_dir=tmp_path, **conf)

    with Dir(secrets_dir).mktree(tmp_path):
        settings = MySettings()
        for k, v in expected.items():
            assert getattr(settings, k) == v
