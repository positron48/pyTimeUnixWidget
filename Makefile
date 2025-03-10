.PHONY: setup install run stop restart status autostart clean help update full-install

# Цвета для вывода
GREEN=\033[0;32m
YELLOW=\033[1;33m
RED=\033[0;31m
NC=\033[0m # No Color

# Переменные
SCREEN_NAME = timewidget

help:
	@echo "${YELLOW}Доступные команды:${NC}"
	@echo "  ${GREEN}make setup${NC}        - Настройка виртуального окружения (установка зависимостей)"
	@echo "  ${GREEN}make install${NC}      - Быстрая установка (зависимости + настройка автозапуска)"
	@echo "  ${GREEN}make run${NC}          - Запуск виджета в фоновом режиме"
	@echo "  ${GREEN}make stop${NC}         - Остановка виджета"
	@echo "  ${GREEN}make restart${NC}      - Перезапуск виджета"
	@echo "  ${GREEN}make status${NC}       - Проверка статуса виджета"
	@echo "  ${GREEN}make autostart${NC}    - Настройка автозапуска при входе в систему"
	@echo "  ${GREEN}make clean${NC}        - Удаление временных файлов и venv"
	@echo "  ${GREEN}make update${NC}       - Обновление зависимостей"
	@echo "  ${GREEN}make full-install${NC} - Полная установка (зависимости + автозапуск + запуск)"

setup:
	@echo "${YELLOW}Настройка виртуального окружения...${NC}"
	@chmod +x setup_venv.sh
	@./setup_venv.sh
	@echo "${GREEN}Готово!${NC}"

install: setup autostart
	@echo "${GREEN}Установка завершена!${NC}"

run:
	@echo "${YELLOW}Запуск виджета в фоновом режиме...${NC}"
	@chmod +x run_background.sh
	@./run_background.sh

stop:
	@echo "${YELLOW}Остановка виджета...${NC}"
	@if screen -list | grep -q $(SCREEN_NAME); then \
		screen -X -S $(SCREEN_NAME) quit; \
		echo "${GREEN}Виджет остановлен.${NC}"; \
	elif pgrep -f "python widget.py" > /dev/null; then \
		pkill -f "python widget.py"; \
		echo "${GREEN}Виджет остановлен.${NC}"; \
	else \
		echo "${RED}Виджет не запущен.${NC}"; \
	fi

restart: stop run

status:
	@if screen -list | grep -q $(SCREEN_NAME); then \
		echo "${GREEN}Виджет запущен в screen ($(SCREEN_NAME)).${NC}"; \
		echo "Для просмотра логов выполните: screen -r $(SCREEN_NAME)"; \
	elif pgrep -f "python widget.py" > /dev/null; then \
		PID=$$(pgrep -f "python widget.py"); \
		echo "${GREEN}Виджет запущен (PID: $$PID).${NC}"; \
	else \
		echo "${RED}Виджет не запущен.${NC}"; \
	fi

autostart:
	@echo "${YELLOW}Настройка автозапуска...${NC}"
	@chmod +x autostart.sh
	@./autostart.sh

clean:
	@echo "${YELLOW}Удаление временных файлов и venv...${NC}"
	@rm -rf venv __pycache__ *.pyc widget.log
	@echo "${GREEN}Готово!${NC}"

update:
	@echo "${YELLOW}Обновление зависимостей...${NC}"
	@if [ -d "venv" ]; then \
		source venv/bin/activate && pip install -U requests retrying netifaces; \
		echo "${GREEN}Зависимости обновлены.${NC}"; \
	else \
		echo "${RED}Виртуальное окружение не найдено. Сначала выполните 'make setup'.${NC}"; \
	fi

full-install: setup autostart run
	@echo "${GREEN}Полная установка завершена! Виджет запущен.${NC}" 