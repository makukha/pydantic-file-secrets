# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

- See upcoming changes in [News directory](https://github.com/makukha/pydantic-file-secrets/tree/main/NEWS.d)

<!-- scriv-insert-here -->

<a id='changelog-0.4.2'></a>
## [0.4.2](https://github.com/makukha/pydantic-file-secrets/releases/tag/v0.4.2) — 2025-03-06

***Added 🌿***

- Added changelog managed with [Scriv](https://scriv.readthedocs.io)

***Experimental 🧪***

- Proposed new simplified pydantic-settings sources customization using `@with_builtin_sources` decorator

***Fixed***

- Typing errors reported in [#30](https://github.com/makukha/pydantic-file-secrets/issues/30)

- Documentation bug for maximum secrets dir size that was documented as 8 MiB while it was actually 16 MiB

- Maximum secrets dir size is exposed as `SECRETS_DIR_MAX_SIZE` constant (it was hard-coded before)

***Docs***

- Added test report and directory layout visualization

***Misc***

- Added tests for pydantic-settings version 2.8

- Added mypy tests for pydantic-settings version 2.5+

- Started using [Copier](https://copier.readthedocs.io) project template

- Started using [multipython](https://github.com/makukha/multipython) image for testing

- Started using [dirlay](https://github.com/makukha/dirlay) in tests

- Started using [docsub](https://github.com/makukha/docsub)

- Started using [just](https://just.systems)

## Prior releases

- See [GitHub release notes](https://github.com/makukha/pydantic-file-secrets/releases)
