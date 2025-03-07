# create GitHub pull request
[group('github')]
gh-create-pr:
    just gh-push
    gh pr create --web -t "$(just gh-issue-title)"

# create GitHub release
[group('github')]
gh-create-release:
    #!/usr/bin/env bash
    set -euo pipefail
    if [ "$(git branch --show-current)" != "main" ]; then
        echo "Can release from main branch only"
        exit 1
    fi
    tag="v$(just version)"
    git tag --force "$tag" HEAD
    git push origin tag "$tag"
    gh release create --draft -t "$tag — $(date -Idate)" --generate-notes "$tag"

# get issue id of current GitHub branch
[group('github')]
gh-issue-id:
    @git branch --show-current | cut -d- -f1

# get issue title of current GitHub branch
[group('github')]
gh-issue-title:
    @GH_PAGER=cat gh issue view "$(just gh-issue-id)" --json title -t '{{{{.title}}'

# push all GitHub commits after ensuring the clean state
[group('github')]
gh-push:
    # ensure clean state
    git diff --exit-code
    git diff --cached --exit-code
    git ls-files --other --exclude-standard --directory
    git push

# get "org/name" of current GitHub repository
[group('github')]
gh-repo-name:
    @git config --get remote.origin.url | sed 's|.*/\(.*/.*\)\.git$|\1|'

# update GitHub repository metadata from pyproject.toml
[group('github')]
gh-repo-upd:
    #!/usr/bin/env bash
    set -euo pipefail
    # update description
    gh repo edit -d "$(yq .project.description pyproject.toml)"
    # update homepage
    homepage="$(yq .project.urls.Documentation pyproject.toml)"
    if [[ $homepage != "https://github.com"* ]]; then
      gh repo edit -h "$homepage"
    fi
    # delete old topics
    old_topics="$(GH_PAGER=cat gh api repos/$(just gh-repo-name) | yq -r '.topics | join(" ")')"
    if [ -n "$old_topics" ]; then
      gh repo edit $(sed 's/ / --remove-topic /g' <<<" $old_topics")
    fi
    # add new topics
    new_topics="$(yq -r '.project.keywords | join(" ")' pyproject.toml)"
    gh repo edit $(sed 's/ / --add-topic /g' <<<" $new_topics")
    # provide community support
    gh label create "code of conduct" --force -c D73A4A -d "Code of Conduct issues"
