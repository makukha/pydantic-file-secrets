#!/bin/sh

BASEDIR=$(dirname "$0")
NAME=$(basename "$(realpath $BASEDIR/..)")

alacritty --hold --working-directory $BASEDIR/.. --title $NAME &
