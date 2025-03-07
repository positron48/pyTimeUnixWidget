#!/bin/bash

# Проверка, активировано ли виртуальное окружение
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "Виртуальное окружение не активировано!"
    echo "Пожалуйста, выполните команду 'source venv/bin/activate' и попробуйте снова."
    exit 1
fi

echo "Установка системных зависимостей..."
sudo apt-get update
sudo apt-get install -y python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-appindicator3-0.1 python3-dev libgirepository1.0-dev pkg-config libcairo2-dev

echo "Установка пакетов через pip..."
pip install requests
pip install retrying
pip install netifaces

echo "Проверка установки..."
if python -c "import requests, retrying, netifaces, gi" &> /dev/null; then
    echo "Все пакеты установлены успешно!"
else
    echo "Ошибка: Не все пакеты удалось импортировать."
    echo "Проверяю отдельно каждый пакет..."
    
    echo -n "requests: "
    if python -c "import requests" &> /dev/null; then echo "OK"; else echo "ОШИБКА"; fi
    
    echo -n "retrying: "
    if python -c "import retrying" &> /dev/null; then echo "OK"; else echo "ОШИБКА"; fi
    
    echo -n "netifaces: "
    if python -c "import netifaces" &> /dev/null; then echo "OK"; else echo "ОШИБКА"; fi
    
    echo -n "gi (GObject Introspection): "
    if python -c "import gi" &> /dev/null; then echo "OK"; else echo "ОШИБКА"; fi
fi 