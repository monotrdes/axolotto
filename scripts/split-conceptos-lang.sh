#!/usr/bin/env bash
#
# split-conceptos-lang.sh
# Separa las paginas bilingues de wiki/conceptos/ en versiones puras.
#   wiki/conceptos-es/  — solo español (hasta ## English)
#   wiki/conceptos-en/  — solo inglés  (desde ## English hasta EOF)
#
# Uso: bash scripts/split-conceptos-lang.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SRC_DIR="$ROOT_DIR/wiki/conceptos"
ES_DIR="$ROOT_DIR/wiki/conceptos-es"
EN_DIR="$ROOT_DIR/wiki/conceptos-en"

rm -rf "$ES_DIR" "$EN_DIR"
mkdir -p "$ES_DIR" "$EN_DIR"

es_count=0
en_count=0

for src_file in "$SRC_DIR"/*.md; do
  [[ -f "$src_file" ]] || continue
  filename="$(basename "$src_file")"

  # ─── Español: todo antes de "## English" ───
  awk '/^## English/ { exit } { print }' "$src_file" > "$ES_DIR/$filename"
  es_count=$((es_count + 1))

  # ─── Inglés: solo la sección English + Quick Reference + footer ───
  # Usamos awk para extraer desde "## English" hasta EOF
  awk 'BEGIN{found=0} /^## English/ {found=1; print; next} found==1 {print}' "$src_file" > "$EN_DIR/$filename"
  en_count=$((en_count + 1))

  # Si el archivo inglés quedó vacío, borrarlo (paginas sin sección English)
  if [[ ! -s "$EN_DIR/$filename" ]]; then
    rm "$EN_DIR/$filename"
    en_count=$((en_count - 1))
  fi
done

echo "Separación completada:"
echo "  Español: $ES_DIR/  ($es_count archivos)"

es_size=$(du -sh "$ES_DIR" | cut -f1)
echo "  Tamaño ES: $es_size"

echo "  Inglés:  $EN_DIR/  ($en_count archivos)"
if [[ $en_count -gt 0 ]]; then
  en_size=$(du -sh "$EN_DIR" | cut -f1)
  echo "  Tamaño EN: $en_size"
fi
