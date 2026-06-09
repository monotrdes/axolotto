#!/bin/bash
echo "=== Axolotto Dev Environment ==="

echo "[1/3] Iniciando sesión tmux..."
~/axolotto/tools/taskboard/bin/tmux_init.sh

echo "[2/3] Iniciando taskboard..."
cd ~/axolotto
python3 tools/taskboard/server.py &
TBPID=$!
echo "  Taskboard PID: $TBPID"

echo "[3/3] Listo."
echo ""
echo "  Taskboard:  http://localhost:8181"
echo "  Agentes:    tmux attach -t axolotto-agents"
echo ""
echo "Para detener: kill $TBPID && tmux kill-session -t axolotto-agents"

wait $TBPID
