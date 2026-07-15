#!/usr/bin/env bash
# =============================================================================
# deploy_local.sh — Levanta Anvil, despliega contratos Axolotto y exporta .env
#
# USO:
#   chmod +x scripts/deploy_local.sh
#   ./scripts/deploy_local.sh
#
# Requiere: forge, anvil (Foundry instalado en ~/.foundry/bin/)
# =============================================================================

set -e

export PATH="$PATH:/home/monotr/.foundry/bin"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$SCRIPT_DIR/.."
CONTRACTS_DIR="$ROOT/contracts"
BACKEND_ENV="$ROOT/backend/.env"

update_or_add_env() {
    local key="$1"
    local value="$2"
    local file="$3"
    if grep -q "^${key}=" "$file" 2>/dev/null; then
        sed -i "s|^${key}=.*|${key}=${value}|" "$file"
    else
        echo "${key}=${value}" >> "$file"
    fi
}

# Cuenta 0 de Anvil — private key conocida (solo para local)
DEPLOYER_KEY="0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
DEPLOYER_ADDR="0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"

echo "══════════════════════════════════════════════════════════════"
echo "  🦎 Axolotto — Deploy Local con Foundry/Anvil"
echo "══════════════════════════════════════════════════════════════"

# ── 1. Verificar si Anvil ya está corriendo ───────────────────────────────
ANVIL_ALREADY_RUNNING=false
if timeout 1 bash -c 'cat < /dev/null > /dev/tcp/127.0.0.1/8545' >/dev/null 2>&1; then
    echo "⛓️  El puerto 8545 ya está en uso. Asumiendo que Anvil ya está activo y expuesto."
    ANVIL_ALREADY_RUNNING=true
fi

if [ "$ANVIL_ALREADY_RUNNING" = false ]; then
    # ── 2. Levantar Anvil en background ───────────────────────────────────────────
    echo "🚀 Levantando Anvil en localhost:8545..."
    nohup anvil \
        --host 0.0.0.0 \
        --port 8545 \
        --accounts 10 \
        --balance 10000 \
        --block-time 1 \
        --silent > /dev/null 2>&1 &
    ANVIL_PID=$!
    echo "   Anvil PID: $ANVIL_PID"
    sleep 2  # Dar tiempo a que arranque

    # Verificar que Anvil está corriendo
    if ! kill -0 $ANVIL_PID 2>/dev/null; then
        echo "❌ Error: Anvil no pudo iniciar"
        exit 1
    fi
    echo "   ✅ Anvil corriendo"
    update_or_add_env "ANVIL_PID" "$ANVIL_PID" "$BACKEND_ENV"
else
    # Si ya corría, no guardamos un PID local de proceso del host
    update_or_add_env "ANVIL_PID" "" "$BACKEND_ENV"
fi

# ── 3. Compilar contratos ─────────────────────────────────────────────────────
echo ""
echo "🔨 Compilando contratos Solidity..."
cd "$CONTRACTS_DIR"
forge build --quiet
echo "   ✅ Compilación exitosa"

# ── 4. Desplegar todos los contratos ─────────────────────────────────────────
echo ""
echo "📦 Desplegando contratos en Anvil..."
DEPLOY_OUTPUT=$(DEPLOYER_PRIVATE_KEY="$DEPLOYER_KEY" \
    METADATA_BASE_URL="http://localhost:8001/api/v1/metadata/" \
    forge script script/Deploy.s.sol \
        --rpc-url http://127.0.0.1:8545 \
        --broadcast \
        --private-key "$DEPLOYER_KEY" 2>&1)

echo "$DEPLOY_OUTPUT"

# Extraer direcciones del output
extract_addr() {
    echo "$DEPLOY_OUTPUT" | grep "DEPLOYED_$1=" | sed "s/.*DEPLOYED_$1=\(0x[a-fA-F0-9]*\).*/\1/"
}

GAL_ADDR=$(extract_addr "FRJ")
AXG_ADDR=$(extract_addr "AXF")
WEBITOS_ADDR=$(extract_addr "WEBITOS")
AXOLOTITOS_ADDR=$(extract_addr "AXOLOTITOS")
CARTAS_ADDR=$(extract_addr "CARTAS")
BOOSTERS_ADDR=$(extract_addr "SOBRECITOS")
TABLAS_ADDR=$(extract_addr "TABLAS")
CONSUMABLES_ADDR=$(extract_addr "CONSUMABLES")
CONTROLLER_ADDR=$(extract_addr "GAME_CONTROLLER")
RECICLON_VAULT_ADDR=$(extract_addr "RECICLON_VAULT")

echo ""
echo "📋 Contratos desplegados:"
echo "   FRJ (ERC-20):          $GAL_ADDR"
echo "   AXF (ERC-20):          $AXG_ADDR"
echo "   Webitos (ERC-721):     $WEBITOS_ADDR"
echo "   Axolotitos (ERC-721):  $AXOLOTITOS_ADDR"
echo "   Cartas (ERC-1155):     $CARTAS_ADDR"
echo "   Boosters (ERC-1155):   $BOOSTERS_ADDR"
echo "   Tablas (ERC-721):      $TABLAS_ADDR"
echo "   Consumables (ERC-1155):$CONSUMABLES_ADDR"
echo "   GameController:        $CONTROLLER_ADDR"
echo "   ReciclonVault:         $RECICLON_VAULT_ADDR"

# ── 5. Actualizar variables de entorno del backend ────────────────────────────
echo ""
echo "⚙️  Actualizando $BACKEND_ENV con direcciones de contratos locales..."

update_or_add_env "BLOCKCHAIN_MODE"       "local"              "$BACKEND_ENV"
update_or_add_env "ANVIL_RPC_URL"         "http://anvil_axolotto:8545" "$BACKEND_ENV"
update_or_add_env "ANVIL_PID"             "$ANVIL_PID"         "$BACKEND_ENV"
update_or_add_env "TREASURY_PRIVATE_KEY"  "$DEPLOYER_KEY"      "$BACKEND_ENV"
update_or_add_env "AXOGEMA_ADDRESS"       "$AXG_ADDR"          "$BACKEND_ENV"
update_or_add_env "GEMA_ALGA_ADDRESS"     "$GAL_ADDR"          "$BACKEND_ENV"
update_or_add_env "WEBITOS_ADDRESS"       "$WEBITOS_ADDR"       "$BACKEND_ENV"
update_or_add_env "AXOLOTITOS_ADDRESS"    "$AXOLOTITOS_ADDR"   "$BACKEND_ENV"
update_or_add_env "CARDS_ADDRESS"         "$CARTAS_ADDR"       "$BACKEND_ENV"
update_or_add_env "BOOSTERS_ADDRESS"      "$BOOSTERS_ADDR"     "$BACKEND_ENV"
update_or_add_env "TABLAS_ADDRESS"        "$TABLAS_ADDR"       "$BACKEND_ENV"
update_or_add_env "CONSUMABLES_ADDRESS"   "$CONSUMABLES_ADDR"  "$BACKEND_ENV"
update_or_add_env "GAME_CONTROLLER_ADDRESS" "$CONTROLLER_ADDR" "$BACKEND_ENV"
update_or_add_env "RECICLON_VAULT_ADDRESS" "$RECICLON_VAULT_ADDR" "$BACKEND_ENV"
update_or_add_env "PLASMA_RPC_URL"        "http://anvil_axolotto:8545" "$BACKEND_ENV"

echo "   ✅ Variables de entorno actualizadas"

# ── 6. Actualizar variables de entorno del frontend ───────────────────────────
FRONTEND_ENV="$ROOT/frontend/.env.local"
if [ -f "$FRONTEND_ENV" ]; then
    echo ""
    echo "⚙️  Actualizando $FRONTEND_ENV con direcciones de contratos locales..."
    update_or_add_env "NEXT_PUBLIC_GEMA_ALGA_ADDRESS" "$GAL_ADDR" "$FRONTEND_ENV"
    update_or_add_env "NEXT_PUBLIC_AXOGEMA_ADDRESS" "$AXG_ADDR" "$FRONTEND_ENV"
    update_or_add_env "NEXT_PUBLIC_WEBITOS_ADDRESS" "$WEBITOS_ADDR" "$FRONTEND_ENV"
    update_or_add_env "NEXT_PUBLIC_GAME_CONTROLLER_ADDRESS" "$CONTROLLER_ADDR" "$FRONTEND_ENV"
    echo "   ✅ Variables de entorno del frontend actualizadas"
fi

echo ""
echo "══════════════════════════════════════════════════════════════"
echo "  ✅ ¡Deploy completo! Anvil corriendo (PID: $ANVIL_PID)"
echo "  Para detener Anvil: kill $ANVIL_PID"
echo "══════════════════════════════════════════════════════════════"
echo ""
echo "ANVIL_PID=$ANVIL_PID"
