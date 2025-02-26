import? '.jist/gh.just'
import? '.jist/git.just'
import? '.jist/op.just'
import? '.jist/scriv.just'
import? '.jist/version.just'

# list available commands
default:
    @just --list

# initialize dev environment
[group('initialize'), macos]
init:
    sudo port install gh git uv yq
    just init-hooks
    just sync

# develop

# run linters
[group('develop')]
lint:
    uv run mypy .
    uv run ruff check
    uv run ruff format --diff

# run tests
[group('develop')]
test *toxargs: build
    make tests/requirements.txt
    time docker compose run --rm -it tox \
        {{ if toxargs == "" { "run-parallel" } else { "run" } }} \
         --installpkg="$(find dist -name '*.whl')" {{toxargs}}
    make badges

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

# publish

# publish package on PyPI
[group('publish')]
pypi-publish: build
    uv publish

#
# Management operations
#

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
    just gh-push
    just gh-pr

# release
[group('manage')]
release:
    just pre-merge
    just bump
    just changelog
    just confirm "Proofread the changelog"
    just pre-merge
    just confirm "Commit changes"
    just gh-pr
    just confirm "Merge pull request"
    git switch main
    git fetch
    git pull
    just gh-repo-upd
    just gh-release
    just confirm "Update release notes and publish GitHub release"
    just pypi-publish
