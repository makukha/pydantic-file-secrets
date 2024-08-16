# pydantic-file-secrets 🔑
> Use file secrets in nested [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) models.

![GitHub License](https://img.shields.io/github/license/makukha/pydantic-file-secrets)
[![Tests](https://raw.githubusercontent.com/makukha/pydantic-file-secrets/0.1.3/docs/badge/tests.svg)](https://github.com/makukha/pydantic-file-secrets)
[![Coverage](https://raw.githubusercontent.com/makukha/pydantic-file-secrets/0.1.3/docs/badge/coverage.svg)](https://github.com/makukha/pydantic-file-secrets)
[![linting - Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v1.json)](https://github.com/astral-sh/ruff)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) \
[![pypi](https://img.shields.io/pypi/v/pydantic-file-secrets.svg#0.1.3)](https://pypi.python.org/pypi/pydantic-file-secrets)
[![versions](https://img.shields.io/pypi/pyversions/pydantic-file-secrets.svg)](https://pypi.org/project/pydantic-file-secrets)
[![Pydantic v2](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/pydantic/main/docs/badge/v2.json)](https://pydantic.dev)


This project is inspired by discussions in [pydantic-settings issue #154](https://github.com/pydantic/pydantic-settings/issues/154).

This package unties secrets from environment variables config options and implements other long waited features.


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

Pydantic Settings has a corresponding data source, [`SecretsSettingsSource`](https://docs.pydantic.dev/latest/api/pydantic_settings/#pydantic_settings.SecretsSettingsSource), but it does not load secrets in nested models. For things that DO NOT work in original Pydantic Settings, see [test_pydantic_motivation.py](https://github.com/makukha/pydantic-file-secrets/blob/main/tests/test_pydantic_motivation.py).


## Solution

The new `FileSecretsSettingsSource` is a drop-in replacement of stock `SecretsSettingsSource`.

### Installation

```shell
$ pip install pydantic-file-secrets
```

### Plain secrets directory layout

```text
# /run/secrets/app_key
secret1

# /run/secrets/db__password
secret2
```

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

### Nested secrets directory layout

Config option `secrets_nested_delimiter` overrides `env_nested_delimiter` for files. In particular, this allows to use nested directory layout along with environmemt variables for other non-secret settings:

```text
# /run/secrets/app_key
secret1

# /run/secrets/db/password
secret2
```

```python
...
    model_config = SettingsConfigDict(
        secrets_dir='/run/secrets',
        secrets_nested_subdir=True,
    )
...
```

## Configuration options

### secrets_dir

Path to secrets directory, same as `SecretsSettingsSource.secrets_dir`.

### secrets_dir_missing

If `secrets_dir` does not exist, original `SecretsSettingsSource` issues a warning. However, this may be undesirable, for example if we don't mount Docker Secrets in e.g. dev environment. Now you have a choice:

* `'ok'` — do nothing if `secrets_dir` does not exist
* `'warn'` (default) — print warning, same as `SecretsSettingsSource`
* `'error'` — raise `SettingsError`

### secrets_dir_max_size

Limit the size of `secrets_dir` for security reasons, defaults to 8 MiB.

`FileSecretsSettingsSource` is a thin wrapper around [`EnvSettingsSource`](https://docs.pydantic.dev/latest/api/pydantic_settings/#pydantic_settings.EnvSettingsSource), which loads all potential secrets on initialization. This could lead to `MemoryError` if we mount a large file under `secrets_dir`.

### secrets_case_sensitive

Same as [`case_sensitive`](https://docs.pydantic.dev/latest/concepts/pydantic_settings/#case-sensitivity), but works for secrets only. If not specified, defaults to `case_sensitive`.

### secrets_nested_delimiter

Same as [`env_nested_delimiter`](https://docs.pydantic.dev/latest/concepts/pydantic_settings/#parsing-environment-variable-values), but works for secrets only. If not specified, defaults to `env_nested_delimiter`. This option is used to implement [nested secrets directory layout](https://github.com/makukha/pydantic-file-secrets?tab=readme-ov-file#nested-secrets-directory-layout) and allows to do even nastier things like `/run/secrets/model/delim/nested1/delim/nested2`.

### secrets_nested_subdir

Boolean flag to turn on nested secrets directory mode, `False` by default. If `True`, sets `secrets_nested_delimiter` to [`os.sep`](https://docs.python.org/3/library/os.html#os.sep). Raises `settingsError` if `secrets_nested_delimiter` is already specified.

### secrets_prefix

Secret path prefix, similar to `env_prefix`, but works for secrets only. Defaults to `env_prefix` if not specified. Works in both plain and nested directory modes, like `'/run/secrets/prefix_model__nested'` and `'/run/secrets/prefix_model/nested'`.


### Not supported config options

Some config options that are declared in [`SecretsSettingsSource`](https://docs.pydantic.dev/latest/api/pydantic_settings/#pydantic_settings.SecretsSettingsSource) interface are actually [not working](https://github.com/makukha/pydantic-file-secrets/blob/main/tests/test_pydantic_source.py) and are not supported in `FileSecretsSettingsSource`:

* `env_ignore_empty`
* `env_parse_none_str`
* `env_parse_enums`

However, we [make sure](https://github.com/makukha/pydantic-file-secrets/blob/main/tests/test_ignored_options.py) that the behaviour of `FileSecretsSettingsSource` matches `SecretsSettingsSource` to provide a drop-in replacement, although it is somewhat wierd (e.g. `env_parse_enums` is always `True`).


## Testing

We [ensure](https://raw.githubusercontent.com/makukha/pydantic-file-secrets/main/tox.ini) 100% test coverage for latest Python release (3.12).

We [test](https://raw.githubusercontent.com/makukha/pydantic-file-secrets/main/tox.ini) all minor Pydantic Settings v2 versions and all minor Python 3 versions supported by Pydantic Settings:

* Python 3.13 + pydantic-settings 2.{0,1,2,3,4}
* Python 3.12 + pydantic-settings 2.{0,1,2,3,4}
* Python 3.11 + pydantic-settings 2.{0,1,2,3,4}
* Python 3.10 + pydantic-settings 2.{0,1,2,3,4}
* Python 3.9 + pydantic-settings 2.{0,1,2,3,4}
* Python 3.8 + pydantic-settings 2.{0,1,2,3,4}


## Roadmap

* Support `_FILE` environment variables to set secret file name.
* Per-field secret file name override.


## Authors

* [Michael Makukha](https://github.com/makukha)

## License

[MIT License](https://github.com/makukha/pydantic-file-secrets/blob/main/LICENSE)
