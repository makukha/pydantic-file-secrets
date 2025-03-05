## Plain secrets directory layout

<!-- docsub: begin -->
<!-- docsub: x dirtree tests/test_usage.py:UsagePlain.secrets_dir -->
<!-- docsub: lines after 1 upto -1 -->
```text
📂 secrets
├── 📄 app_key
└── 📄 db__passwd
```
<!-- docsub: end -->

<!-- docsub: begin -->
<!-- docsub: include tests/usage/plain.py -->
<!-- docsub: lines after 1 upto -1 -->
```python
from pydantic import BaseModel, Secret
from pydantic_file_secrets import FileSecretsSettingsSource, SettingsConfigDict
from pydantic_settings import BaseSettings
from pydantic_settings.sources import PydanticBaseSettingsSource


class DbSettings(BaseModel):
    passwd: Secret[str]


class Settings(BaseSettings):
    app_key: Secret[str]
    db: DbSettings

    model_config = SettingsConfigDict(
        secrets_dir='secrets',
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            FileSecretsSettingsSource(file_secret_settings),
        )
```
<!-- docsub: end -->

<!-- docsub: begin -->
<!-- docsub: x cases tests/test_usage.py UsagePlain -->
```pycon
>>> Settings().model_dump()
{'app_key': Secret('**********'), 'db': {'passwd': Secret('**********')}}
```

<!-- docsub: end -->


## Nested secrets directory layout

Config option `secrets_nested_delimiter` overrides `env_nested_delimiter` for files. In particular, this allows to use nested directory layout along with environmemt variables for other non-secret settings:


<!-- docsub: begin -->
<!-- docsub: x dirtree tests/test_usage.py:UsageNested.secrets_dir -->
<!-- docsub: lines after 1 upto -1 -->
```text
📂 secrets
├── 📄 app_key
└── 📂 db
    └── 📄 passwd
```
<!-- docsub: end -->

<!-- docsub: begin -->
<!-- docsub: exec sed -n '/ *model_config =/,/ *)/p' tests/usage/nested.py -->
<!-- docsub: lines after 1 upto -1 -->
```python
    model_config = SettingsConfigDict(
        secrets_dir='secrets',
        secrets_nested_subdir=True,
    )
```
<!-- docsub: end -->

<!-- docsub: begin -->
<!-- docsub: x cases tests/test_usage.py UsageNested -->
```pycon
>>> Settings().model_dump()
{'app_key': Secret('**********'), 'db': {'passwd': Secret('**********')}}
```

<!-- docsub: end -->


## Multiple `secrets_dir`


<!-- docsub: begin -->
<!-- docsub: x dirtree tests/test_usage.py:UsageMultiple.secrets_dir -->
<!-- docsub: lines after 1 upto -1 -->
```text
📂 secrets
├── 📂 layer1
│   └── 📄 app_key
└── 📂 layer2
    └── 📄 db__passwd
```
<!-- docsub: end -->

<!-- docsub: begin -->
<!-- docsub: exec sed -n '/ *model_config =/,/ *)/p' tests/usage/multiple.py -->
<!-- docsub: lines after 1 upto -1 -->
```python
    model_config = SettingsConfigDict(
        secrets_dir=['secrets/layer1', 'secrets/layer2'],
    )
```
<!-- docsub: end -->

<!-- docsub: begin -->
<!-- docsub: x cases tests/test_usage.py UsageMultiple -->
```pycon
>>> Settings().model_dump()
{'app_key': Secret('**********'), 'db': {'passwd': Secret('**********')}}
```

<!-- docsub: end -->


## Syntactic sugar 🍰 — experimental 🧪

> [!CAUTION]
> This syntax may change on any release. Pin current `pydantic-file-secrets` version if decided to use it.

Few important things to note:

- `@with_builtin_sources` decorator provides `NamedTuple` argument, sources names don't need to be copied anymore
- `BaseSource` alias is shorter than `PydanticBaseSettingsSource` and is easier to use in type hints
- `settings_cls` was removed from `settings_customise_sources` signature, probably `cls` is sufficient

<!-- docsub: begin -->
<!-- docsub: include tests/usage/sugar.py -->
<!-- docsub: lines after 1 upto -1 -->
```python
from pydantic import BaseModel, Secret
from pydantic_file_secrets import (
    BaseSource,
    BuiltinSources,
    FileSecretsSettingsSource,
    SettingsConfigDict,
    with_builtin_sources,
)
from pydantic_settings import BaseSettings


class DbSettings(BaseModel):
    passwd: Secret[str]


class Settings(BaseSettings):
    app_key: Secret[str]
    db: DbSettings

    model_config = SettingsConfigDict(
        secrets_dir='secrets',
        secrets_nested_delimiter='__',
    )

    @classmethod
    @with_builtin_sources
    def settings_customise_sources(cls, src: BuiltinSources) -> tuple[BaseSource, ...]:
        return (
            src.init_settings,
            src.env_settings,
            src.dotenv_settings,
            FileSecretsSettingsSource(src.file_secret_settings),
        )
```
<!-- docsub: end -->

<!-- docsub: begin -->
<!-- docsub: x cases tests/test_usage.py UsageSugar -->
```pycon
>>> Settings().model_dump()
{'app_key': Secret('**********'), 'db': {'passwd': Secret('**********')}}
```

<!-- docsub: end -->
