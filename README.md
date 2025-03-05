# pydantic-file-secrets 🔑
<!-- docsub: begin -->
<!-- docsub: exec yq '"> " + .project.description' pyproject.toml -->
> Use file secrets in nested Pydantic Settings models, drop-in replacement for SecretsSettingsSource.
<!-- docsub: end -->

<!-- docsub: begin -->
<!-- docsub: include docs/badges.md -->
[![license](https://img.shields.io/github/license/makukha/pydantic-file-secrets.svg)](https://github.com/makukha/pydantic-file-secrets/blob/main/LICENSE)
[![pypi](https://img.shields.io/pypi/v/pydantic-file-secrets.svg#v0.4.1)](https://pypi.org/project/pydantic-file-secrets)
[![python versions](https://img.shields.io/pypi/pyversions/pydantic-file-secrets.svg)](https://pypi.org/project/pydantic-file-secrets)
[![tests](https://raw.githubusercontent.com/makukha/pydantic-file-secrets/v0.4.1/docs/img/badge/tests.svg)](https://github.com/makukha/pydantic-file-secrets)
[![coverage](https://raw.githubusercontent.com/makukha/pydantic-file-secrets/v0.4.1/docs/img/badge/coverage.svg)](https://github.com/makukha/pydantic-file-secrets)
[![tested with multipython](https://img.shields.io/badge/tested_with-multipython-x)](https://github.com/makukha/multipython)
[![uses docsub](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/makukha/docsub/refs/heads/main/docs/badge/v1.json)](https://github.com/makukha/docsub)
[![mypy](https://img.shields.io/badge/type_checked-mypy-%231674b1)](http://mypy.readthedocs.io)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/ruff)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
<!-- docsub: end -->
[![Pydantic v2](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/pydantic/main/docs/badge/v2.json)](https://pydantic.dev)
[![pypi downloads](https://img.shields.io/pypi/dw/pydantic-file-secrets)](https://pypistats.org/packages/pydantic-file-secrets)


This project is inspired by discussions in Pydantic Settings repository and proposes solution to [#30](https://github.com/pydantic/pydantic-settings/issues/30) and [#154](https://github.com/pydantic/pydantic-settings/issues/154).


# Features

<!-- docsub: begin -->
<!-- docsub: include docs/features.md -->
* Plain or nested directory layout: `secrets/dir__key` or `secrets/dir/key`
* Respects `env_prefix`, `env_nested_delimiter` and other [config options](https://github.com/makukha/pydantic-file-secrets?tab=readme-ov-file#configuration-options)
* Implements config options `secrets_prefix`, `secrets_nested_delimiter` [and more](https://github.com/makukha/pydantic-file-secrets?tab=readme-ov-file#configuration-options) to configure secrets and env vars independently
* Drop-in replacement of standard `SecretsSettingsSource`
* Pure Python thin wrapper over standard `EnvSettingsSource`
* No third party dependencies except `pydantic-settings`
* Fully typed
* 100% test coverage
<!-- docsub: end -->


# Installation

```shell
$ pip install pydantic-file-secrets
```


# Motivation

Nested Pydantic config can contain nested models with secret entries, as well as secrets in top level config. In dockerized environment, these entries may be read from file system, e.g. `/run/secrets` when using Docker Secrets:

```python
from pydantic import BaseModel, Secret
from pydantic_settings import BaseSettings, SettingsConfigDict

class DbSettings(BaseModel):
    user: str
    passwd: Secret[str]  # secret in nested model

class Settings(BaseSettings):
    app_key: Secret[str]  # secret in root model
    db: DbSettings

    model_config = SettingsConfigDict(
        secrets_dir='/run/secrets',
    )
```


# Usage

<!-- docsub: begin #usage.md -->
<!-- docsub: include docs/usage.md -->
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
<!-- docsub: end #usage.md -->


# Configuration options

## secrets_dir

Path to secrets directory. Same as `SecretsSettingsSource.secrets_dir` if `str` or `Path`. If `list`, the last match wins. If `secrets_dir` is passed in both source constructor and model config, values are not merged (constructor takes priority).

## secrets_dir_missing

If `secrets_dir` does not exist, original `SecretsSettingsSource` issues a warning. However, this may be undesirable, for example if we don't mount Docker Secrets in e.g. dev environment. Now you have a choice:

* `'ok'` — do nothing if `secrets_dir` does not exist
* `'warn'` (default) — print warning, same as `SecretsSettingsSource`
* `'error'` — raise `SettingsError`

If multiple `secrets_dir` passed, the same `secrets_dir_missing` action applies to each of them.

## secrets_dir_max_size

Limit the size of `secrets_dir` for security reasons, defaults to `SECRETS_DIR_MAX_SIZE` equal to 16 MiB.

`FileSecretsSettingsSource` is a thin wrapper around [`EnvSettingsSource`](https://docs.pydantic.dev/latest/api/pydantic_settings/#pydantic_settings.EnvSettingsSource), which loads all potential secrets on initialization. This could lead to `MemoryError` if we mount a large file under `secrets_dir`.

If multiple `secrets_dir` passed, the limit applies to each directory independently.

## secrets_case_sensitive

Same as [`case_sensitive`](https://docs.pydantic.dev/latest/concepts/pydantic_settings/#case-sensitivity), but works for secrets only. If not specified, defaults to `case_sensitive`.

## secrets_nested_delimiter

Same as [`env_nested_delimiter`](https://docs.pydantic.dev/latest/concepts/pydantic_settings/#parsing-environment-variable-values), but works for secrets only. If not specified, defaults to `env_nested_delimiter`. This option is used to implement [nested secrets directory layout](https://github.com/makukha/pydantic-file-secrets?tab=readme-ov-file#nested-secrets-directory-layout) and allows to do even nastier things like `/run/secrets/model/delim/nested1/delim/nested2`.

## secrets_nested_subdir

Boolean flag to turn on nested secrets directory mode, `False` by default. If `True`, sets `secrets_nested_delimiter` to [`os.sep`](https://docs.python.org/3/library/os.html#os.sep). Raises `SettingsError` if `secrets_nested_delimiter` is already specified.

## secrets_prefix

Secret path prefix, similar to `env_prefix`, but works for secrets only. Defaults to `env_prefix` if not specified. Works in both plain and nested directory modes, like `'/run/secrets/prefix_model__nested'` and `'/run/secrets/prefix_model/nested'`.


## Not supported config options

Some config options that are declared in [`SecretsSettingsSource`](https://docs.pydantic.dev/latest/api/pydantic_settings/#pydantic_settings.SecretsSettingsSource) interface are actually [not working](https://github.com/makukha/pydantic-file-secrets/blob/main/tests/test_original_source.py) and are not supported in `FileSecretsSettingsSource`:

* `env_ignore_empty`
* `env_parse_none_str`
* `env_parse_enums`

However, we [make sure](https://github.com/makukha/pydantic-file-secrets/blob/main/tests/test_ignored_options.py) that the behaviour of `FileSecretsSettingsSource` matches `SecretsSettingsSource` to provide a drop-in replacement, although it is somewhat wierd (e.g. `env_parse_enums` is always `True`).


# Testing

100% test coverage [is provided](https://raw.githubusercontent.com/makukha/pydantic-file-secrets/main/tox.ini) for latest stable Python release (3.13).

Tests are run for all minor Pydantic Settings v2 versions and all minor Python 3 versions supported by Pydantic Settings:

* Python 3.{8,9,10,11,12,13}
* pydantic-settings v2.{2,3,4,5,6,7,8}


# History

* September 2024 — Multiple `secrets_dir` [feature](https://github.com/pydantic/pydantic-settings/pull/372) was merged to [pydantic-settings v2.5.0](https://github.com/pydantic/pydantic-settings/releases/tag/v2.5.0)


# Authors

* Michael Makukha


# See also

* [Documentation](https://github.com/makukha/pydantic-file-secrets#readme)
* [Changelog](https://github.com/makukha/pydantic-file-secrets/tree/main/CHANGELOG.md)
* [Issues](https://github.com/makukha/pydantic-file-secrets/issues)
* [License](https://github.com/makukha/pydantic-file-secrets/tree/main/LICENSE)
