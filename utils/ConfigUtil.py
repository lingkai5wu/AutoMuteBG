import os
import shutil

import pkg_resources
import yaml


class ConfigUtil:
    def __init__(self):
        self.config_file = "config.yaml"
        self.default_config_path = pkg_resources.resource_filename(__name__, "../resource/default_config.yaml")
        self.config = None
        self.default_config = None

        self._read()

    def _read(self):
        with open(self.default_config_path, "r", encoding="utf-8") as f:
            self.default_config = yaml.safe_load(f)
        if not os.path.exists(self.config_file):
            self._reset()
        with open(self.config_file, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)
            self._validate_consistency(self.config["default"], self.default_config["default"])

    def _validate_consistency(self, target_config, reference_config):
        for key in reference_config:
            if key not in target_config:
                self._reset()
                raise CustomException(f"默认配置中缺少 {key}，已重置 {self.config_file}，请修改配置文件后重新运行程序")
            if isinstance(reference_config[key], dict) and isinstance(target_config[key], dict):
                self._validate_consistency(target_config[key], reference_config[key])

    def _reset(self):
        if os.path.exists(self.config_file):
            shutil.move(self.config_file, "backup_" + self.config_file)
        # 复制default_config.yaml到当前目录
        shutil.copy2(self.default_config_path, self.config_file)

    def get_by_process(self, process_name):
        def merge_configs(parent_config, child_config):
            if not set(child_config.keys()).issubset(set(parent_config.keys())):
                raise CustomException(f"{process_name} 进程配置错误", child_config)
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


if __name__ == '__main__':
    config_util = ConfigUtil()
    print(config_util.get_by_process("StarRail.exe"))
