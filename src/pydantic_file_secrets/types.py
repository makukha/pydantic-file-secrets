from collections.abc import Sequence
from pathlib import Path
from typing import Literal, Optional, Union

import pydantic_settings
from typing_extensions import TypeAlias

PathType: TypeAlias = Union[Path, str, Sequence[Union[Path, str]]]


class SettingsConfigDict(pydantic_settings.SettingsConfigDict, total=False):
    secrets_dir_missing: Optional[Literal['ok', 'warn', 'error']]
    secrets_dir_max_size: Optional[int]
    secrets_case_sensitive: Optional[bool]
    secrets_prefix: Optional[str]
    secrets_nested_delimiter: Optional[str]
    secrets_nested_subdir: Optional[bool]
