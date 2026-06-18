# VoidCorp Terminal

> **Космическая программа в терминале.**  
> Построй ракету — выйди на орбиту — исследуй Солнечную систему.

CLI-игра в жанре space program simulator, вдохновлённая Kerbal Space Program.  
Управляй космической программой корпорации VoidCorp: проектируй ракеты, запускай
их, выполняй контракты, исследуй планеты и открывай новые технологии — всё это
не выходя из терминала.

## Установка

**Вариант 1: curl (самый быстрый)**

```bash
curl -fsSL https://cosmos-cli.xyz/install | bash
cosmos
```

**Вариант 2: pip из GitHub**

```bash
pip install "https://github.com/shirou-eh/Cosmos-cli.git#subdirectory=Cosmos-cli"
cosmos
```

**Вариант 3: из репозитория**

```bash
git clone https://github.com/shirou-eh/Cosmos-cli.git
cd Cosmos-cli/Cosmos-cli
python -m venv venv
source venv/bin/activate   # Linux/macOS
# venv\Scripts\activate    # Windows
pip install -r requirements.txt
python -m cosmos.main start
```

**Вариант 4: Docker**

```bash
docker-compose up
```

## Управление

| Клавиша | Действие |
|---------|----------|
| `V` | Сборочный Цех (VAB) |
| `L` | Стартовая площадка |
| `M` | Mission Control |
| `R` | Центр Исследований |
| `S` | Сохранить игру |
| `Q` | Выход |

### В полёте

| Клавиша | Действие |
|---------|----------|
| `Z` | Максимальная тяга + старт |
| `X` | Выключить двигатели |
| `R`/`F` | Увеличить/уменьшить тягу |
| `W`/`S` | Тангаж (наклон) |
| `Пробел` | Отстрел ступени |
| `P` | Парашют |
| `O` | Overdrive (150% тяги) |
| `M` | Бортовой компьютер |

## Системные требования

- **Python** 3.9 или новее
- **ОС**: Linux, macOS, Windows 10+ (Windows Terminal)
- **Терминал** с поддержкой True Color и Unicode

## Сайт

🌐 [cosmos-cli.xyz](https://cosmos-cli.xyz)  
📖 [docs.cosmos-cli.xyz](https://docs.cosmos-cli.xyz)
