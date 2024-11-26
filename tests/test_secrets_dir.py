from pydantic_settings.sources import SettingsError
import pytest


def test_missing_dir_ok(settings_model, monkeypatch, tmp_path):
    monkeypatch.setenv('DB__USER', 'user')
    Settings = settings_model(
        model_config=dict(
            env_nested_delimiter='__',
            secrets_dir=tmp_path / 'non-existing',
            secrets_dir_missing='ok',
        ),
    )
    conf = Settings()
    assert conf.app_key is None
    assert conf.db.password is None


def test_missing_dir_warn(settings_model, monkeypatch, tmp_path):
    monkeypatch.setenv('DB__USER', 'user')
    Settings = settings_model(
        model_config=dict(
            env_nested_delimiter='__',
            secrets_dir=tmp_path / 'non-existing',
            # warn is default
        ),
    )
    with pytest.warns(UserWarning, match='does not exist'):
        conf = Settings()
    assert conf.app_key is None
    assert conf.db.password is None


def test_missing_dir_error(settings_model, monkeypatch, tmp_path):
    monkeypatch.setenv('DB__USER', 'user')
    Settings = settings_model(
        model_config=dict(
            env_nested_delimiter='__',
            secrets_dir=tmp_path / 'non-existing',
            secrets_dir_missing='error',
        ),
    )
    with pytest.raises(SettingsError, match='does not exist'):
        Settings()


def test_missing_dir_invalid(settings_model, monkeypatch, tmp_path):
    monkeypatch.setenv('DB__USER', 'user')
    Settings = settings_model(
        model_config=dict(
            env_nested_delimiter='__',
            secrets_dir=tmp_path / 'non-existing',
            secrets_dir_missing='whatever',  # invalid value
        ),
    )
    with pytest.raises(SettingsError, match='invalid secrets_dir_missing value'):
        Settings()


def test_secrets_not_dir(settings_model, monkeypatch, secrets_dir):
    monkeypatch.setenv('DB__USER', 'user')
    secrets_dir.add_files(
        ('secrets_notdir', ''),
    )
    Settings = settings_model(
        model_config=dict(
            env_nested_delimiter='__',
            secrets_dir=secrets_dir / 'secrets_notdir',  # file
        ),
    )
    with pytest.raises(SettingsError, match='must reference a directory'):
        Settings()


def test_secrets_dir_size(settings_model, monkeypatch, secrets_dir):
    SIZE = 10
    monkeypatch.setenv('DB__USER', 'user')
    secrets_dir.add_files(
        ('large_file', ' ' * SIZE),
    )
    Settings = settings_model(
        model_config=dict(
            env_nested_delimiter='__',
            secrets_dir=secrets_dir,
            secrets_dir_max_size=SIZE - 1,
        ),
    )
    with pytest.raises(SettingsError, match='secrets_dir size'):
        Settings()
