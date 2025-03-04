## Plain secrets directory layout

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

## Nested secrets directory layout

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

## Multiple `secrets_dir`

When passing `list` to `secrets_dir`, last match wins.

```python
...
    model_config = SettingsConfigDict(
        secrets_dir=['/run/configs/', '/run/secrets'],
    )
...
```
