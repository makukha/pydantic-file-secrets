# add changelog entry
[group('project')]
news:
    uv run scriv create

# collect changelog entries
[group('project')]
changelog:
    uv run scriv collect
    sed -i '' -e 's/^#* \*\*\*/***/' CHANGELOG.md
