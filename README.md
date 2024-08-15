# pydantic-file-secrets 📁🔑
> Use file secrets in nested models of Pydantic Settings.

![GitHub License](https://img.shields.io/github/license/makukha/pydantic-file-secrets)
[![Tests](https://raw.githubusercontent.com/makukha/pydantic-file-secrets/0.1.1/docs/badge/tests.svg)](https://github.com/makukha/pydantic-file-secrets)
[![Coverage](https://raw.githubusercontent.com/makukha/pydantic-file-secrets/0.1.1/docs/badge/coverage.svg)](https://github.com/makukha/pydantic-file-secrets)
[![linting - Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v1.json)](https://github.com/astral-sh/ruff)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) \
[![pypi](https://img.shields.io/pypi/v/pydantic-file-secrets.svg#0.1.1)](https://pypi.python.org/pypi/pydantic-file-secrets)
[![versions](https://img.shields.io/pypi/pyversions/pydantic-file-secrets.svg)](https://pypi.org/project/pydantic-file-secrets)
[![Pydantic v2](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/pydantic/main/docs/badge/v2.json)](https://pydantic.dev)


This package is inspired by and based on discussions in [pydantic-settings issue #154](https://github.com/pydantic/pydantic-settings/issues/154).


## Features

* Use secret file source in nested settings models
* Drop-in replacement of standard `SecretsSettingsSource`
* Plain or nested directory layout: `/run/secrets/dir__key` or `/run/secrets/dir/key`
* Respects `env_prefix`, `env_nested_delimiter` and other [config options](https://github.com/makukha/pydantic-file-secrets?tab=readme-ov-file#configuration-options)
* Has `secrets_prefix`, `secrets_nested_delimiter`, [etc.](https://github.com/makukha/pydantic-file-secrets?tab=readme-ov-file#configuration-options) to configure secrets and env vars separately
* Pure Python thin wrapper over standard `EnvSettingsSource`
* No third party dependencies except `pydantic-settings`
* 100% test coverage


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

Pydantic Settings has a corresponding data source, [`SecretsSettingsSource`](https://docs.pydantic.dev/latest/api/pydantic_settings/#pydantic_settings.SecretsSettingsSource), but it does not load secrets in nested models. For methods that ***do not*** work in original Pydantic Settings, see [test_pydantic_motivation.py](https://github.com/makukha/pydantic-file-secrets/blob/main/tests/test_pydantic_motivation.py).


## Solution

The new `FileSecretsSettingsSource` is a drop-in replacement of stock `SecretsSettingsSource`.

### Installation

```shell
$ pip install pydantic-file-secrets
```

### Plain directory layout

| file                        | content   |
|-----------------------------|-----------|
| `/run/secrets/app_key`      | `secret1` |
| `/run/secrets/db__password` | `secret2` |

```python
from pydantic import BaseModel, Secret
from pydantic_file_secrets import FileSecretsSettingsSource
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
            FileSecretsSettingsSource(settings_cls),
        )

```

### Secrets in subdirectories

Config option `secrets_nested_delimiter` overrides `env_nested_delimiter` for files. In particular, this allows to use nested directory layout along with environmemt variables for other non-secret settings:

| file                       | content   |
|----------------------------|-----------|
| `/run/secrets/app_key`     | `secret1` |
| `/run/secrets/db/password` | `secret2` |

```python
...
    model_config = SettingsConfigDict(
        secrets_dir='/run/secrets',
        secrets_nested_subdir=True,
    )
...
```

## Configuration options

TODO


## Roadmap

* Support `_FILE` environment variables to set secret file name.
* Per-field secret file name override.


## Changelog
