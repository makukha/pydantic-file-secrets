import pytest

import pydantic_settings.main  # import to monkeypatch
from pydantic_file_secrets import FileSecretsSettingsSource


@pytest.fixture
def monkeypatch_settings(monkeypatch):
    monkeypatch.setattr(
        pydantic_settings.main,
        'SecretsSettingsSource',
        FileSecretsSettingsSource,
    )


def test_dropin(settings_model, monkeypatch_settings, secrets_dir):
    secrets_dir.add_files(
        ('dir1/key1', 'secret1'),
        ('dir2/key2', 'secret2'),
    )

    class Settings(pydantic_settings.BaseSettings):
        key1: str
        key2: str

    conf = Settings(_secrets_dir=[secrets_dir / 'dir1', secrets_dir / 'dir2'])

    assert conf.key1 == 'secret1'
    assert conf.key2 == 'secret2'
