from gi.repository import Gtk, GLib
from gi.repository import AppIndicator3
import os
import random
import configparser
from configparser import NoSectionError, NoOptionError
import requests

#read config
cfg_file_path = 'config.ini'
config = configparser.ConfigParser()
config.read(cfg_file_path)

class aStatusIcon:
    def __init__(self):
        currpath = os.path.dirname(os.path.realpath(__file__))

        self.ind = AppIndicator3.Indicator.new("example-simple-client", currpath + "/timeIcon.png",
                                               AppIndicator3.IndicatorCategory.APPLICATION_STATUS)
        self.ind.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        self.ind.set_attention_icon("indicator-messages-new")
        self.ind.set_label('', '')
        # self.ind.set_icon("timeIcon.png")

        # create a menu
        self.menu = Gtk.Menu()

        item = Gtk.MenuItem("Quit")
        item.show()
        item.connect("activate", self.quit)
        self.menu.append(item)
        self.menu.show()

        self.ind.set_menu(self.menu)

    def quit(self, widget, data=None):
        Gtk.main_quit()

    def change_label(self, ind_app, host, token):
        headers = {'token': token}
        r = requests.get(host + '/api/current', headers=headers)

        if r.status_code == 200:
            r = r.json()

            if 'activity' in r is not None:
                name = r['activity'] + ' ' + str(r['delta'])
                ind_app.set_label(' ' + name, '')
            else:
                ind_app.set_label(' нет задач', '')

        else:
            ind_app.set_label(' ошибка подключения', '')

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

    indicator = aStatusIcon()

    indicator.change_label(indicator.ind, host, token)
    GLib.timeout_add(5000, indicator.change_label, indicator.ind, host, token)

    main()