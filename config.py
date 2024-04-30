import json
import os.path


class Settings:
    def __init__(self, rec_sec=None):
        self.rec_sec = rec_sec

    def to_dict(self):
        return self.__dict__

    def get_rec_sec(self):
        return self.rec_sec


config_path = "config.json"
default = Settings(rec_sec=4)


def save_config(conf):
    with open(config_path, "w") as conf_file:
        json.dump(conf.to_dict(), conf_file, indent=4)


def load_config():
    if not os.path.exists(config_path):
        with open(config_path, "w") as conf_file:
            json.dump(default.to_dict(), conf_file, indent=4)
    with open(config_path, "r") as conf_file:
        conf = json.load(conf_file)
    return conf
