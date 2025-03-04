"""
These tests show that nested secrets do not work in Pydantic Settings.
"""

from typing import Optional

from dirlay import Dir
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
import pytest
from pytest import mark


class DbSettings(BaseModel):
    user: str
    passwd: Optional[str] = None


class AppSettings(BaseSettings):
    app_key: Optional[str] = None
    db: DbSettings


@mark.parametrize(
    'secrets_dir,warning',
    (
        # file name matching nested field name does not work
        ({'passwd': 'secret1', 'app_key': 'secret2'}, None),
        # file name with env_nested_delimiter does not work
        ({'db__passwd': 'secret1', 'app_key': 'secret2'}, None),
        # subdirectory does not work
        ({'db/passwd': 'secret1', 'app_key': 'secret2'}, (UserWarning, 'found a directory instead')),
    ),
)  # fmt: skip
def test_failing_configuration(secrets_dir, warning, monkeypatch, tmp_path):
    monkeypatch.setenv('DB__USER', 'user')

    class Settings(AppSettings):
        model_config = SettingsConfigDict(
            secrets_dir=tmp_path,
            env_nested_delimiter='__',
        )

    with Dir(secrets_dir).mktree(tmp_path):
        if warning is None:
            settings = Settings()
        else:
            warning_type, msg_fragment = warning
            with pytest.warns(warning_type, match=msg_fragment):
                settings = Settings()

        assert settings.model_dump() == {
            'db': {'user': 'user', 'passwd': None},  # passwd is not loaded
            'app_key': 'secret2',  # app_key is loaded because it's not nested
        }
