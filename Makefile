SHELL=/bin/bash -euo pipefail

.PHONY: build
build: dist
dist: src/**/* pyproject.toml README.md uv.lock
	uv lock
	rm -rf $@
	uv build

.PHONY: badges
badges: docs/img/badge/coverage.svg docs/img/badge/tests.svg
docs/img/badge/%.svg: .tmp/%.xml
	mkdir -p $(@D)
	uv run genbadge $* --local -i $< -o $@

.PHONY: requirements
requirements: tests/requirements.txt
tests/requirements.txt: pyproject.toml uv.lock
	uv export --frozen --no-emit-project --no-hashes --only-group testing > $@

.PHONY: docs
docs: README.md

README.md: FORCE
	uv run docsub sync -i $@

FORCE:
