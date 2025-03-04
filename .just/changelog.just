# add changelog entry
[group('project')]
news:
    uv run scriv create

# collect changelog entries
[group('project')]
changelog:
    uv run scriv collect
    sed -e's/^### \(.*\)$/***\1***/; s/\([a-z]\)\*\*\*$/\1***/' -i '' CHANGELOG.md
