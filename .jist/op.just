# display confirmation prompt
[private]
confirm msg:
    @printf "\n{{msg}}, then press enter " && read

# synchronize dev environment
[group('develop')]
sync:
    rm -rf .jist
    wget https://github.com/makukha/jist/archive/refs/heads/main.zip
    unzip -j main.zip -x '*/*/*' -d .jist
    rm main.zip
    uv sync --all-extras --all-groups

# update dev environment
[group('develop')]
upgrade:
    uv sync --all-extras --all-groups --upgrade
