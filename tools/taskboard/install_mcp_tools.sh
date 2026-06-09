#!/bin/bash
# install_mcp_tools.sh — Install fog-context and shadowbrain MCP servers
# for the Axolotto project. Run this ONCE on each development machine.
#
# Usage: bash tools/taskboard/install_mcp_tools.sh
#
# After running, restart Claude Code to pick up the new MCP servers.

set -e

echo "========================================"
echo "Axolotto MCP Tools Installer"
echo "========================================"
echo ""

# ── Detect OS/Arch ──────────────────────────────────────────────────────────
OS=$(uname -s)
ARCH=$(uname -m)

case "$OS" in
    Linux)  PLATFORM="linux" ;;
    Darwin) PLATFORM="macos" ;;
    *)      echo "Unsupported OS: $OS (try WSL or manual install)"; exit 1 ;;
esac

case "$ARCH" in
    x86_64)  ARCH_SUFFIX="amd64" ;;
    aarch64|arm64) ARCH_SUFFIX="arm64" ;;
    *)       echo "Unsupported arch: $ARCH"; exit 1 ;;
esac

# ── fog-context (codebase knowledge graph) ──────────────────────────────────
echo "--- Installing fog-context ---"
FOG_VERSION=$(curl -s https://api.github.com/repos/luciusvo/fog-context/releases/latest | grep tag_name | cut -d'"' -f4)
if [ -z "$FOG_VERSION" ]; then
    echo "  Could not determine latest fog-context version. Skipping."
else
    FOG_URL="https://github.com/luciusvo/fog-context/releases/download/${FOG_VERSION}/fog-mcp-${PLATFORM}-${ARCH_SUFFIX}"
    FOG_BIN="$HOME/.local/bin/fog-mcp-server"

    mkdir -p "$HOME/.local/bin"
    echo "  Downloading fog-context ${FOG_VERSION}..."
    curl -L "$FOG_URL" -o "$FOG_BIN" && chmod +x "$FOG_BIN"
    echo "  fog-context installed to $FOG_BIN"

    # Index the Axolotto project
    echo "  Indexing Axolotto project (this may take a minute)..."
    "$FOG_BIN" index --project "$(dirname "$(dirname "$(dirname "$(readlink -f "$0")")")")" 2>&1 || echo "  Indexing skipped (run manually: fog-mcp-server index --project /path/to/axolotto)"
fi

# ── shadowbrain (shared agent memory) ───────────────────────────────────────
echo "--- Installing shadowbrain ---"
if command -v npm &> /dev/null; then
    npm install -g shadowbrain 2>&1 || echo "  npm install failed. Install manually: npm install -g shadowbrain"
    if command -v shadowbrain &> /dev/null; then
        shadowbrain install claude-code 2>&1 || echo "  shadowbrain agent registration skipped"
        echo "  shadowbrain installed and registered with Claude Code"
    fi
else
    echo "  npm not found. Install Node.js first, then: npm install -g shadowbrain"
fi

echo ""
echo "========================================"
echo "Installation complete!"
echo ""
echo "MCP servers configured:"
echo "  1. axolotto-kb (custom) — always available"
echo "  2. fog-context         — codebase knowledge graph"
echo "  3. shadowbrain         — cross-session memory"
echo ""
echo "Run 'cat .claude/context/project-brief.md' to verify context."
echo "Restart Claude Code to pick up changes."
echo "========================================"
