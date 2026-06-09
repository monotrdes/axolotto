#!/usr/bin/env bash
#
# build-wiki-consolidated.sh
# Consolida todos los archivos .md del wiki en un solo archivo.
# Soporta separacion por idioma: español (default), inglés, o bilingüe.
#
# Uso:
#   bash scripts/build-wiki-consolidated.sh              # Solo español (default)
#   bash scripts/build-wiki-consolidated.sh --lang en    # Solo inglés
#   bash scripts/build-wiki-consolidated.sh --lang both  # Bilingüe (original)
#   bash scripts/build-wiki-consolidated.sh -o /ruta/salida.md

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
WIKI_DIR="$ROOT_DIR/wiki"
LANG="es"
OUTPUT=""

# Parsear flags
while [[ $# -gt 0 ]]; do
  case $1 in
    --lang)
      LANG="$2"; shift 2 ;;
    -o)
      OUTPUT="$2"; shift 2 ;;
    *)
      echo "Uso: $0 [--lang es|en|both] [-o output.md]"
      exit 1 ;;
  esac
done

# Output por defecto segun idioma
if [[ -z "$OUTPUT" ]]; then
  case "$LANG" in
    es)   OUTPUT="$ROOT_DIR/wiki-consolidado.md" ;;
    en)   OUTPUT="$ROOT_DIR/wiki-consolidado-en.md" ;;
    both) OUTPUT="$ROOT_DIR/wiki-consolidado-bilingual.md" ;;
  esac
fi

# ─── Configuración de directorios ───

EXCLUDE_DIRS=(".obsidian" "axolotto-wiki")

DIR_ORDER=(
  "."              "Raiz"
  "conceptos"      "Conceptos"
  "ai"             "AI"
  "arquitectura"   "Arquitectura"
  "api"            "API"
  "economia"       "Economia"
  "mecanicas"      "Mecanicas"
  "jugadores"      "Jugadores"
)

declare -A FILE_ORDER
FILE_ORDER["."]="00-INDEX.md CHANGELOG.md"

# ─── Funciones ───

collect_files() {
  local dir="$1"
  local search_path="$WIKI_DIR/$dir"
  [[ "$dir" == "." ]] && search_path="$WIKI_DIR"
  [[ -d "$search_path" ]] || return 0

  local preferred=(${FILE_ORDER["$dir"]:-})
  local -A seen
  local result=()

  for pref in "${preferred[@]}"; do
    local f="$search_path/$pref"
    if [[ -f "$f" ]]; then
      result+=("$f")
      seen["$pref"]=1
    fi
  done

  while IFS= read -r -d '' f; do
    local name
    name="$(basename "$f")"
    [[ -n "${seen[$name]:-}" ]] && continue
    result+=("$f")
  done < <(find "$search_path" -maxdepth 1 -name "*.md" -type f -print0 | sort -z)

  for f in "${result[@]}"; do
    printf '%s\n' "$f"
  done
}

# Extrae la parte en español de un archivo (todo antes de cualquier "## English*")
extract_es() {
  local file="$1"
  awk '/^## English/ { exit } { print }' "$file"
}

# Extrae la parte en inglés de un archivo (desde "## English" hasta el final)
extract_en() {
  local file="$1"
  local found=0
  while IFS= read -r line; do
    if [[ $found -eq 0 ]] && [[ "$line" =~ ^##\ English ]]; then
      found=1
      echo "## English"
      continue
    fi
    if [[ $found -eq 1 ]]; then
      echo "$line"
    fi
  done < "$file"
}

# ─── Recolectar archivos ───

ALL_FILES=()
for ((i=0; i<${#DIR_ORDER[@]}; i+=2)); do
  dir="${DIR_ORDER[$i]}"
  label="${DIR_ORDER[$i+1]}"

  while IFS= read -r f; do
    [[ -z "$f" ]] && continue
    ALL_FILES+=("$f|$dir|$label")
  done < <(collect_files "$dir")
done

TOTAL="${#ALL_FILES[@]}"
NOW="$(date '+%Y-%m-%d %H:%M')"

# ─── Título según idioma ───

case "$LANG" in
  es)
    TITLE="# Axolotto — Wiki Completa"
    SUBTITLE="> **Idioma:** Español"
    ;;
  en)
    TITLE="# Axolotto — Complete Wiki"
    SUBTITLE="> **Language:** English"
    ;;
  both)
    TITLE="# Axolotto — Wiki Completa (Bilingüe / Bilingual)"
    SUBTITLE="> **Idioma:** Español + English"
    ;;
esac

# ─── Generar output ───

{
  echo "$TITLE"
  echo ""
  echo "> **Generado:** $NOW"
  echo "> **Archivos:** $TOTAL archivos markdown del wiki"
  echo "$SUBTITLE"
  echo "> **Script:** \`scripts/build-wiki-consolidated.sh\`"
  echo ""
  echo "---"
  echo ""

  current_dir="__NONE__"
  for entry in "${ALL_FILES[@]}"; do
    IFS='|' read -r filepath dir label <<< "$entry"

    # Separador de directorio
    if [[ "$dir" != "$current_dir" ]]; then
      echo ""
      echo "---"
      echo ""
      echo "## $label"
      echo ""
      current_dir="$dir"
    fi

    # Titulo del archivo
    filename="$(basename "$filepath")"
    basename_noext="${filename%.md}"
    relpath="$dir/$filename"
    [[ "$dir" == "." ]] && relpath="$filename"

    echo "### $basename_noext"
    echo "> \`$relpath\`"
    echo ""

    # Contenido segun idioma
    if [[ ! -s "$filepath" ]]; then
      echo "*(archivo vacio)*"
    else
      case "$LANG" in
        es)
          extract_es "$filepath"
          ;;
        en)
          extract_en "$filepath"
          ;;
        both)
          cat "$filepath"
          ;;
      esac
      # Asegurar newline
      echo ""
    fi
    echo ""
  done
} > "$OUTPUT"

SIZE=$(wc -c < "$OUTPUT" | tr -d ' ')
echo "Wiki consolidado generado ($LANG):"
echo "  $OUTPUT"
echo "  Tamano: $(printf "%'d" "$SIZE") bytes | Archivos: $TOTAL"
