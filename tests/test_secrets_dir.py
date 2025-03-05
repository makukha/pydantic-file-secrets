from typing import Optional, Tuple

from dirlay import Dir
from pydantic_settings import BaseSettings
from pydantic_settings.sources import SettingsError
import pytest
from pytest import mark

from pydantic_file_secrets import (
    BaseSource,
    BuiltinSources,
    FileSecretsSettingsSource,
    SECRETS_DIR_MAX_SIZE,
    SettingsConfigDict,
    with_builtin_sources,
)


class Settings(BaseSettings):
    key1: Optional[str] = None
    key2: Optional[str] = None

    @classmethod
    @with_builtin_sources
    def settings_customise_sources(cls, src: BuiltinSources) -> Tuple[BaseSource, ...]:
        return (FileSecretsSettingsSource(src.file_secret_settings),)


@mark.parametrize(
    'conf,secrets,dirs,expected',
    (
        (
            # when multiple secrets_dir values are given, their values are merged
            dict(),
            Dir({'dir1/key1': 'a', 'dir1/key2': 'b', 'dir2/key2': 'c'}),
            ['dir1', 'dir2'],
            {'key1': 'a', 'key2': 'c'},
        ),
        (
            # when secrets_dir is not a directory, error is raised
            dict(),
            Dir({'some_file': ''}),
            'some_file',
            (SettingsError, 'must reference a directory'),
        ),
        (
            # missing secrets_dir emits warning by default
            dict(),
            Dir({'key1': 'value'}),
            'missing_subdir',
            (UserWarning, 1, 'does not exist', {'key1': None, 'key2': None}),
        ),
        (
            # ...or expect warning explicitly (identical behaviour)
            dict(secrets_dir_missing='warn'),
            Dir({'key1': 'value'}),
            'missing_subdir',
            (UserWarning, 1, 'does not exist', {'key1': None, 'key2': None}),
        ),
        (
            # missing secrets_dir warning can be suppressed
            dict(secrets_dir_missing='ok'),
            Dir({'key1': 'value'}),
            'missing_subdir',
            {'key1': None, 'key2': None},
        ),
        (
            # missing secrets_dir can raise error
            dict(secrets_dir_missing='error'),
            Dir({'key1': 'value'}),
            'missing_subdir',
            (SettingsError, 'does not exist'),
        ),
        (
            # invalid secrets_dir_missing value raises error
            dict(secrets_dir_missing='uNeXpEcTeD'),
            Dir({'key1': 'value'}),
            'missing_subdir',
            (SettingsError, 'invalid secrets_dir_missing value'),
        ),
        (
            # when multiple secrets_dir do not exist, multiple warnings are emitted
            dict(),
            Dir({'key1': 'value'}),
            ['missing_subdir1', 'missing_subdir2'],
            (UserWarning, 2, 'does not exist', {'key1': None, 'key2': None}),
        ),
        (
            # secrets_dir size is limited
            dict(),
            Dir({'key1': 'x' * SECRETS_DIR_MAX_SIZE}),
            '.',
            {'key1': 'x' * SECRETS_DIR_MAX_SIZE, 'key2': None},
        ),
        (
            # ...and raises error if file is larger than the limit
            dict(),
            Dir({'key1': 'x' * (SECRETS_DIR_MAX_SIZE + 1)}),
            '.',
            (SettingsError, 'secrets_dir size'),
        ),
        (
            # secrets_dir size limit can be adjusted
            dict(secrets_dir_max_size=100),
            Dir({'key1': 'x' * 100}),
            '.',
            {'key1': 'x' * 100, 'key2': None},
        ),
        (
            # ...and raises error if file is larger than the limit
            dict(secrets_dir_max_size=100),
            Dir({'key1': 'x' * 101}),
            '.',
            (SettingsError, 'secrets_dir size'),
        ),
        (
            # ...even if secrets_dir size exceeds limit because of another file
            dict(secrets_dir_max_size=100),
            Dir({'another_file': 'x' * 101}),
            '.',
            (SettingsError, 'secrets_dir size'),
        ),
        (
            # when multiple secrets_dir values are given, their sizes are not added
            dict(secrets_dir_max_size=100),
            Dir({'dir1/key1': 'x' * 100, 'dir2/key2': 'y' * 100}),
            ['dir1', 'dir2'],
            {'key1': 'x' * 100, 'key2': 'y' * 100},
        ),
    ),
)
def test_cases(conf: SettingsConfigDict, secrets, dirs, expected, tmp_path):
    secrets_dirs = (
        [tmp_path / d for d in dirs]
        if isinstance(dirs, list)
        else tmp_path / dirs
    )  # fmt: skip

    class MySettings(Settings):
        model_config = SettingsConfigDict(secrets_dir=secrets_dirs, **conf)

    with secrets.mktree(tmp_path):
        # clean execution
        if isinstance(expected, dict):
            assert MySettings().model_dump() == expected
        # error
        elif isinstance(expected, tuple) and len(expected) == 2:
            error_type, msg_fragment = expected
            with pytest.raises(error_type, match=msg_fragment):
                MySettings()
        # warnings
        elif isinstance(expected, tuple) and len(expected) == 4:
            warning_type, warning_count, msg_fragment, value = expected
            with pytest.warns(warning_type) as warninfo:
                settings = MySettings()
            assert len(warninfo) == warning_count
            assert all(msg_fragment in str(w.message) for w in warninfo)
            assert settings.model_dump() == value
        # unexpected
        else:
            raise AssertionError('unreachable')
