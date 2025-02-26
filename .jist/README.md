# Just-based templates

## Usage

1. Generate skeleton

```shell
wget https://github.com/makukha/jist/archive/refs/heads/main.zip
unzip -j main.zip -x '*/*/*' -d .jist
rm main.zip
```
```shell
uvx cookiecutter gh:makukha/jist/python -fs -o ..
```

2. Update `pyproject.toml`
