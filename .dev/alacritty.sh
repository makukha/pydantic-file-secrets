#!/bin/sh

alacritty --hold \
  --config-file alacritty.toml \
  --working-directory $(pwd)/.. \
  --title $(basename $(pwd)/..) \
  &
