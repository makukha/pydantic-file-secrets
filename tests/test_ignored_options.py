from enum import Enum
from typing import Optional

from dirlay import Dir
from pydantic_settings import BaseSettings
from pytest import mark

from tests.sample import settings_customise_sources


class SampleEnum(str, Enum):
    TEST = 'test'


class Settings(BaseSettings):
    field_empty: Optional[str] = None
    field_none: Optional[str] = None
    field_enum: Optional[SampleEnum] = None


@mark.parametrize(
    'conf,expected',
    (
        # default settings
        ({}, dict(field_empty='', field_none='null', field_enum=SampleEnum.TEST)),
        # env_ignore_empty has no effect on secrets
        ({'env_ignore_empty': True}, dict(field_empty='')),
        ({'env_ignore_empty': False}, dict(field_empty='')),
        # env_parse_none_str has no effect on secrets
        ({'env_parse_none_str': 'null'}, dict(field_none='null')),
        # env_parse_enums has no effect on secrets
        ({'env_parse_enums': True}, dict(field_enum=SampleEnum.TEST)),
        ({'env_parse_enums': False}, dict(field_enum=SampleEnum.TEST)),
    ),
)
def test_env_ignore_empty(conf, expected, tmp_path):
    secrets = Dir() | {
        'field_empty': '',
        'field_none': 'null',
        'field_enum': 'test',
    }

    class Original(Settings):
        model_config = {'secrets_dir': tmp_path, **conf}

    class Evaluated(Settings):
        model_config = {'secrets_dir': tmp_path, **conf}
        settings_customise_sources = classmethod(settings_customise_sources)

    with secrets.mktree(tmp_path):
        original = Original()
        evaluated = Evaluated()
        assert original.model_dump() == evaluated.model_dump()
        for k, v in expected.items():
            assert getattr(original, k) == getattr(evaluated, k) == v
