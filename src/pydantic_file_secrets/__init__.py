from pathlib import Path
from typing import Any, Literal
import warnings

from pydantic.fields import FieldInfo
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsError
from pydantic_settings.utils import path_type_label

from .__version__ import __version__

__all__ = [
    'FileSecretsSettingsSource',
]


type SecretsDirMissing = Literal['ok', 'warn', 'error']


class FileSecretsSettingsSource(PydanticBaseSettingsSource):
    def __init__(
        self,
        settings_cls: type[BaseSettings],
        secrets_dir: str | Path | None = None,
        secrets_dir_missing: SecretsDirMissing | None = None,
        secrets_case_sensitive: bool | None = None,
        secrets_prefix: str | None = None,
        secrets_nested_delimiter: str | None = None,
        secrets_ignore_empty: bool | None = None,
    ) -> None:
        super().__init__(settings_cls)

        self.secrets_dir: str | None = first_not_none(  # todo: test precedence & backwards compatibility
            secrets_dir,
            self.config.get('secrets_dir'),
        )
        self.secrets_dir_missing: SecretsDirMissing | None = first_not_none(  # todo: test backwards compatibility
            secrets_dir_missing,
            self.config.get('secrets_dir_missing'),
            'warn',  # todo: test all options
        )
        self.case_sensitive: bool = first_not_none(  # todo: test precedence & backwards compatibility
            secrets_case_sensitive,
            self.config.get('secrets_case_sensitive'),
            self.config.get('case_sensitive'),
            False,
        )
        self.prefix: str = first_not_none(  # todo: test precedence & backwards compatibility
            secrets_prefix,
            self.config.get('secrets_prefix'),
            self.config.get('env_prefix'),
            '',
        )
        self.nested_delimiter: str | None = first_not_none(  # todo: test precedence & backwards compatibility
            secrets_nested_delimiter,
            self.config.get('secrets_nested_delimiter'),
            self.config.get('env_nested_delimiter'),
        )
        self.ignore_empty: bool = first_not_none(  # todo: test precedence & backwards compatibility
            secrets_ignore_empty,
            self.config.get('secrets_ignore_empty'),
            False,
        )

    def __call__(self) -> dict[str, Any]:

        # provide valid secrets_path
        if self.secrets_dir is None:
            return {}
        self.secrets_path: Path = Path(self.secrets_dir).expanduser()
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
            return {}
        if not self.secrets_path.is_dir():
            raise SettingsError(f'secrets_dir must reference a directory, not a {path_type_label(self.secrets_path)}')


        return {}  # todo: remove
        ###############

        data: dict[str, Any] = {}

        for field_name, field in self.settings_cls.model_fields.items():
            try:
                field_value, field_key, value_is_complex = self.get_field_value(field, field_name)
            except Exception as e:
                raise SettingsError(
                    f'error getting value for field "{field_name}" from source "{self.__class__.__name__}"'
                ) from e

            try:
                field_value = self.prepare_field_value(field_name, field, field_value, value_is_complex)
            except ValueError as e:
                raise SettingsError(
                    f'error parsing value for field "{field_name}" from source "{self.__class__.__name__}"'
                ) from e

            if field_value is not None:
                if self.env_parse_none_str is not None:
                    if isinstance(field_value, dict):
                        field_value = self._replace_env_none_type_values(field_value)
                    elif isinstance(field_value, EnvNoneType):
                        field_value = None
                if (
                    not self.case_sensitive
                    # and lenient_issubclass(field.annotation, BaseModel)
                    and isinstance(field_value, dict)
                ):
                    data[field_key] = self._replace_field_names_case_insensitively(field, field_value)
                else:
                    data[field_key] = field_value

        return data

    def get_field_value(self, field: FieldInfo, field_name: str) -> tuple[Any, str, bool]:
        return (None, field_name, False)  # todo


def dummy():
    if True:
        print('')
    else:
        pass


def first_not_none(*objs) -> Any:
    return next(filter(lambda o: o is not None, objs), None)
