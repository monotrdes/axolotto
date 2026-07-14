#!/usr/bin/env bash
# =============================================================================
# deploy_production.sh — Despliega Axolotto al servidor de producción (Linux/macOS)
#
# USO:
#   ./scripts/deploy_production.sh git
#   ./scripts/deploy_production.sh hotfix frontend/app/page.tsx
# =============================================================================

set -e

MODE="${1:-git}"
SERVER="192.168.100.15"
USER="monotr"
REMOTE_DIR="/home/monotr/axolotto"
PRODUCTION_URL="https://www.axolot.to"

echo "=============================================================="
echo "  Axolotto - Despliegue a Producción ($SERVER)"
echo "=============================================================="
echo "URL de producción: $PRODUCTION_URL"
echo ""

# 1. Verificar SSH
echo "[check] Verificando conexión SSH..."
if ! remote_host=$(ssh "${USER}@${SERVER}" "hostname" 2>/dev/null); then
    echo "❌ [FAIL] No se pudo establecer conexión SSH con ${USER}@${SERVER}."
    exit 1
fi
echo "   [OK] Conectado a: $remote_host"

# 2. Modo Git
if [ "$MODE" = "git" ]; then
    echo ""
    echo "[git] Iniciando despliegue basado en Git..."
    
    BRANCH=$(git branch --show-current)
    echo "   Rama local actual: $BRANCH"

    # Verificar cambios sin commitear
    if [ -n "$(git status --short)" ]; then
        echo "   ⚠️  [WARN] Tienes cambios locales sin commitear:"
        git status --short
        
        read -p "   ¿Deseas commitear y subir estos cambios automáticamente? (s/n): " choice
        if [[ "$choice" =~ ^[Ss]$ ]]; then
            read -p "   Mensaje de commit: " msg
            if [ -z "$msg" ]; then msg="deploy: auto-commit antes de deploy"; fi
            git add -A
            git commit -m "$msg"
            echo "   [OK] Cambios commiteados."
        else
            echo "   [ABORT] Cancela el deploy para resolver manualmente."
            exit 1
        fi
    fi

    # Push
    echo "   Subiendo rama '$BRANCH' a origin..."
    git push origin "$BRANCH"
    echo "   [OK] Push completado."

    # SSH y Pull
    echo "   Actualizando código en el servidor y compilando..."
    SSH_CMD="cd $REMOTE_DIR && git fetch origin && git checkout $BRANCH && git pull origin $BRANCH && cd frontend && npm install && npm run build && pm2 delete axolotto-frontend 2>/dev/null; pm2 start npm --name axolotto-frontend -- start"
    
    ssh "${USER}@${SERVER}" "$SSH_CMD"
    echo "   [OK] Despliegue Git completado con éxito en el servidor."

# 3. Modo HotFix
elif [ "$MODE" = "hotfix" ]; then
    echo ""
    echo "[hotfix] Iniciando copia directa de archivos vía SCP..."
    
    FILE="$2"
    if [ -z "$FILE" ]; then
        echo "❌ [FAIL] Debes especificar el archivo local a copiar. Ejemplo: ./scripts/deploy_production.sh hotfix frontend/app/page.tsx"
        exit 1
    fi

    if [ ! -f "$FILE" ]; then
        echo "❌ [FAIL] El archivo local no existe: $FILE"
        exit 1
    fi

    REMOTE_FILE="$REMOTE_DIR/$FILE"
    echo "   Copiando $FILE -> $REMOTE_FILE"
    scp "$FILE" "${USER}@${SERVER}:${REMOTE_FILE}"
    echo "   [OK] Transferencia exitosa."

    # Recompilar frontend
    echo "   Recompilando frontend en el servidor..."
    SSH_CMD="cd $REMOTE_DIR/frontend && npm run build && pm2 delete axolotto-frontend 2>/dev/null; pm2 start npm --name axolotto-frontend -- start"
    ssh "${USER}@${SERVER}" "$SSH_CMD"
    
    echo "   [OK] HotFix aplicado y frontend reiniciado con éxito."
else
    echo "❌ Modo no reconocido. Usa 'git' o 'hotfix'."
    exit 1
fi

echo ""
echo "=============================================================="
echo "  [OK] Despliegue finalizado!"
echo "  Visita: $PRODUCTION_URL"
echo "=============================================================="
