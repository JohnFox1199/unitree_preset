#!/bin/bash
set -e

echo "=== Установка Unitree G1 Simulation ==="

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "ℹ️  $1"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

# Проверка системы
log_info "Проверка системы..."
if ! command -v python3 >/dev/null; then
    log_error "Python3 не установлен"
    exit 1
fi

# Создаем бэкапы существующих файлов
backup_file() {
    if [ -e "$1" ]; then
        local backup="${1}.backup.$(date +%Y%m%d_%H%M%S)"
        log_warning "Создаётся бэкап: $backup"
        cp -r "$1" "$backup"
    fi
}

# Установка системных зависимостей
log_info "Установка системных зависимостей..."
sudo apt update && sudo apt install -y \
    build-essential cmake \
    python3 python3-pip python3-venv \
    libgl1-mesa-dev libglfw3 || {
    log_warning "Некоторые пакеты не установились, продолжаем..."
}

# Настройка MuJoCo
log_info "Настройка MuJoCo..."
mkdir -p ~/.mujoco
if [ -f "thirdparty/mujoco/mujoco-3.3.6-linux-x86_64.tar.gz" ]; then
    tar -xf thirdparty/mujoco/mujoco-3.3.6-linux-x86_64.tar.gz -C ~/.mujoco
    log_success "MuJoCo установлен из локального пакета"
else
    log_warning "Локальный MuJoCo не найден, будет скачан из интернета"
    wget -q https://github.com/google-deepmind/mujoco/releases/download/3.3.6/mujoco-3.3.6-linux-x86_64.tar.gz -P /tmp/
    tar -xf /tmp/mujoco-3.3.6-linux-x86_64.tar.gz -C ~/.mujoco
    rm /tmp/mujoco-3.3.6-linux-x86_64.tar.gz
fi

# Добавляем в .bashrc
if ! grep -q "MUJOCO_PY_MUJOCO_PATH" ~/.bashrc; then
    echo 'export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$HOME/.mujoco/mujoco-3.3.6/bin' >> ~/.bashrc
    echo 'export MUJOCO_PY_MUJOCO_PATH=$HOME/.mujoco/mujoco-3.3.6' >> ~/.bashrc
    log_success "MuJoCo добавлен в PATH"
fi

# Виртуальное окружение
backup_file "unitree_venv"
log_info "Создание виртуального окружения..."
python3 -m venv unitree_venv
source unitree_venv/bin/activate

# Python пакеты
log_info "Установка Python пакетов..."
pip install --upgrade pip

if [ -d "thirdparty/wheels" ]; then
    pip install --no-index --find-links thirdparty/wheels -r requirements.txt
else
    pip install -r requirements.txt
fi

# Компиляция Unitree SDK
log_info "Компиляция Unitree SDK..."
cd unitree_sdk2
mkdir -p build && cd build
cmake -DBUILD_EXAMPLES=OFF .. 
make -j$(nproc) unitree_sdk2 || make unitree_sdk2
cd ../..

# Установка Python SDK
log_info "Установка Python SDK..."
cd unitree_sdk2_python
pip install -e .
cd ..

# Финальная настройка
echo 'export UNITREE_PRESET_PATH=$(pwd)' >> ~/.bashrc
echo 'export PYTHONPATH=$PYTHONPATH:$(pwd)' >> ~/.bashrc

log_success "Установка завершена!"
echo ""
echo "Для активации окружения: source unitree_venv/bin/activate"
echo "Для проверки: ./scripts/verify_installation.sh"
echo "Для запуска симуляции: cd unitree_mujoco/simulate_python && ./run_simulator.sh"
