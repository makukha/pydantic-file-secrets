# register git hooks
[group('initialize')]
git-hooks:
    echo -e "#!/usr/bin/env bash\njust pre-commit" > .git/hooks/pre-commit
    chmod a+x .git/hooks/pre-commit
