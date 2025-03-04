# pydantic-file-secrets 🔑

> Use file secrets in nested [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) models, drop-in replacement for `SecretsSettingsSource`.

<!-- docsub: begin -->
<!-- docsub: include docs/badges.md -->
[![license](https://img.shields.io/github/license/makukha/pydantic-file-secrets.svg)](https://github.com/makukha/pydantic-file-secrets/blob/main/LICENSE)
[![pypi](https://img.shields.io/pypi/v/pydantic-file-secrets.svg#v0.4.1)](https://pypi.org/project/pydantic-file-secrets)
[![python versions](https://img.shields.io/pypi/pyversions/pydantic-file-secrets.svg)](https://pypi.org/project/pydantic-file-secrets)
[![tests](https://raw.githubusercontent.com/makukha/pydantic-file-secrets/v0.4.1/docs/img/badge/tests.svg)](https://github.com/makukha/pydantic-file-secrets)
[![coverage](https://raw.githubusercontent.com/makukha/pydantic-file-secrets/v0.4.1/docs/img/badge/coverage.svg)](https://github.com/makukha/pydantic-file-secrets)
[![pypi downloads](https://img.shields.io/pypi/dw/pydantic-file-secrets)](https://pypistats.org/packages/pydantic-file-secrets)
[![tested with multipython](https://img.shields.io/badge/tested_with-multipython-x)](https://github.com/makukha/multipython)
[![uses docsub](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/makukha/docsub/refs/heads/main/docs/badge/v1.json)](https://github.com/makukha/docsub)
[![mypy](https://img.shields.io/badge/type_checked-mypy-%231674b1)](http://mypy.readthedocs.io)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/ruff)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
<!-- docsub: end -->

This project is inspired by discussions in Pydantic Settings and solves problems in issues [#30](https://github.com/pydantic/pydantic-settings/issues/30), [#154](https://github.com/pydantic/pydantic-settings/issues/154).


## Features

* Use secret file source in nested settings models
* Plain or nested directory layout: `/run/secrets/dir__key` or `/run/secrets/dir/key`
* Respects `env_prefix`, `env_nested_delimiter` and other [config options](https://github.com/makukha/pydantic-file-secrets?tab=readme-ov-file#configuration-options)
* Implements config options `secrets_prefix`, `secrets_nested_delimiter`, [etc.](https://github.com/makukha/pydantic-file-secrets?tab=readme-ov-file#configuration-options) to configure secrets and env vars independently
* Drop-in replacement of standard `SecretsSettingsSource`
* Can be used to monkey patch `SecretsSettingsSource`
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
    passwd: Secret[str]  # secret in nested model

class Settings(BaseSettings):
    app_key: Secret[str]  # secret in root model
    db: DbSettings

    model_config = SettingsConfigDict(
        secrets_dir='/run/secrets',
    )
```

Pydantic Settings has a corresponding data source, [`SecretsSettingsSource`](https://docs.pydantic.dev/latest/api/pydantic_settings/#pydantic_settings.SecretsSettingsSource), but it does not load secrets in nested models. For things that DO NOT work in original Pydantic Settings, see [test_pydantic_motivation.py](https://github.com/makukha/pydantic-file-secrets/blob/main/tests/test_motivation.py).


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

# /run/secrets/db__passwd
secret2
```

```python
from pydantic import BaseModel, Secret
from pydantic_file_secrets import FileSecretsSettingsSource
from pydantic_settings import BaseSettings, SettingsConfigDict

class DbSettings(BaseModel):
    user: str
    passwd: Secret[str]

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
            init_settings,
            env_settings,
            dotenv_settings,
            FileSecretsSettingsSource(file_secret_settings),
        )

```

### Nested secrets directory layout

Config option `secrets_nested_delimiter` overrides `env_nested_delimiter` for files. In particular, this allows to use nested directory layout along with environmemt variables for other non-secret settings:

```text
# /run/secrets/app_key
secret1

# /run/secrets/db/passwd
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

### Multiple `secrets_dir`

When passing `list` to `secrets_dir`, last match wins.

```python
...
    model_config = SettingsConfigDict(
        secrets_dir=['/run/configs/', '/run/secrets'],
    )
...
```

## Configuration options

### secrets_dir

Path to secrets directory. Same as `SecretsSettingsSource.secrets_dir` if `str` or `Path`. If `list`, the last match wins. If `secrets_dir` is passed in both source constructor and model config, values are not merged (constructor takes priority).

### secrets_dir_missing

If `secrets_dir` does not exist, original `SecretsSettingsSource` issues a warning. However, this may be undesirable, for example if we don't mount Docker Secrets in e.g. dev environment. Now you have a choice:

* `'ok'` — do nothing if `secrets_dir` does not exist
* `'warn'` (default) — print warning, same as `SecretsSettingsSource`
* `'error'` — raise `SettingsError`

If multiple `secrets_dir` passed, the same `secrets_dir_missing` action applies to each of them.

### secrets_dir_max_size

Limit the size of `secrets_dir` for security reasons, defaults to `SECRETS_DIR_MAX_SIZE` equal to 16 MiB.

`FileSecretsSettingsSource` is a thin wrapper around [`EnvSettingsSource`](https://docs.pydantic.dev/latest/api/pydantic_settings/#pydantic_settings.EnvSettingsSource), which loads all potential secrets on initialization. This could lead to `MemoryError` if we mount a large file under `secrets_dir`.

If multiple `secrets_dir` passed, the limit applies to each directory independently.

### secrets_case_sensitive

Same as [`case_sensitive`](https://docs.pydantic.dev/latest/concepts/pydantic_settings/#case-sensitivity), but works for secrets only. If not specified, defaults to `case_sensitive`.

### secrets_nested_delimiter

Same as [`env_nested_delimiter`](https://docs.pydantic.dev/latest/concepts/pydantic_settings/#parsing-environment-variable-values), but works for secrets only. If not specified, defaults to `env_nested_delimiter`. This option is used to implement [nested secrets directory layout](https://github.com/makukha/pydantic-file-secrets?tab=readme-ov-file#nested-secrets-directory-layout) and allows to do even nastier things like `/run/secrets/model/delim/nested1/delim/nested2`.

### secrets_nested_subdir

Boolean flag to turn on nested secrets directory mode, `False` by default. If `True`, sets `secrets_nested_delimiter` to [`os.sep`](https://docs.python.org/3/library/os.html#os.sep). Raises `SettingsError` if `secrets_nested_delimiter` is already specified.

### secrets_prefix

Secret path prefix, similar to `env_prefix`, but works for secrets only. Defaults to `env_prefix` if not specified. Works in both plain and nested directory modes, like `'/run/secrets/prefix_model__nested'` and `'/run/secrets/prefix_model/nested'`.


### Not supported config options

Some config options that are declared in [`SecretsSettingsSource`](https://docs.pydantic.dev/latest/api/pydantic_settings/#pydantic_settings.SecretsSettingsSource) interface are actually [not working](https://github.com/makukha/pydantic-file-secrets/blob/main/tests/test_pydantic_source.py) and are not supported in `FileSecretsSettingsSource`:

* `env_ignore_empty`
* `env_parse_none_str`
* `env_parse_enums`

However, we [make sure](https://github.com/makukha/pydantic-file-secrets/blob/main/tests/test_ignored_options.py) that the behaviour of `FileSecretsSettingsSource` matches `SecretsSettingsSource` to provide a drop-in replacement, although it is somewhat wierd (e.g. `env_parse_enums` is always `True`).


## Testing

100% test coverage [is ensured](https://raw.githubusercontent.com/makukha/pydantic-file-secrets/main/tox.ini) for latest stable Python release (3.13).

Tests are run for all minor Pydantic Settings v2 versions and all minor Python 3 versions supported by Pydantic Settings:

* Python 3.{8,9,10,11,12,13}
* pydantic-settings v2.{2,3,4,5,6,7,8}


## History

* Several `secrets_dir` features were [ported](https://github.com/pydantic/pydantic-settings/releases/tag/v2.5.0) to `pydantic-settings` version 2.5.0


## Authors

* [Michael Makukha](https://github.com/makukha)

## License

[MIT License](https://github.com/makukha/pydantic-file-secrets/blob/main/LICENSE)

## Changelog

* [Project changelog](https://github.com/makukha/pydantic-file-secrets/tree/main/CHANGELOG.md)
* [GitHub release notes](https://github.com/makukha/pydantic-file-secrets/releases)
