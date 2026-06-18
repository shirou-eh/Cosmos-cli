#!/bin/bash
set -e

# ──────────────────────────────────────────────
#  VoidCorp Terminal — Quick Install
#  curl -fsSL https://cosmos-cli.xyz/install | bash
# ──────────────────────────────────────────────

REPO="shirou-eh/Cosmos-cli"
BRANCH="main"
SUBDIR="Cosmos-cli"

# Colors
R="\033[1;31m"; G="\033[1;32m"; C="\033[1;36m"
M="\033[1;35m"; Y="\033[1;33m"; N="\033[0m"

echo -e "${M}"
echo "╔══════════════════════════════════════════╗"
echo "║      VoidCorp Terminal — Установка       ║"
echo "╚══════════════════════════════════════════╝"
echo -e "${N}"

# Check Python
PYTHON=""
for cmd in python3 python; do
    if command -v $cmd &>/dev/null; then
        VER=$($cmd --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
        MAJOR=${VER%%.*}
        MINOR=${VER#*.}
        if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 9 ]; then
            PYTHON=$cmd
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    echo -e "${R}Ошибка: требуется Python 3.9+${N}"
    echo "Установите: https://python.org"
    exit 1
fi

echo -e "${C}Python найден:${N} $($PYTHON --version)"

# Install via pip from GitHub
echo -e "${Y}Установка VoidCorp Terminal...${N}"
$PYTHON -m pip install --quiet --upgrade "pip setuptools" 2>/dev/null
$PYTHON -m pip install "https://github.com/$REPO.git@$BRANCH#subdirectory=$SUBDIR"

# Verify
echo ""
if command -v cosmos &>/dev/null; then
    echo -e "${G}✓ Установка завершена!${N}"
    echo -e "${C}Запустите:${N} cosmos"
elif $PYTHON -c "import cosmos" 2>/dev/null; then
    echo -e "${G}✓ Установка завершена!${N}"
    echo -e "${C}Запустите:${N} $PYTHON -m cosmos"
else
    echo -e "${R}Ошибка установки.${N}"
    echo "Попробуйте вручную:"
    echo "  git clone https://github.com/$REPO.git"
    echo "  cd Cosmos-cli && $PYTHON -m venv venv && source venv/bin/activate"
    echo "  pip install -r requirements.txt && python -m cosmos"
    exit 1
fi
