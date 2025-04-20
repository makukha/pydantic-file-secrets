import? '.just/changelog.just'
import? '.just/gh.just'
import? '.just/version.just'

# list available commands
default:
    @just --list

#
# Develop
#

# run once on project creation
[group('develop')]
seed:
    echo -e "#!/usr/bin/env bash\njust pre-commit" > .git/hooks/pre-commit

# initialize dev environment
[group('develop'), macos]
pre:
    sudo port install gh git uv yq

# synchronize dev environment
[group('develop')]
sync:
    chmod ug+x .git/hooks/*
    uv sync --all-extras --all-groups --frozen
    make requirements

# update dev environment
[group('develop')]
upgrade:
    uv sync --all-extras --all-groups --upgrade
    uvx copier update --trust --vcs-ref main

# run linters
[group('develop')]
lint:
    uv run mypy .
    uv run ruff check
    uv run ruff format --diff

[private]
tox-provision:
    time docker compose run --rm -it tox run --notest --skip-pkg-install

# run tests
[group('develop')]
test *toxargs: build
    make tests/requirements.txt
    rm -f .tox/*/.pass-*
    {{ if toxargs == "" { "just tox-provision" } else { "" } }}
    time docker compose run --rm -it tox \
        {{ if toxargs == "" { "run-parallel" } else { "run" } }} \
         --installpkg="$(find dist -name '*.whl')" {{toxargs}}
    make badges
    just docs

# enter testing docker container
[group('develop')]
shell:
    docker compose run --rm -it --entrypoint bash tox

# build python package
[group('develop')]
build: sync
    make build

# build docs
[group('develop')]
docs:
    make docs

#
# Publish
#

# publish package on PyPI
[group('publish')]
pypi-publish: build
    uv publish

#
# Manage
#

# display confirmation prompt
[private]
confirm msg:
    @printf "\n{{msg}}, then press enter " && read

# run pre-commit hook
[group('manage')]
pre-commit:
    just lint
    just docs

# run pre-merge
[group('manage')]
pre-merge:
    just lint
    just docs
    just test

# merge
[group('manage')]
merge:
    just pre-merge
    just gh-create-pr
    just confirm "Merge pull request"
    git switch main
    git fetch
    git pull

# release
[group('manage')]
release:
    just pre-merge
    just bump
    just changelog
    just docs
    just confirm "Proofread the changelog and commit changes"
    just merge
    just gh-repo-upd
    just gh-create-release
    just confirm "Update release notes and publish GitHub release"
    just pypi-publish
