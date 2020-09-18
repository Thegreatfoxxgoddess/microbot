# SPDX-License-Identifier: GPL-2.0-or-later

import os

import heroku3
from dotenv import load_dotenv

load_dotenv('config.env')
hapi = os.environ.get('Heroku_ApiKey', None)
hname = os.environ.get('Heroku_AppName', None)


class Settings():
    config = heroku3.from_key(hapi).apps()[hname].config()

    def get_config(self, key):
        return self.config[key]

    def get_bool(self, key):
        return bool(self.config[key] == "True")

    def set_config(self, key, value):
        value = str(value)
        self.config[key] = value

    def add_to_list(self, key, value):
        config_value = self.config[key]
        value = str(value)

        if config_value:
            config_list = config_value.split("|")
        else:
            config_list = []

        if value not in config_list:
            config_list.append(value)

        self.config[key] = "|".join(config_list)

    def remove_from_list(self, key, value):
        config_value = self.config[key]
        value = str(value)

        if config_value:
            config_list = config_value.split("|")
        else:
            return

        if value in config_list:
            config_list.remove(value)
        else:
            return

        self.config[key] = "|".join(config_list)

    def get_list(self, key):
        list_setting = self.config[key]
        return list_setting.split("|") if list_setting else []
