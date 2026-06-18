#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"
source venv/bin/activate
export PYTHONPATH="$DIR"
clear
echo -e "\033[1;35mДобро пожаловать в Космический Центр VoidCorp\033[0m"
echo -e "\033[1;36mЗагрузка систем...\033[0m"
sleep 0.5
python3 -m cosmos.main
