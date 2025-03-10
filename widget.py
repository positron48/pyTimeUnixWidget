# -*- coding: UTF-8 -*-
from retrying import retry
import netifaces
from gi.repository import Gtk, GLib
from gi.repository import AppIndicator3
import os
import math
import time
import datetime
import configparser
from configparser import NoSectionError, NoOptionError
import requests
import sys
import threading

#read config
cfg_file_path = 'config.ini'
config = configparser.ConfigParser()
config.read(cfg_file_path)

# Get the absolute path to the script directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def get_user_text(parent, message, title=''):
    # Returns user input as a string or None
    # If user does not input text it returns None, NOT AN EMPTY STRING.
    dialogWindow = Gtk.MessageDialog(None,
                          Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                          Gtk.MessageType.QUESTION,
                          Gtk.ButtonsType.OK_CANCEL,
                          message)

    dialogWindow.set_title(title)

    dialogBox = dialogWindow.get_content_area()
    userEntry = Gtk.Entry()
    userEntry.set_size_request(250,0)
    dialogBox.pack_end(userEntry, False, False, 0)

    dialogWindow.show_all()
    response = dialogWindow.run()
    text = userEntry.get_text()
    dialogWindow.destroy()
    if (response == Gtk.ResponseType.OK) and (text != ''):
        return text
    else:
        return None


class aStatusIcon:
    def __init__(self, host, token):
        self.host = host
        self.token = token
        self.last_activity_time = time.time()
        self.last_data = None
        self.sleep_threshold = 60  # считаем сном, если не было активности более 60 секунд

        # Use absolute path to the icon file
        icon_path = os.path.join(SCRIPT_DIR, "time_icon.png")
        
        # Verify icon exists
        if not os.path.exists(icon_path):
            print(f"Error: Icon file not found at {icon_path}")
            sys.exit(1)
            
        # Create indicator with absolute path
        self.ind = AppIndicator3.Indicator.new(
            "time-tracker-widget", 
            icon_path,
            AppIndicator3.IndicatorCategory.APPLICATION_STATUS
        )
        
        # Ensure the indicator is set to active
        self.ind.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        self.ind.set_attention_icon("indicator-messages-new")
        self.ind.set_label('Загрузка...', '')

        # create a menu
        self.menu = Gtk.Menu()

        item = Gtk.MenuItem("новая задача")
        item.show()
        item.connect("activate", self.start)
        self.menu.append(item)

        item = Gtk.MenuItem("остановить")
        item.show()
        item.connect("activate", self.stop)
        self.menu.append(item)

        item = Gtk.MenuItem("выход")
        item.show()
        item.connect("activate", self.quit)
        self.menu.append(item)

        self.menu.show()

        self.ind.set_menu(self.menu)

        self.task_id = None
        self.consecutive_errors = 0
        self.max_consecutive_errors = 3

    def quit(self, widget, data=None):
        Gtk.main_quit()

    def stop(self, widget, data=None):
        if self.task_id is None:
            return True

        headers = {'token': self.token}
        try:
            r = requests.post(self.host + '/api/task/stop', headers=headers, data={'id': self.task_id})
            if r.status_code == 200:
                self.task_id = None
                self.change_label()
        except:
            return True

    def start(self, widget, data=None):
        taskText = get_user_text(self, "задача@проект #тег, комментарий", "Введите название задачи")
        if taskText is not None and taskText != "":
            headers = {'token': self.token}
            try:
                r = requests.post(self.host + '/api/task', headers=headers, data={'name': taskText})
                if r.status_code == 200:
                    self.change_label()
            except:
                return True

    def is_network_connected(self):
        # Check if any network interfaces are up
        interfaces = netifaces.interfaces()
        return any(netifaces.ifaddresses(interface).get(netifaces.AF_INET) for interface in interfaces)

    @retry(stop_max_attempt_number=3, wait_fixed=1000)
    def fetch_data(self):
        if not self.is_network_connected():
            raise Exception("Network is not connected")
            
        headers = {'token': self.token}
        r = requests.get(self.host + '/api/current', headers=headers)
        r.raise_for_status()
        return r.json()

    def check_for_sleep_wake(self):
        """Проверяет был ли компьютер в режиме сна"""
        current_time = time.time()
        time_diff = current_time - self.last_activity_time
        
        if time_diff > self.sleep_threshold:
            print(f"Обнаружен выход из режима сна. Прошло {time_diff:.1f} секунд")
            # Задержка для восстановления сети
            time.sleep(2)
            # Обновляем данные принудительно
            try:
                self.force_refresh()
            except Exception as e:
                print(f"Ошибка при обновлении после сна: {e}")
        
        self.last_activity_time = current_time
        return True
        
    def force_refresh(self):
        """Принудительное обновление состояния"""
        # Сбрасываем кэш данных
        self.last_data = None
        # Устанавливаем промежуточное сообщение
        self.ind.set_label(' обновление...', '')
        # Перерисовываем индикатор
        self.ind.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        # Запрашиваем новые данные в отдельном потоке
        threading.Thread(target=self._background_refresh).start()
    
    def _background_refresh(self):
        """Обновление в фоновом потоке"""
        try:
            # Пробуем получить новые данные
            data = self.fetch_data()
            # Если успешно, обновляем UI из основного потока
            GLib.idle_add(self._update_label_with_data, data)
        except Exception as e:
            # В случае ошибки, обновляем UI с сообщением об ошибке
            GLib.idle_add(self._update_label_with_error, str(e))
    
    def _update_label_with_data(self, data):
        """Обновляет метку с полученными данными"""
        self.last_data = data
        
        if 'activity' in data:
            self.task_id = data['id']
            hours = math.floor(data['delta'])
            minutes = math.floor((data['delta'] - hours) * 60)
            if minutes < 10:
                minutes = '0' + str(minutes)
            else:
                minutes = str(minutes)

            name = data['activity'] + ' ' + str(hours) + ':' + minutes
            self.ind.set_label(' ' + name, '')
        else:
            self.ind.set_label(' нет задач', '')
            
        # Сбрасываем счетчик ошибок
        self.consecutive_errors = 0
        # Перерисовываем
        self.ind.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        return False  # для GLib.idle_add
        
    def _update_label_with_error(self, error_message):
        """Обновляет метку с сообщением об ошибке"""
        self.ind.set_label(' ошибка подключения', '')
        # Перерисовываем
        self.ind.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        
        # Увеличиваем счетчик ошибок
        self.consecutive_errors += 1
        print(f"Ошибка соединения ({self.consecutive_errors}/{self.max_consecutive_errors}): {error_message}")
        
        # После нескольких ошибок подряд, меняем интервал обновления
        if self.consecutive_errors >= self.max_consecutive_errors:
            print("Несколько ошибок подряд. Следующая попытка через 30 секунд.")
            GLib.timeout_add(30000, self._retry_after_errors)
        
        return False  # для GLib.idle_add
    
    def _retry_after_errors(self):
        """Повторная попытка после серии ошибок"""
        print("Повторная попытка подключения...")
        self.consecutive_errors = 0
        self.force_refresh()
        return False  # для GLib.timeout_add

    def change_label(self):
        # Проверяем, не был ли компьютер в режиме сна
        self.check_for_sleep_wake()
        
        try:
            data = self.fetch_data()
            self._update_label_with_data(data)
            
        except requests.exceptions.RequestException as e:
            # Handle network errors
            self._update_label_with_error(str(e))
            
        except Exception as e:
            # Handle other exceptions
            self.ind.set_label(' ошибка', '')
            # Force the indicator to redraw
            self.ind.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
            print(f"Неизвестная ошибка: {e}")

        return True

def getValueFromConfig(config, name):
    try:
        value = config.get('main', name)
    except NoSectionError:
        return None
    except NoOptionError:
        return None
    return value


def main():
    Gtk.main()
    return 0


if __name__ == "__main__":
    host = getValueFromConfig(config, 'host')
    token = getValueFromConfig(config, 'token')
    
    if not host or not token:
        print("Error: Host or token not found in config.ini")
        sys.exit(1)

    try:
        indicator = aStatusIcon(host, token)
        
        # Initial label update
        indicator.change_label()
        
        # Set up periodic updates
        GLib.timeout_add(5000, indicator.change_label)
        
        # Set up more frequent wake detection
        GLib.timeout_add(1000, indicator.check_for_sleep_wake)
        
        main()
    except Exception as e:
        print(f"Error initializing application: {e}")
        sys.exit(1)