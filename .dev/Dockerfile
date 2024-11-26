FROM makukha/multipython:latest

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    --mount=type=bind,from=dattached/bootstrap,dst=/b \
<<EOT
apt-get update
bash /b/debian-apt-install-devtools.sh
rm -rf /tmp/* /var/tmp/*
EOT

RUN --mount=type=cache,dst=/root/.cache/pip \
    pip install uv

COPY .dev/requirements.dev.txt /tmp/

RUN --mount=type=cache,dst=/root/.cache/uv \
    uv pip install --system -r /tmp/requirements.dev.txt

WORKDIR /project
