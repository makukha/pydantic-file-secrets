"""
These tests show that the behaviour of FileSecretsSettingsSource matches
SecretsSettingsSource for options env_ignore_empty, env_parse_none_str, env_parse_enums.
"""

from enum import Enum
from typing import Tuple, Type, Union

from pydantic_settings import BaseSettings, SettingsConfigDict
import pytest

from pydantic_file_secrets import FileSecretsSettingsSource


class SomeEnum(str, Enum):
    TEST = 'test'


class Settings(BaseSettings):
    key_empty: Union[str, None] = None
    key_none: Union[str, None] = None
    key_enum: Union[SomeEnum, None] = None


class SettingsPairMaker:
    def __call__(
        self,
        model_config: SettingsConfigDict,
    ) -> Tuple[Type[Settings], Type[Settings]]:
        class SettingsSSS(Settings):  # SecretsSettingsSource
            pass

        class SettingsFSSS(Settings):  # FileSecretsSettingsSource
            @classmethod
            def settings_customise_sources(
                cls,
                settings_cls,
                init_settings,
                env_settings,
                dotenv_settings,
                file_secret_settings,
            ) -> tuple:
                return (
                    init_settings,
                    env_settings,
                    FileSecretsSettingsSource(file_secret_settings),
                )

        SettingsSSS.model_config = model_config
        SettingsFSSS.model_config = model_config

        return (SettingsSSS, SettingsFSSS)


@pytest.fixture()
def settings_models() -> SettingsPairMaker:
    return SettingsPairMaker()


@pytest.fixture()
def populated_secrets_dir(secrets_dir):
    secrets_dir.add_files(
        ('key_empty', ''),
        ('key_none', 'null'),
        ('key_enum', 'test'),
    )
    yield secrets_dir


@pytest.mark.parametrize(
    'conf', [{}, {'env_ignore_empty': True}, {'env_ignore_empty': False}]
)
def test_env_ignore_empty(settings_models, conf, populated_secrets_dir):
    SettingsSSS, SettingsFSSS = settings_models(
        model_config=SettingsConfigDict(
            secrets_dir=populated_secrets_dir,
            **conf,
        ),
    )
    conf_sss, conf_fsss = SettingsSSS(), SettingsFSSS()
    assert conf_sss.key_empty == conf_fsss.key_empty == ''


@pytest.mark.parametrize('conf', [{}, {'env_parse_none_str': 'null'}])
def test_env_parse_none_str(settings_models, conf, populated_secrets_dir):
    SettingsSSS, SettingsFSSS = settings_models(
        model_config=SettingsConfigDict(
            secrets_dir=populated_secrets_dir,
            **conf,
        ),
    )
    conf_sss, conf_fsss = SettingsSSS(), SettingsFSSS()
    assert conf_sss.key_none == conf_fsss.key_none == 'null'


@pytest.mark.parametrize(
    'conf', [{}, {'env_parse_enums': True}, {'env_parse_enums': False}]
)
def test_env_parse_enums(settings_models, conf, populated_secrets_dir):
    SettingsSSS, SettingsFSSS = settings_models(
        model_config=SettingsConfigDict(
            secrets_dir=populated_secrets_dir,
            **conf,
        ),
    )
    conf_sss, conf_fsss = SettingsSSS(), SettingsFSSS()
    assert conf_sss.key_enum is SomeEnum.TEST
    assert conf_fsss.key_enum is SomeEnum.TEST
