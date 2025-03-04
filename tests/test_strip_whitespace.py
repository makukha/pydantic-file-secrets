from dirlay import Dir

from tests.sample import AppSettings


def test_strip_whitespace(monkeypatch, tmp_path):
    monkeypatch.setenv('DB__USER', 'user')
    secrets = Dir() | {
        'app_key': ' secret1 ',
        'db__passwd': '\tsecret2\n',
    }

    class Settings(AppSettings):
        model_config = dict(
            env_nested_delimiter='__',
            secrets_dir=tmp_path,
            secrets_nested_delimiter='__',
        )

    with secrets.mktree(tmp_path):
        assert Settings(_secrets_dir=tmp_path).model_dump() == {
            'app_key': 'secret1',
            'db': {'user': 'user', 'passwd': 'secret2'},
        }
