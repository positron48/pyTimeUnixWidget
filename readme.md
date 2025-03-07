# Gnome widget for timetracker

## Установка

### Системные зависимости
```bash
sudo apt update
sudo apt install -y python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-appindicator3-0.1 python3-dev libgirepository1.0-dev pkg-config libcairo2-dev python3-venv
```

### Настройка конфигурации
```bash
cp config.ini.dist config.ini
```

Установите `host` и `token` в файле config.ini

### Метод 1: Быстрая установка через скрипт
```bash
chmod +x setup_venv.sh
./setup_venv.sh
```

### Метод 2: Ручная настройка venv
```bash
# Создание виртуального окружения с доступом к системным пакетам
python3 -m venv venv --system-site-packages

# Активация виртуального окружения
source venv/bin/activate

# Установка зависимостей
pip install requests retrying netifaces
```

### Устранение проблем с зависимостями
Если у вас возникли проблемы с установкой пакетов, используйте специальный скрипт:
```bash
chmod +x install_packages.sh
source venv/bin/activate
./install_packages.sh
```

## Запуск

### Метод 1: Быстрый запуск в фоновом режиме
```bash
chmod +x run_background.sh
./run_background.sh
```
Скрипт автоматически запустит виджет в фоновом режиме с помощью `screen` или `nohup` и выведет информацию о том, как просмотреть логи и остановить виджет.

### Метод 2: Запуск в активированном venv
```bash
source venv/bin/activate
python widget.py
```

### Метод 3: Ручной запуск в фоновом режиме (screen)
```bash
source venv/bin/activate
screen -dmS timewidget python widget.py
```

Для отключения консоли можно использовать `screen`.

## Автозапуск

Чтобы настроить автозапуск виджета при входе в систему:

```bash
chmod +x autostart.sh
./autostart.sh
```

Это создаст файл .desktop в ~/.config/autostart/, который запустит виджет при входе в систему.