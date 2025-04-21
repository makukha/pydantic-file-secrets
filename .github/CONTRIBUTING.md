# Contribution Guidelines

We would appreciate your contributions:

- [Feature requests and bug reports](https://github.com/makukha/pydantic-file-secrets/issues)
- [Security vulnerability reports](https://github.com/makukha/pydantic-file-secrets/blob/main/.github/SECURITY.md)
- Pull requests

## Pull requests

If the change proposed is not trivial, like typo in docs, please create an issue first.

### Prerequisites

You will need:

- [uv](https://docs.astral.sh/uv/)
- [Just](https://just.systems/man/en/)
- [GNU make](https://www.gnu.org/software/make/make.html)
- [Docker](https://www.docker.com) or [Podman](https://podman.io)
- [Git](https://git-scm.com)
- [yq](https://mikefarah.gitbook.io/yq)

If your OS is macOS or Linux, some of them will be installed by `just init`.

### Initialize dev environment

- Fork project repository [makukha/pydantic-file-secrets](https://github.com/makukha/pydantic-file-secrets) under your account.
- Create feature branch in your fork.
- Clone and install Python packages:

    ```shell
    git clone https://github.com/<YOUR_USER_NAME>/pydantic-file-secrets.git
    just init build
    ```

### Write code

It is convenient to start from adding tests reproducing the bug or shaping the new
feature. All added code must be covered with tests.

The code will be checked with [Ruff](https://github.com/astral-sh/ruff) and
[mypy](https://mypy.readthedocs.io). See `pyproject.toml` for details.

### Run lint and format checks

```shell
just lint
```

There must be no errors.

### Run tests

* Fast, the "main" configuration only:

    ```shell
    just test -m main
    ```

    Coverage report is generated as part of "main" configuration.
    Every new PR must not decrease the code coverage.

* The whole test matrix (will take some time):

    ```shell
    just test
    ```
* Debug single failing tox environment other than "main":

    ```shell
    just test -e <TOX ENV NAME>
    ```

    See `tox.ini` for details.

### Build package and docs

```shell
just build
```

There must be no errors.

### Add changelog entry

```shell
just news
```

Edit the new `*.md` file added under `NEWS.d/`: uncomment the appropriate
section and describe what was done in your pull request.

### Create pull request

The project maintainers will get back to review your PR.

Thank you for your valuable contribution!
