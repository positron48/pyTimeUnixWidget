#!/bin/bash

# Путь к текущей директории
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Проверка существования виртуального окружения
if [ ! -d "venv" ]; then
    echo "Виртуальное окружение не найдено. Сначала настройте его с помощью setup_venv.sh"
    exit 1
fi

# Выбор метода запуска в фоне
if command -v screen &> /dev/null; then
    # Проверка, запущен ли уже виджет в screen
    if screen -ls | grep -q "timewidget"; then
        echo "Виджет уже запущен в screen. Чтобы перезапустить, сначала остановите его:"
        echo "screen -X -S timewidget quit"
        exit 0
    fi
    
    # Запуск через screen
    echo "Запуск виджета в фоновом режиме через screen..."
    screen -dmS timewidget bash -c "cd $SCRIPT_DIR && source venv/bin/activate && python widget.py"
    echo "Виджет запущен! Для просмотра логов выполните: screen -r timewidget"
    echo "Для отключения от сессии нажмите Ctrl+A, затем D"
    echo "Для остановки виджета выполните: screen -X -S timewidget quit"
else
    # Запуск через nohup
    echo "Запуск виджета в фоновом режиме через nohup..."
    nohup bash -c "cd $SCRIPT_DIR && source venv/bin/activate && python widget.py" > widget.log 2>&1 &
    echo "Виджет запущен! PID: $!"
    echo "Логи записываются в файл: $SCRIPT_DIR/widget.log"
    echo "Для остановки виджета выполните: kill $!"
fi 