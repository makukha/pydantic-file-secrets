from dirlay import Dir
import pydantic_settings.main  # import to monkeypatch

from pydantic_file_secrets import FileSecretsSettingsSource


def test_dropin(monkeypatch, tmp_path):
    monkeypatch.setattr(
        pydantic_settings.main,
        'SecretsSettingsSource',
        FileSecretsSettingsSource,
    )
    secrets = Dir() | {
        'dir1/key1': 'secret1',
        'dir2/key2': 'secret2',
    }

    class Settings(pydantic_settings.BaseSettings):
        key1: str
        key2: str

    with secrets.mktree(tmp_path):
        conf = Settings(_secrets_dir=[secrets // 'dir1', secrets // 'dir2'])
        assert conf.model_dump() == {
            'key1': 'secret1',
            'key2': 'secret2',
        }
