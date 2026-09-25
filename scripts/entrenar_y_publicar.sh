#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 3 ]; then
    echo "Uso: $0 {n|s|m|l|x} {bread-v2|mexican-v3} {det|seg}" >&2
    exit 2
fi

tamano=$1
dataset=$2
tarea=$3
[[ "$tamano" =~ ^[nsmlx]$ ]] || exit 2

case "$dataset:$tarea" in
    bread-v2:det)
        datos="$HOME/Descargas/bread-detector-v2-yolo26/data_local.yaml"
        modelo="yolo26${tamano}.pt"
        tarea_yolo=detect
        ;;
    mexican-v3:seg)
        datos="$HOME/Descargas/mexican-bread-v3-yolo26/data_local.yaml"
        modelo="yolo26${tamano}-seg.pt"
        tarea_yolo=segment
        ;;
    *)
        echo "Esa combinación de dataset y tarea no tiene etiquetas compatibles" >&2
        exit 2
        ;;
esac

repo=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
nombre="yolo26${tamano}_${dataset}_${tarea}"
modelos="$repo/models/aprendizaje_automatico_iii/proyecto_1"
test -f "$datos"
test ! -e "$modelos/$nombre"
cd "$HOME/Descargas"

"$repo/.venv/bin/yolo" "task=$tarea_yolo" mode=train "model=$modelo" "data=$datos" \
    epochs=100 patience=20 imgsz=640 batch=0.7 device=0 cache=False workers=4 \
    seed=42 deterministic=True save=True save_period=-1 plots=False \
    "project=$modelos" "name=$nombre" exist_ok=False

"$repo/scripts/publicar_mejor_peso.sh" "$nombre"
