import os
from pathlib import Path
from typing import Any, Literal
import warnings

from pydantic_settings import BaseSettings, EnvSettingsSource, SettingsError
from pydantic_settings.sources import parse_env_vars
from pydantic_settings.utils import path_type_label

from .__version__ import __version__


__all__ = ['__version__', 'FileSecretsSettingsSource']


type SecretsDirMissing = Literal['ok', 'warn', 'error']


class FileSecretsSettingsSource(EnvSettingsSource):
    def __init__(
        self,
        settings_cls: type[BaseSettings],
        secrets_dir: str | Path | None = None,
        secrets_dir_missing: SecretsDirMissing | None = None,
        secrets_dir_max_size: int | None = None,
        secrets_case_sensitive: bool | None = None,
        secrets_prefix: str | None = None,
        secrets_nested_delimiter: str | None = None,
        secrets_nested_subdir: bool | None = None,
    ) -> None:

        # config options
        conf = settings_cls.model_config
        self.secrets_dir: str | None = first_not_none(
            secrets_dir,
            conf.get('secrets_dir'),
        )
        self.secrets_dir_missing: SecretsDirMissing | None = first_not_none(
            secrets_dir_missing,
            conf.get('secrets_dir_missing'),
            'warn',
        )
        self.secrets_dir_max_size: int = first_not_none(
            secrets_dir_max_size,
            conf.get('secrets_dir_max_size'),
            16 * 2 ** 20,  # 8 MiB seems to be a reasonable default
        )
        self.case_sensitive: bool = first_not_none(
            secrets_case_sensitive,
            conf.get('secrets_case_sensitive'),
            conf.get('case_sensitive'),
            False,
        )
        self.secrets_prefix: str = first_not_none(
            secrets_prefix,
            conf.get('secrets_prefix'),
            conf.get('env_prefix'),
            '',
        )

        # nested options
        self.secrets_nested_delimiter: str | None = first_not_none(
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
            self.secrets_path = None
        else:
            self.secrets_path: Path = Path(self.secrets_dir).expanduser().resolve()
            if not self.secrets_path.exists():
                match self.secrets_dir_missing:
                    case 'ok':
                        pass
                    case 'warn':
                        warnings.warn(f'directory "{self.secrets_path}" does not exist')
                    case 'error':
                        raise SettingsError(f'directory "{self.secrets_path}" does not exist')
                    case _:
                        raise SettingsError(f'invalid secrets_dir_missing value: {self.secrets_dir_missing}')
            else:
                if not self.secrets_path.is_dir():
                    raise SettingsError(f'secrets_dir must reference a directory, not a {path_type_label(self.secrets_path)}')
                secrets_dir_size = sum(
                    f.stat().st_size
                    for f in self.secrets_path.glob('**/*')
                    if f.is_file()
                )
                if secrets_dir_size > self.secrets_dir_max_size:
                    raise SettingsError(f'secrets_dir size is above {self.secrets_dir_max_size} bytes')

        # construct parent
        super().__init__(
            settings_cls,
            case_sensitive=self.case_sensitive,
            env_prefix=self.secrets_prefix,
            env_nested_delimiter=self.secrets_nested_delimiter,
            env_ignore_empty=False,  # match SecretsSettingsSource behaviour
            env_parse_none_str=None,  # match SecretsSettingsSource behaviour
            env_parse_enums=True,  # match SecretsSettingsSource behaviour
        )
        self.env_parse_none_str = None  # update manually because of None

        # update parent members
        if self.secrets_path is None:
            self.env_vars = {}
        else:
            secrets = {
                str(p.relative_to(self.secrets_path)): p.read_text()
                for p in self.secrets_path.glob('**/*')
                if p.is_file()
            }
            self.env_vars = parse_env_vars(
                secrets, self.case_sensitive, self.env_ignore_empty, self.env_parse_none_str,
            )

    def __repr__(self) -> str:
        return f'FileSecretsSettingsSource(secrets_dir={self.secrets_dir!r})'

    def __call__(self):
        res = super().__call__()
        # breakpoint()  # this is the most informative place to debug
        return res


def first_not_none(*objs) -> Any:
    return next(filter(lambda o: o is not None, objs), None)