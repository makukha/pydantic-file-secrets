def test_prefix_plain(settings_model, monkeypatch, secrets_dir):
    monkeypatch.setenv('DB__USER', 'user')
    secrets_dir.add_files(
        ('prefix_app_key', 'secret1'),
        ('prefix_db___password', 'secret2'),
    )
    Settings = settings_model(
        model_config=dict(
            env_nested_delimiter='__',
            secrets_dir=secrets_dir,
            secrets_nested_delimiter='___',
            secrets_prefix='prefix_',
        ),
    )
    conf = Settings()
    assert conf.app_key == 'secret1'
    assert conf.db.password == 'secret2'  # noqa: S105


def test_prefix_with_subdir(settings_model, monkeypatch, secrets_dir):
    monkeypatch.setenv('DB__USER', 'user')
    secrets_dir.add_files(
        ('prefix_app_key', 'secret1'),
        ('prefix_db/password', 'secret2'),
    )
    Settings = settings_model(
        model_config=dict(
            env_nested_delimiter='__',
            secrets_dir=secrets_dir,
            secrets_nested_subdir=True,
            secrets_prefix='prefix_',
        ),
    )
    conf = Settings()
    assert conf.app_key == 'secret1'
    assert conf.db.password == 'secret2'  # noqa: S105


def test_prefix_multiple_subdirs(settings_model, monkeypatch, secrets_dir):
    monkeypatch.setenv('DB__USER', 'user')
    secrets_dir.add_files(
        ('dir1/dir2/app_key', 'secret1'),
        ('dir1/dir2/db/password', 'secret2'),
    )
    Settings = settings_model(
        model_config=dict(
            env_nested_delimiter='__',
            secrets_dir=secrets_dir,
            secrets_nested_subdir=True,
            secrets_prefix='dir1/dir2/',
        ),
    )
    conf = Settings()
    assert conf.app_key == 'secret1'
    assert conf.db.password == 'secret2'  # noqa: S105
