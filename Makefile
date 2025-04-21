SHELL = /usr/bin/env sh -eu

FORCE:

# requirements

.PHONY: requirements
requirements: tests/requirements.txt
tests/requirements.txt: pyproject.toml uv.lock
	uv export --frozen --no-emit-project --no-hashes --only-group testing > $@

# build

.PHONY: build
build: dist/pkg
dist/pkg: src/**/* README.md pyproject.toml uv.lock
	rm -rf $@
	uv build -o dist/pkg
README.md: docs/*.md
%.md: FORCE
	uv run docsub sync -i $@
uv.lock: pyproject.toml
	uv lock

# docs

.PHONY: docs
docs: README.md

# sources

.PHONY: sources
sources: badges requirements README.md

.PHONY: badges
badges: docs/img/badge/coverage.svg docs/img/badge/tests.svg
docs/img/badge/%.svg: .tmp/%.xml
	mkdir -p $(@D)
	uv run genbadge $* --local -i $< -o $@
