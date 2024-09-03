def test_strip_whitespace(settings_model, monkeypatch, secrets_dir):
    monkeypatch.setenv('DB__USER', 'user')
    secrets_dir.add_files(
        ('app_key', ' secret1 '),
        ('db___password', '\tsecret2\n'),  # file name with delimiter
    )
    Settings = settings_model(
        model_config=dict(
            env_nested_delimiter='__',
            secrets_dir=secrets_dir,
            secrets_nested_delimiter='___',
        ),
    )
    conf = Settings()
    assert conf.app_key == 'secret1'
    assert conf.db.password == 'secret2'  # noqa: S105
