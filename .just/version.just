# bump project version
[group('project')]
bump:
    #!/usr/bin/env bash
    set -euo pipefail
    uv run bump-my-version show-bump
    printf 'Choose version part: '
    read PART
    uv run bump-my-version bump -- "$PART"
    uv lock

# show current version
[group('project')]
version:
    @uv run bump-my-version show current_version 2>/dev/null
