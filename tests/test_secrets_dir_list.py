import pytest


def test_merge(settings_model, monkeypatch, secrets_dir):
    monkeypatch.setenv('DB__USER', 'user')
    secrets_dir.add_files(
        ('dir1/app_key', 'secret1'),
        ('dir1/db___password', 'secret2'),
        ('dir2/db___password', 'secret3'),
    )
    Settings = settings_model(
        model_config=dict(
            env_nested_delimiter='__',
            secrets_dir=[secrets_dir / 'dir1', secrets_dir / 'dir2'],
            secrets_nested_delimiter='___',
        ),
    )
    conf = Settings()
    assert conf.app_key == 'secret1'
    assert conf.db.password == 'secret3'  # noqa: S105


def test_missing(settings_model, monkeypatch, secrets_dir):
    monkeypatch.setenv('DB__USER', 'user')
    Settings = settings_model(
        model_config=dict(
            env_nested_delimiter='__',
            secrets_dir=[secrets_dir / 'dir1', secrets_dir / 'dir2'],
            secrets_nested_delimiter='___',
        ),
    )
    with pytest.warns(UserWarning) as warninfo:
        Settings()
    assert len(warninfo) == 2
    assert all('does not exist' in w.message.args[0] for w in warninfo)
