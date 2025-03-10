# Gnome widget for timetracker

## Быстрая установка через Make

```bash
# Установка зависимостей и настройка автозапуска
make install

# Полная установка (зависимости + автозапуск + запуск)
make full-install

# Список всех доступных команд
make help
```

## Управление виджетом через Make

```bash
# Запуск виджета в фоновом режиме
make run

# Остановка виджета
make stop

# Перезапуск виджета
make restart

# Проверка статуса виджета
make status

# Обновление зависимостей
make update

# Удаление временных файлов и venv
make clean
```

## Стандартная установка

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

## Стандартный запуск

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
