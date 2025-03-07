#!/bin/bash

# Путь к папке с проектом (измените на свой)
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Создаем desktop-файл для автозапуска
mkdir -p ~/.config/autostart/
cat > ~/.config/autostart/time-tracker-widget.desktop << EOF
[Desktop Entry]
Type=Application
Name=Time Tracker Widget
Comment=Gnome widget for timetracker
Exec=bash -c "cd ${PROJECT_DIR} && source ${PROJECT_DIR}/venv/bin/activate && python ${PROJECT_DIR}/widget.py"
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Terminal=false
EOF

echo "Автозапуск настроен. Виджет будет запускаться при входе в систему." 