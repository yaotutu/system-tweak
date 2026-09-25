#!/usr/bin/env bash
set -euo pipefail

tmp_dir=$(mktemp -d)
cleanup() {
  rm -rf "$tmp_dir"
}
trap cleanup EXIT

git clone --depth=1 https://github.com/rime/plum.git "$tmp_dir/plum"
rime_dir="$HOME/.local/share/fcitx5/rime" \
  bash "$tmp_dir/plum/rime-install" iDvel/rime-ice
