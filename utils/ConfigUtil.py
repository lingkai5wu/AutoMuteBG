import os
import shutil

import pkg_resources
import yaml
from injector import singleton, inject


@singleton
class ConfigUtil:
    @inject
    def __init__(self):
        self.config_file = "config.yaml"
        self.default_config_path = pkg_resources.resource_filename(__name__, "../resource/default_config.yaml")
        self.config = None
        self.default_config = None

        self._read()

    config = None

    def _read(self):
        if not os.path.exists(self.config_file):
            shutil.copy2(self.default_config_path, self.config_file)
        with open(self.config_file, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)
        self._verify()

    def _verify(self):
        with open(self.default_config_path, "r", encoding="utf-8") as f:
            self.default_config = yaml.safe_load(f)
        try:
            self._verify_consistency(self.config["setting"], self.default_config["setting"])
            self._verify_consistency(self.config["default"], self.default_config["default"])
        except KeyError:
            self._reset()

    def _verify_consistency(self, target_config, reference_config):
        for key in reference_config:
            if key not in target_config:
                self._reset()
            if isinstance(reference_config[key], dict) and isinstance(target_config[key], dict):
                self._verify_consistency(target_config[key], reference_config[key])

    def _reset(self):
        if os.path.exists(self.config_file):
            shutil.move(self.config_file, "backup_" + self.config_file)
        shutil.copy2(self.default_config_path, self.config_file)
        raise CustomException(f"Configuration file verification failed. {self.config_file} has been reset. "
                              f"Please modify and run the program again.")

    def get_by_process(self, process_name):
        def merge_configs(parent_config, child_config):
            if not set(child_config.keys()).issubset(set(parent_config.keys())):
                raise CustomException(f"Process configuration error for {process_name}.", child_config)
            merged = parent_config.copy()
            for key, value in child_config.items():
                if key in merged and isinstance(value, dict) and isinstance(merged[key], dict):
                    merged[key] = merge_configs(merged[key], value)
                else:
                    merged[key] = value
            return merged

        process_config = self.config["processes"][process_name]
        if process_config is None:
            return self.config["default"]
        default_config = self.config["default"].copy()
        return merge_configs(default_config, process_config)


class CustomException(Exception):
    pass
