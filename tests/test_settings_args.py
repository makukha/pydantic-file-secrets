def test_strip_whitespace(settings_model, monkeypatch, secrets_dir):
    monkeypatch.setenv('DB__USER', 'user')
    secrets_dir.add_files(
        ('dir1/app_key', 'secret1'),
        ('dir2/db___password', 'secret2'),
    )
    Settings = settings_model(
        model_config=dict(
            env_nested_delimiter='__',
            secrets_nested_delimiter='___',
        ),
    )
    conf = Settings(_secrets_dir=[secrets_dir / 'dir1', secrets_dir / 'dir2'])
    assert conf.app_key == 'secret1'
    assert conf.db.password == 'secret2'  # noqa: S105
