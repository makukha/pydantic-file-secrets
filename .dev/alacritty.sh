#!/bin/sh

alacritty --hold \
  --working-directory $(pwd)/.. \
  --title $(basename $(pwd)/..) \
  &
