from dirlay import Dir
from pytest import mark

from tests.sample import AppSettings


@mark.parametrize(
    'conf,secrets',
    (
        (
            dict(secrets_nested_delimiter='___', secrets_prefix='prefix_'),
            {'prefix_app_key': 'secret1', 'prefix_db___passwd': 'secret2'},
        ),
        (
            dict(secrets_nested_subdir=True, secrets_prefix='prefix_'),
            {'prefix_app_key': 'secret1', 'prefix_db/passwd': 'secret2'},
        ),
        (
            dict(secrets_nested_subdir=True, secrets_prefix='dir1/dir2/'),
            {'dir1/dir2/app_key': 'secret1', 'dir1/dir2/db/passwd': 'secret2'},
        ),
    ),
)
def test_prefix(conf, secrets, monkeypatch, tmp_path):
    monkeypatch.setenv('DB__USER', 'user')

    class Settings(AppSettings):
        model_config = dict(
            env_nested_delimiter='__',
            secrets_dir=tmp_path,
            **conf,
        )

    with Dir(secrets).mktree(tmp_path):
        assert Settings().model_dump() == {
            'app_key': 'secret1',
            'db': {'user': 'user', 'passwd': 'secret2'},
        }
