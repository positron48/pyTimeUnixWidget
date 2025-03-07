#!/bin/bash

# Проверка наличия Python3
if ! command -v python3 &> /dev/null; then
    echo "Python3 не найден. Пожалуйста, установите Python3."
    exit 1
fi

# Проверка наличия pip
if ! command -v pip3 &> /dev/null; then
    echo "pip3 не найден. Пожалуйста, установите pip для Python3."
    exit 1
fi

# Проверка наличия venv
if ! python3 -c "import venv" &> /dev/null; then
    echo "Модуль 'venv' не найден. Устанавливаем..."
    sudo apt-get update
    sudo apt-get install -y python3-venv
fi

# Установка системных зависимостей
echo "Установка системных зависимостей..."
sudo apt-get update
sudo apt-get install -y python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-appindicator3-0.1 python3-dev libgirepository1.0-dev pkg-config libcairo2-dev

# Создание виртуального окружения
echo "Создание виртуального окружения..."
python3 -m venv venv --system-site-packages
source venv/bin/activate

# Обновление pip
echo "Обновление pip..."
pip install --upgrade pip

# Создаем отдельный файл requirements для pip-пакетов
cat > requirements_pip.txt << EOF
requests>=2.28.0
retrying>=1.3.3
netifaces>=0.11.0
EOF

# Установка зависимостей из requirements_pip.txt
echo "Установка зависимостей..."
pip install -r requirements_pip.txt

# Проверка успешности установки всех пакетов
echo "Проверка установленных пакетов..."

if ! python -c "import requests, retrying, netifaces, gi" &> /dev/null; then
    echo "ОШИБКА: Не все пакеты установлены корректно."
    echo "Попытка установить отдельные пакеты:"
    
    # Попытка установить пакеты по отдельности
    pip install requests
    pip install retrying
    pip install netifaces
    
    # Проверка импорта снова
    if ! python -c "import requests, retrying, netifaces, gi" &> /dev/null; then
        echo "ОШИБКА: Некоторые пакеты не удалось установить."
        echo "Пожалуйста, используйте скрипт install_packages.sh для ручной установки пакетов:"
        echo "    chmod +x install_packages.sh"
        echo "    ./install_packages.sh"
        exit 1
    fi
fi

# Делаем скрипт запуска в фоне исполняемым
if [ -f "run_background.sh" ]; then
    chmod +x run_background.sh
fi

echo ""
echo "Виртуальное окружение настроено успешно!"
echo "Все необходимые пакеты установлены."
echo ""
echo "Для активации виртуального окружения выполните:"
echo "    source venv/bin/activate"
echo ""
echo "Для запуска виджета в виртуальном окружении выполните:"
echo "    source venv/bin/activate"
echo "    python widget.py"
echo ""
echo "Для запуска виджета в фоновом режиме выполните:"
echo "    ./run_background.sh"
echo ""
echo "Если возникнут проблемы с пакетами, используйте скрипт install_packages.sh:"
echo "    chmod +x install_packages.sh"
echo "    source venv/bin/activate"
echo "    ./install_packages.sh"
echo ""

# Предложение запустить виджет в фоновом режиме
read -p "Запустить виджет в фоновом режиме сейчас? (y/n): " start_now
if [[ "$start_now" == "y" || "$start_now" == "Y" ]]; then
    if [ -f "run_background.sh" ]; then
        ./run_background.sh
    else
        echo "Скрипт run_background.sh не найден."
        echo "Создайте его или запустите виджет вручную."
    fi
fi 