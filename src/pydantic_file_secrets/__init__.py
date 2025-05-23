import os
import warnings
from functools import reduce
from glob import iglob
from pathlib import Path
from typing import Any, Dict, Literal, Optional, Union

import pydantic_settings
from pydantic_settings import (
    BaseSettings,
    EnvSettingsSource,
    PydanticBaseSettingsSource,
    SecretsSettingsSource,
)
from pydantic_settings.sources import PathType
from pydantic_settings.utils import path_type_label

try:  # pydantic-settings >= 2.9
    from pydantic_settings import (
        SettingsError as SettingsError,
    )
except ImportError:  # pydantic-settings <= 2.3
    from pydantic_settings.sources import (  # type: ignore[attr-defined,no-redef,unused-ignore]
        SettingsError as SettingsError,
    )

try:  # pydantic-settings >= 2.9
    from pydantic_settings.sources.utils import (  # type: ignore[import-not-found,unused-ignore]
        parse_env_vars,
    )
except ImportError:  # pydantic-settings <= 2.8
    from pydantic_settings.sources import (  # type: ignore[attr-defined,no-redef,unused-ignore]
        parse_env_vars,
    )

from .__version__ import __version__ as __version__
from .customise import BaseSource, BuiltinSources, with_builtin_sources
from .types import SettingsConfigDict

__all__ = [
    'BaseSource',
    'BuiltinSources',
    'FileSecretsSettingsSource',
    'SettingsConfigDict',
    'with_builtin_sources',
]


SECRETS_DIR_MAX_SIZE = 16 * 2**20  # 16 MiB seems to be a reasonable default
PS_VERSION = pydantic_settings.__version__


class FileSecretsSettingsSource(EnvSettingsSource):
    def __init__(
        self,
        file_secret_settings: Union[PydanticBaseSettingsSource, SecretsSettingsSource],
        secrets_dir: Optional[PathType] = None,
        secrets_dir_missing: Optional[Literal['ok', 'warn', 'error']] = None,
        secrets_dir_max_size: Optional[int] = None,
        secrets_case_sensitive: Optional[bool] = None,
        secrets_prefix: Optional[str] = None,
        secrets_nested_delimiter: Optional[str] = None,
        secrets_nested_subdir: Optional[bool] = None,
        # args for compatibility with SecretsSettingsSource, don't use directly
        case_sensitive: Optional[bool] = None,
        env_prefix: Optional[str] = None,
    ) -> None:
        # We allow the first argument to be settings_cls like original
        # SecretsSettingsSource. However, it is recommended to pass
        # SecretsSettingsSource instance instead (as it is shown in usage examples),
        # otherwise `_secrets_dir` arg passed to Settings() constructor will be ignored.
        settings_cls: type[BaseSettings] = getattr(
            file_secret_settings,
            'settings_cls',
            file_secret_settings,  # type: ignore[arg-type]
        )
        # config options
        conf = settings_cls.model_config
        self.secrets_dir: Optional[PathType] = first_not_none(
            getattr(file_secret_settings, 'secrets_dir', None),
            secrets_dir,
            conf.get('secrets_dir'),
        )
        self.secrets_dir_missing: Literal['ok', 'warn', 'error'] = first_not_none(
            secrets_dir_missing,
            conf.get('secrets_dir_missing'),
            'warn',
        )
        self.secrets_dir_max_size: int = first_not_none(
            secrets_dir_max_size,
            conf.get('secrets_dir_max_size'),
            SECRETS_DIR_MAX_SIZE,
        )
        self.case_sensitive: bool = first_not_none(
            secrets_case_sensitive,
            conf.get('secrets_case_sensitive'),
            case_sensitive,
            conf.get('case_sensitive'),
            False,
        )
        self.secrets_prefix: str = first_not_none(
            secrets_prefix,
            conf.get('secrets_prefix'),
            env_prefix,
            conf.get('env_prefix'),
            '',
        )

        # nested options
        self.secrets_nested_delimiter: Optional[str] = first_not_none(
            secrets_nested_delimiter,
            conf.get('secrets_nested_delimiter'),
            conf.get('env_nested_delimiter'),
        )
        self.secrets_nested_subdir: bool = first_not_none(
            secrets_nested_subdir,
            conf.get('secrets_nested_subdir'),
            False,
        )
        if self.secrets_nested_subdir:
            if secrets_nested_delimiter or conf.get('secrets_nested_delimiter'):
                raise SettingsError(
                    'Options secrets_nested_delimiter and secrets_nested_subdir '
                    'are mutually exclusive'
                )
            else:
                self.secrets_nested_delimiter = os.sep

        # ensure valid secrets_path
        if self.secrets_dir is None:
            paths = []
        elif isinstance(self.secrets_dir, (Path, str)):
            paths = [self.secrets_dir]
        else:
            paths = list(self.secrets_dir)
        self.secrets_paths: list[Path] = [Path(p).expanduser().resolve() for p in paths]
        for path in self.secrets_paths:
            self.validate_secrets_path(path)

        # construct parent
        super().__init__(
            settings_cls,
            case_sensitive=self.case_sensitive,
            env_prefix=self.secrets_prefix,
            env_nested_delimiter=self.secrets_nested_delimiter,
            env_ignore_empty=False,  # match SecretsSettingsSource behaviour
            env_parse_none_str=None,  # match SecretsSettingsSource behaviour
            **(
                {'env_parse_enums': True}  # match SecretsSettingsSource behaviour
                if PS_VERSION >= '2.3'
                else {}
            ),
        )
        self.env_parse_none_str = None  # update manually because of None

        # update parent members
        if not len(self.secrets_paths):
            self.env_vars = {}
        else:
            secrets = reduce(
                lambda d1, d2: dict((*d1.items(), *d2.items())),
                (self.load_secrets(p) for p in self.secrets_paths),
            )
            self.env_vars = parse_env_vars(
                secrets,
                self.case_sensitive,
                self.env_ignore_empty,
                self.env_parse_none_str,
            )

    def validate_secrets_path(self, path: Path) -> None:
        if not path.exists():
            if self.secrets_dir_missing == 'ok':
                pass
            elif self.secrets_dir_missing == 'warn':
                warnings.warn(f'directory "{path}" does not exist', stacklevel=2)
            elif self.secrets_dir_missing == 'error':
                raise SettingsError(f'directory "{path}" does not exist')
            else:
                raise SettingsError(
                    f'invalid secrets_dir_missing value: {self.secrets_dir_missing}'
                )
        else:
            if not path.is_dir():
                raise SettingsError(
                    f'secrets_dir must reference a directory, '
                    f'not a {path_type_label(path)}'
                )
            secrets_dir_size = sum(
                f.stat().st_size for f in path.glob('**/*') if f.is_file()
            )
            if secrets_dir_size > self.secrets_dir_max_size:
                raise SettingsError(
                    f'secrets_dir size is above {self.secrets_dir_max_size} bytes'
                )

    @staticmethod
    def load_secrets(path: Path) -> Dict[str, str]:
        return {
            str(p.relative_to(path)): p.read_text().strip()
            for p in map(Path, iglob(f'{path}/**/*', recursive=True))
            if p.is_file()
        }

    def __repr__(self) -> str:
        return f'FileSecretsSettingsSource(secrets_dir={self.secrets_dir!r})'

    def __call__(self) -> dict[str, Any]:
        res = super().__call__()
        # breakpoint()  # this is the most informative place to debug
        return res


def first_not_none(*objs: Any) -> Any:
    return next(filter(lambda o: o is not None, objs), None)
