#!/bin/bash
# Uso:
#   ./reiniciar.sh          → reinicia todo (sin taskboard)
#   ./reiniciar.sh task     → inicia taskboard manualmente
#   ./reiniciar.sh axo      → reinicia todo EXCEPTO el taskboard

TARGET="${1:-all}"

restart_taskboard() {
    echo "🦎 Reiniciando Taskboard..."
    pm2 delete axolotto-taskboard 2>/dev/null
    pm2 start tools/taskboard/server.py \
        --name axolotto-taskboard \
        --interpreter python3 \
        --cwd "$(pwd)"
    echo "✅ Taskboard listo en http://localhost:8181"
}

restart_axo() {
    echo "🦎 Reiniciando Axolotto (sin Taskboard)..."
    docker-compose down 2>/dev/null
    docker rm -f axolotto_backend axolotto_db axolotto_anvil 2>/dev/null

    if lsof -i :8545 -t > /dev/null 2>&1; then
        echo "⚠️  Liberando puerto 8545 en el host..."
        kill -9 $(lsof -i :8545 -t) 2>/dev/null || true
        sleep 1
    fi

    echo "🚀 Levantando base de datos y nodo Anvil..."
    docker-compose up -d db_axolotto anvil_axolotto

    echo "⏳ Esperando que Anvil inicialice..."
    sleep 4

    echo "📦 Compilando y desplegando contratos locales..."
    bash scripts/deploy_local.sh

    echo "🚀 Iniciando Backend..."
    docker-compose up -d --build backend_axolotto

    echo "📦 Compilando y reiniciando Frontend..."
    cd frontend
    npm run build
    pm2 delete axolotto-frontend 2>/dev/null
    pm2 start npm --name "axolotto-frontend" -- start
    cd ..

    echo "✅ ¡Axolotto reiniciado (Taskboard intacto)!"
    echo "   Backend:  http://localhost:8000"
    echo "   Frontend: http://localhost:3000"
}

if [ "$TARGET" = "task" ]; then
    restart_taskboard
    exit 0
fi

if [ "$TARGET" = "axo" ]; then
    restart_axo
    exit 0
fi

if [ "$TARGET" = "runner" ]; then
    echo "🦎 Iniciando Task Agent Runner (watch mode)..."
    python3 scripts/task_agent_runner.py --watch
    exit 0
fi

# --- Full restart ---
echo "🦎 Deteniendo Axolotto..."
docker-compose down 2>/dev/null
docker rm -f axolotto_backend axolotto_db axolotto_anvil axolotto_taskboard 2>/dev/null

if lsof -i :8545 -t > /dev/null 2>&1; then
    echo "⚠️  Liberando puerto 8545 en el host..."
    kill -9 $(lsof -i :8545 -t) 2>/dev/null || true
    sleep 1
fi

echo "🚀 Levantando base de datos y nodo Anvil..."
docker-compose up -d db_axolotto anvil_axolotto

echo "⏳ Esperando que Anvil inicialice..."
sleep 4

echo "📦 Compilando y desplegando contratos locales..."
bash scripts/deploy_local.sh

echo "🚀 Iniciando Backend..."
docker-compose up -d --build backend_axolotto

echo "📦 Compilando y reiniciando Frontend..."
cd frontend
npm run build
pm2 delete axolotto-frontend 2>/dev/null
pm2 start npm --name "axolotto-frontend" -- start
cd ..
echo "✅ ¡Ecosistema Axolotto reiniciado con éxito!"
echo "   Backend:  http://localhost:8000"
echo "   Frontend: http://localhost:3000"
echo "   Taskboard: manual → ./reiniciar.sh task"