from collections.abc import Callable, Sequence
from functools import wraps
from pathlib import Path
from typing import NamedTuple, Tuple, Type, TypeVar, Union

from pydantic_settings import BaseSettings
from pydantic_settings.sources import PydanticBaseSettingsSource
from typing_extensions import TypeAlias


PathType: TypeAlias = Union[Path, str, Sequence[Union[Path, str]]]


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
