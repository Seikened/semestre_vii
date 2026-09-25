#!/usr/bin/env bash
set -euo pipefail
test "$#" -eq 3 || exit 2

repo=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
"$repo/.venv/bin/python" "$repo/scripts/entrenar_panes.py" "yolo26${1}_${2}_${3}"
