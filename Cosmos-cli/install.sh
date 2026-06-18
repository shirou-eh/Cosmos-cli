#!/bin/bash
set -e

clear
echo -e "\033[1;35m"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║           VOIDCORP TERMINAL v3.0 — УСТАНОВЩИК          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo -e "\033[0m"
sleep 1

echo -e "\033[1;36m[VOIDCORP NET] Установка защищенного соединения...\033[0m"
sleep 1
echo -e "\033[1;32m[VOIDCORP NET] Доступ разрешен.\033[0m"
echo -e "\033[1;34m[СИСТЕМА] Подготовка виртуальной среды обитания ядра...\033[0m"

python3 -m venv venv
source venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt

cat << 'EOF' > .install_anim.py
import time
import random
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.panel import Panel
from rich.align import Align
from rich.text import Text

console = Console()
console.clear()

console.print(Panel("[bold magenta]=== ИНИЦИАЛИЗАЦИЯ УСТАНОВЩИКА VOIDCORP V3.0 ===[/bold magenta]", border_style="magenta"))
console.print("[dim cyan]Внимание: Обнаружены аномалии в подпространстве. Игнорирую...[/dim cyan]\n")

with Progress(
    SpinnerColumn("dots", style="bold cyan"),
    TextColumn("[progress.description]{task.description}"),
    BarColumn(complete_style="magenta", finished_style="green"),
    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    console=console,
) as progress:
    t1 = progress.add_task("[yellow]Сборка базового модуля ядра...", total=100)
    for _ in range(100):
        time.sleep(0.005)
        progress.update(t1, advance=1)

    t2 = progress.add_task("[cyan]Подключение к серверам орбитальной сети (Иштар)...", total=100)
    for _ in range(40):
        time.sleep(0.02)
        progress.update(t2, advance=1)

    progress.update(t2, description="[bold red]ВНИМАНИЕ! Магнитная буря. Потеря пакетов...[/bold red]")
    time.sleep(2.0)

    progress.update(t2, description="[cyan]Восстановление сигнала. Маршрутизация через ретранслятор Зевс...[/cyan]")
    for _ in range(60):
        time.sleep(0.015)
        progress.update(t2, advance=1)

    t3 = progress.add_task("[green]Развертывание физического движка Cosmos v2.0 и загрузка чертежей...", total=100)
    for _ in range(100):
        time.sleep(0.008)
        progress.update(t3, advance=1)

    t4 = progress.add_task("[bold #FFEA00]Синхронизация нейромодулей Архитектора и Критика...", total=100)
    for _ in range(100):
        time.sleep(0.01)
        progress.update(t4, advance=1)

    t5 = progress.add_task("[bold #FF00FF]Калибровка системы боковых ускорителей...", total=100)
    for _ in range(100):
        time.sleep(0.007)
        progress.update(t5, advance=1)

console.clear()
logo = """
[bold #9400D3]
╔═══╗╔╗ ╔╗╔════╗╔═══╗╔═══╗╔═══╗╔═══╗╔═══╗╔══╗╔═══╗
║╔═╗║║║ ║║║╔╗╔╗║║╔══╝║╔═╗║║╔═╗║║╔═╗║║╔══╝╚╣╠╝║╔══╝
║╚═╝║║╚═╝║╚╝║║╚╝║╚══╗║║ ║║║╚═╝║║║ ║║║╚══╗ ║║ ║╚══╗
║╔╗╔╝║╔═╗║  ║║  ║╔══╝║╚═╝║║╔╗╔╝║║ ║║║╔══╝ ║║ ║╔══╝
║║║╚╗║║ ║║  ║║  ║╚══╗║╔═╗║║║║╚╗║╚═╝║║╚══╗╔╣╠╗║╚══╗
╚╝╚═╝╚╝ ╚╝  ╚╝  ╚═══╝╚╝ ╚╝╚╝╚═╝╚═══╝╚═══╝╚══╝╚═══╝
[/bold #9400D3]
"""
console.print(Align.center(logo))
console.print(Align.center("[bold cyan]КОРПОРАТИВНАЯ СИСТЕМА УСПЕШНО РАЗВЕРНУТА. ДОБРО ПОЖАЛОВАТЬ, ДИРЕКТОР.[/bold cyan]"))
console.print(Align.center("[dim]База данных компонентов обновлена (+43 детали, боковые ускорители)[/dim]"))
console.print(Align.center("[dim]Система выбора деталей, новые планеты, переработанный полетный движок[/dim]"))
time.sleep(2.0)
EOF

python3 .install_anim.py
rm .install_anim.py

cat << 'EOF' > run_cosmos.sh
#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"
source venv/bin/activate
export PYTHONPATH="$DIR"
clear
echo -e "\033[1;35mДобро пожаловать в Космический Центр VoidCorp\033[0m"
echo -e "\033[1;36mЗагрузка систем...\033[0m"
sleep 0.5
python3 -m cosmos.main start
EOF
chmod +x run_cosmos.sh

echo -e "\n\033[1;35m╔══════════════════════════════════════════════════════════╗"
echo -e "║        УСТАНОВКА VOIDCORP TERMINAL ЗАВЕРШЕНА        ║"
echo -e "╚══════════════════════════════════════════════════════════╝\033[0m"
echo -e "\033[1;36mДля старта терминала введите:\033[0m ./run_cosmos.sh"
echo -e "\033[1;36mДля запуска через Docker:\033[0m docker-compose up"
echo ""
