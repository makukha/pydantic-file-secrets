* Use secret file source in nested settings models
* Plain or nested directory layout: `/run/secrets/dir__key` or `/run/secrets/dir/key`
* Respects `env_prefix`, `env_nested_delimiter` and other [config options](https://github.com/makukha/pydantic-file-secrets?tab=readme-ov-file#configuration-options)
* Implements config options `secrets_prefix`, `secrets_nested_delimiter`, [etc.](https://github.com/makukha/pydantic-file-secrets?tab=readme-ov-file#configuration-options) to configure secrets and env vars independently
* Drop-in replacement of standard `SecretsSettingsSource`
* Can be used to monkey patch `SecretsSettingsSource`
* Pure Python thin wrapper over standard `EnvSettingsSource`
* No third party dependencies except `pydantic-settings`
* 100% test coverage
