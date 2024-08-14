
from pydantic_settings import SettingsConfigDict
import pytest

from pydantic_file_secrets import FileSecretsSettingsSource


def settings_customise_sources(
    cls,
    settings_cls,
    init_settings,
    env_settings,
    dotenv_settings,
    file_secret_settings,
) -> tuple:
    return env_settings, init_settings, FileSecretsSettingsSource(settings_cls)


def test_delimited_name(Settings, monkeypatch, secrets_dir):

    class CustomSettings(Settings):
        model_config = SettingsConfigDict(
            secrets_dir=secrets_dir,
            env_nested_delimiter='__',
        )
        settings_customise_sources = classmethod(settings_customise_sources)

    monkeypatch.setenv('DB__USER', 'user')
    secrets_dir.add_files({
        'app_key': 'secret',
        'db__password': 'secret',  # file name with delimiter
    })
    conf = CustomSettings()

    # assert conf.app_key == 'secret'
    # assert conf.db.password == 'secret'


# todo: custom separator
# todo: subdirs


# def test_pure_name_fails(Settings, monkeypatch, secrets_dir):
#     Settings.model_config = SettingsConfigDict(
#         secrets_dir=secrets_dir,
#         env_nested_delimiter='__',
#     )
#     monkeypatch.setenv('DB__USER', 'user')
#     secrets_dir.add_files({
#         'app_key': 'secret',
#         'password': 'secret',  # file name matching nested option name
#     })
#     conf = Settings()
#
#     assert conf.app_key == 'secret'
#     assert conf.db.password is None
#
#
# def test_subdir_fails(Settings, monkeypatch, secrets_dir):
#     Settings.model_config = SettingsConfigDict(
#         secrets_dir=secrets_dir,
#         env_nested_delimiter='__',
#     )
#     monkeypatch.setenv('DB__USER', 'user')
#     secrets_dir.add_files({
#         'app_key': 'secret',
#         'db/password': 'secret',  # file in subdirectory
#     })
#     with pytest.warns(UserWarning, match='attempted to load secret file .* but found a directory instead'):
#         conf = Settings()
#
#     assert conf.app_key == 'secret'
#     assert conf.db.password is None
