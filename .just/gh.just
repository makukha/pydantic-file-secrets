mod git


default:

# get issue id of current GitHub branch
[no-cd]
issue-id:
    @git branch --show-current | cut -d- -f1

# get issue title of current GitHub branch
[no-cd]
issue-title:
    @GH_PAGER=cat gh issue view "$(just gh::issue-id)" --json title -t '{{{{.title}}'

# create GitHub pull request
[no-cd]
pr-create:
    #!/usr/bin/env sh
    set -eu
    just git::push
    TITLE=
    gh pr create --web -t "$(just gh::issue-title)"

# create GitHub release
[no-cd]
release-create tag:
    #!/usr/bin/env sh
    set -eu
    if [ "$(git branch --show-current)" != "main" ]; then
        echo "Can release from main branch only"
        exit 1
    fi
    git push origin tag "{{tag}}"
    gh release create --draft -t "{{tag}} — $(date -Idate)" --generate-notes "{{tag}}"

# get "org/name" of current GitHub repository
[no-cd]
repo-name:
    @git config --get remote.origin.url | sed 's|.*/\(.*/.*\)\.git$|\1|'

# update GitHub repository metadata from pyproject.toml
[no-cd]
repo-update:
    #!/usr/bin/env bash
    set -eu
    # update description
    gh repo edit -d "$(yq .project.description pyproject.toml)"
    # update homepage
    homepage="$(yq .project.urls.Documentation pyproject.toml)"
    if [[ $homepage != "https://github.com"* ]]; then
      gh repo edit -h "$homepage"
    fi
    # delete old topics
    old_topics="$(GH_PAGER=cat gh api repos/$(just gh::repo-name) | yq -r '.topics | join(" ")')"
    if [ -n "$old_topics" ]; then
      gh repo edit $(sed 's/ / --remove-topic /g' <<<" $old_topics")
    fi
    # add new topics
    new_topics="$(yq -r '.project.keywords | join(" ")' pyproject.toml)"
    gh repo edit $(sed 's/ / --add-topic /g' <<<" $new_topics")
    # provide community support
    gh label create "code of conduct" --force -c D73A4A -d "Code of Conduct issues"
