from pydantic_settings.sources import SettingsError
import pytest


def test_subdir(settings_model, monkeypatch, secrets_dir):
    monkeypatch.setenv('DB__USER', 'user')
    secrets_dir.add_files(
        ('app_key', 'secret1'),
        ('db/password', 'secret2'),  # file in subdir
    )
    Settings = settings_model(
        model_config=dict(
            secrets_dir=secrets_dir,
            env_nested_delimiter='__',
            secrets_nested_subdir=True,
        ),
    )
    conf = Settings()
    assert conf.app_key == 'secret1'
    assert conf.db.password == 'secret2'  # noqa: S105


def test_invalid_options(settings_model, monkeypatch, secrets_dir):
    monkeypatch.setenv('DB__USER', 'user')
    Settings = settings_model(
        model_config=dict(
            secrets_dir=secrets_dir,
            env_nested_delimiter='__',
            secrets_nested_subdir=True,
            secrets_nested_delimiter='__',
        ),
    )
    with pytest.raises(SettingsError, match='mutually exclusive'):
        Settings()
