from gi.repository import Gtk, GLib
from gi.repository import AppIndicator3
import os
import math
import random
import configparser
from configparser import NoSectionError, NoOptionError
import requests

#read config
cfg_file_path = 'config.ini'
config = configparser.ConfigParser()
config.read(cfg_file_path)

class aStatusIcon:
    def __init__(self, host, token):
        self.host = host
        self.token = token

        currpath = os.path.dirname(os.path.realpath(__file__))

        self.ind = AppIndicator3.Indicator.new("example-simple-client", currpath + "/timeIcon.png",
                                               AppIndicator3.IndicatorCategory.APPLICATION_STATUS)
        self.ind.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        self.ind.set_attention_icon("indicator-messages-new")
        self.ind.set_label('', '')
        # self.ind.set_icon("timeIcon.png")

        # create a menu
        self.menu = Gtk.Menu()

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

    def change_label(self):
        headers = {'token': self.token}
        try:
            r = requests.get(self.host + '/api/current', headers=headers)
        except:
            self.ind.set_label(' ошибка подключения', '')
            return True

        if r.status_code == 200:
            r = r.json()

            if 'activity' in r is not None:
                self.task_id = r['id']
                hours = math.floor(r['delta'])
                minutes = math.floor((r['delta'] - hours) * 60)
                if minutes < 10:
                    minutes = '0' + str(minutes)
                else:
                    minutes = str(minutes)

                name = r['activity'] + ' ' + str(hours) + ':' + minutes
                self.ind.set_label(' ' + name, '')
            else:
                self.ind.set_label(' нет задач', '')
        else:
            self.ind.set_label(' ошибка подключения', '')

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

    indicator = aStatusIcon(host, token)

    indicator.change_label()
    GLib.timeout_add(5000, indicator.change_label)

    main()