# config_manager.py
import json
import os

CONFIG_FILE = 'crude_config.json'

DEFAULT_CONFIG = {
    "server": "irc.example.com",
    "port": 6667,
    "ssl": False,
    "nickname": "YourNick",
    "username": "YourUser",
    "realname": "YourRealName"
}

class ConfigManager:
    def __init__(self):
        self.config = {}
        self.load_config()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = DEFAULT_CONFIG
            self.save_config()

    def save_config(self):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f, indent=4)

    def get(self, key):
        return self.config.get(key, DEFAULT_CONFIG.get(key))

    def set(self, key, value):
        self.config[key] = value
        self.save_config()
