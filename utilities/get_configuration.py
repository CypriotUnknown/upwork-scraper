import os
import json


def get_configuration_file() -> dict:
    config_file_path = os.getenv("CONFIG_PATH", "conf.json")
    if os.path.exists(config_file_path):
        with open(config_file_path, "r") as file:
            return json.load(file)

    return {}
