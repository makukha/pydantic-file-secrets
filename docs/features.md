* Plain or nested directory layout: `secrets/dir__key` or `secrets/dir/key`
* Respects `env_prefix`, `env_nested_delimiter` and other [config options](https://github.com/makukha/pydantic-file-secrets?tab=readme-ov-file#configuration-options)
* Implements config options `secrets_prefix`, `secrets_nested_delimiter` [and more](https://github.com/makukha/pydantic-file-secrets?tab=readme-ov-file#configuration-options) to configure secrets and env vars independently
* Drop-in replacement of standard `SecretsSettingsSource`
* Pure Python thin wrapper over standard `EnvSettingsSource`
* No third party dependencies except `pydantic-settings`
* Fully typed
* 100% test coverage
