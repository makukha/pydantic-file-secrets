from collections.abc import Callable
from functools import wraps
from typing import Literal, NamedTuple, Optional, Tuple, Type, TypeVar

from pydantic_settings import BaseSettings, SettingsConfigDict as BaseSettingsConfigDict
from pydantic_settings.sources import PydanticBaseSettingsSource
from typing_extensions import TypeAlias


class SettingsConfigDict(BaseSettingsConfigDict, total=False):
    secrets_dir_missing: Optional[Literal['ok', 'warn', 'error']]
    secrets_dir_max_size: Optional[int]
    secrets_case_sensitive: Optional[bool]
    secrets_prefix: Optional[str]
    secrets_nested_delimiter: Optional[str]
    secrets_nested_subdir: Optional[bool]


# settings customise sources: syntactic sugar


T = TypeVar('T', bound=Type[BaseSettings])
BaseSource: TypeAlias = PydanticBaseSettingsSource


class BuiltinSources(NamedTuple):
    init_settings: PydanticBaseSettingsSource
    env_settings: PydanticBaseSettingsSource
    dotenv_settings: PydanticBaseSettingsSource
    file_secret_settings: PydanticBaseSettingsSource


def with_builtin_sources(
    method: Callable[[T, BuiltinSources], Tuple[BaseSource, ...]],
) -> Callable[
    [
        T,
        Type[BaseSettings],
        PydanticBaseSettingsSource,
        PydanticBaseSettingsSource,
        PydanticBaseSettingsSource,
        PydanticBaseSettingsSource,
    ],
    Tuple[BaseSource, ...],
]:
    @wraps(method)
    def simple(
        cls: T,
        setting_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[BaseSource, ...]:
        args = BuiltinSources(
            init_settings=init_settings,
            env_settings=env_settings,
            dotenv_settings=dotenv_settings,
            file_secret_settings=file_secret_settings,
        )
        return method(cls, args)

    return simple
