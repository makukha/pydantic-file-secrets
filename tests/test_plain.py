def test_delimited_name(settings_model, monkeypatch, secrets_dir):
    monkeypatch.setenv('DB__USER', 'user')
    secrets_dir.add_files({
        'app_key': 'secret1',
        'db___password': 'secret2',  # file name with delimiter
    })
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


def test_secrets_off(settings_model, monkeypatch, secrets_dir):
    monkeypatch.setenv('DB__USER', 'user')
    secrets_dir.add_files({
        'app_key': 'secret1',
        'db__password': 'secret2',  # file name with delimiter
    })
    Settings = settings_model(
        model_config=dict(
            env_nested_delimiter='__',
            # missing secrets_dir
        ),
    )
    conf = Settings()
    assert conf.app_key is None
    assert conf.db.password is None
