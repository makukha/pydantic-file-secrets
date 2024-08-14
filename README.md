# pydantic-file-secrets
> Use file secrets in nested models of Pydantic Settings.

[![license](https://img.shields.io/github/license/makukha/pydantic-file-secrets.svg)](https://github.com/makukha/pydantic-file-secrets/blob/main/LICENSE)
[![Tests](https://raw.githubusercontent.com/makukha/pydantic-file-secrets/0.1.0a1/docs/badge/tests.svg)](https://github.com/makukha/pydantic-file-secrets)
[![Coverage](https://raw.githubusercontent.com/makukha/pydantic-file-secrets/0.1.0a1/docs/badge/coverage.svg)](https://github.com/makukha/pydantic-file-secrets)
[![types - Mypy](https://img.shields.io/badge/types-Mypy-green.svg)](https://github.com/python/mypy)
[![linting - Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v1.json)](https://github.com/astral-sh/ruff) \
[![pypi](https://img.shields.io/pypi/v/pydantic-file-secrets.svg#0.1.0a1)](https://pypi.python.org/pypi/pydantic-file-secrets)
[![versions](https://img.shields.io/pypi/pyversions/pydantic-file-secrets.svg)](https://pypi.org/project/pydantic-file-secrets)

This package is inspired by and based on discussions in [pydantic-settings issue #154](https://github.com/pydantic/pydantic-settings/issues/154).

## Features

* File secret values in nested settings models
* Plain or nested directory layout: `/run/secrets/topic__key` or `/run/secrets/topic/key`
* Drop-in replacement of standard `SecretsSettingsSource`
* Respects `env_nested_delimiter` and other [config options](#configuration-options)
* Configured independently but with a fallback to `EnvSettingsSource`

## Motivation

Nested Pydantic config can contain nested models with secret entries, as well as secrets in top level config. In dockerized environment, these entries may be read from file system, e.g. `/run/secrets` when using Docker Secrets:

```python
from pydantic import BaseModel, Secret
from pydantic_settings import BaseSettings, SettingsConfigDict

class DbSettings(BaseModel):
    user: str
    password: Secret[str]  # secret in nested model

class Settings(BaseSettings):
    db: DbSettings
    app_key: Secret[str]  # secret in root config

    model_config = SettingsConfigDict(
        secrets_dir='/run/secrets',
    )
```

Pydantic has a corresponding data source, [`SecretsSettingsSource`](https://docs.pydantic.dev/latest/api/pydantic_settings/#pydantic_settings.SecretsSettingsSource), but it does not load secrets in nested models. For methods that ***do not*** work in original Pydantic Settings, see [tests/test_pydantic.py]().


## Solution

The new `FileSecretsSettingsSource` is a drop-in replacement of stock `SecretsSettingsSource`.

```shell
$ pip install pydantic-file-secrets
```

| file                        | content  |
|-----------------------------|----------|
| `/run/secrets/app_key`      | `secret` |
| `/run/secrets/db__password` | `secret` |

```python
from pydantic import BaseModel, Secret
from pydantic_file_secrets import FileSecretsSettingsSource  # 1
from pydantic_settings import BaseSettings, SettingsConfigDict

class DbSettings(BaseModel):
    user: str
    password: Secret[str]

class Settings(BaseSettings):
    db: DbSettings
    app_key: Secret[str]

    model_config = SettingsConfigDict(
        secrets_dir='/run/secrets',
        env_nested_delimiter='__',
    )
    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ):
        return (
            env_settings,
            init_settings,
            FileSecretsSettingsSource(file_secret_settings),  # 2
        )

```

### Custom delimiter

Config option `secrets_nested_delimiter` overrides `env_nested_delimiter` for files. In particular, this allows to use nested directory layout:

| file                       | content  |
|----------------------------|----------|
| `/run/secrets/app_key`     | `secret` |
| `/run/secrets/db/password` | `secret` |

```python
...
    model_config = SettingsConfigDict(
        secrets_dir='/run/secrets',
        env_nested_delimiter='__',
        secrets_nested_delimiter='/',
    )
...
```

## Configuration options

TODO


## Roadmap

* Support `_FILE` environment variables.
* Support per-field secret file name override.


## Changelog
