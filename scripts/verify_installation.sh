#!/bin/bash
echo "=== Проверка установки Unitree G1 ==="

check() {
    if eval "$1" 2>/dev/null; then
        echo "✅ $2"
        return 0
    else
        echo "❌ $2"
        return 1
    fi
}

# Проверка виртуального окружения
if [ ! -f "../unitree_venv/bin/activate" ]; then
    echo "❌ Виртуальное окружение не найдено"
    echo "Запустите: ./scripts/install.sh"
    exit 1
fi

source ../unitree_venv/bin/activate

echo ""
echo "=== Проверка компонентов ==="

check "python -c 'import mujoco'" "MuJoCo"
check "python -c 'import unitree_sdk2py'" "Unitree SDK" 
check "python -c 'import cv2'" "OpenCV"
check "python -c 'import numpy'" "NumPy"
check "[ -d \"$HOME/.mujoco/mujoco-3.3.6\" ]" "MuJoCo установлен"
check "[ -f \"../unitree_sdk2/lib/x86_64/libunitree_sdk2.a\" ]" "Unitree C++ SDK"

echo ""
echo "=== Переменные окружения ==="
env | grep -E "(MUJOCO|UNITREE)" | sort

echo ""
echo "Проверка завершена!"
