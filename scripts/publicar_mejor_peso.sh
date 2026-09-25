#!/usr/bin/env bash
set -euo pipefail

nombre=${1:?Indica la carpeta del entrenamiento}
repo=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
salida="$repo/models/aprendizaje_automatico_iii/proyecto_1/$nombre"
mejor="$salida/weights/best.pt"

[[ "$nombre" =~ ^yolo26[nsmlx]_[a-z0-9-]+_(det|seg)$ ]] || exit 2
test -f "$mejor"
cd "$repo"
exec 9>"$(git rev-parse --git-path publicar_mejor_peso.lock)"
flock 9
test "$(git branch --show-current)" = main
if ! git diff --cached --quiet; then
    echo "Hay cambios preparados para otro commit" >&2
    exit 1
fi

export PATH="$HOME/.local/bin:$PATH"
git pull --ff-only origin main

cat > "$salida/.gitignore" <<'EOF'
*
!/.gitignore
!/weights/
!/weights/best.pt
EOF

test "$(git check-attr filter -- "$mejor" | awk '{print $3}')" = lfs
git add -- "$salida/.gitignore" "$mejor"
if ! git diff --cached --quiet; then
    git commit -m "Publicar mejor peso $nombre"
fi
git push origin main
