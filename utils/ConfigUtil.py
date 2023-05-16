import yaml


class ConfigUtil:
    DEFAULT_CONFIG = {
        "default": {
            "loop_interval": 0.2,
            "fg_volume": 1,
            "bg_volume": 0,
            "easing": {
                "duration": 0.5,
                "steps": 50
            }
        },
        "processes": {
            "StarRail.exe": None
        }
    }

    def __init__(self):
        self.config_file = "config.yaml"
        self.config = None
        self._read()

    def _read(self):
        try:
            with open(self.config_file, "r") as f:
                self.config = yaml.safe_load(f)
                self._validate_default(self.config["default"], self.DEFAULT_CONFIG["default"])
        except FileNotFoundError:
            self._reset()
            raise CustomException("已重置 config.yaml，请重启")

    def _validate_default(self, config, default_config):
        for key in default_config:
            if key not in config:
                raise CustomException(f"default 中缺少 {key}，请参阅使用说明，或删除 {self.config_file} 后重新运行程序")
            if isinstance(default_config[key], dict) and isinstance(config[key], dict):
                self._validate_default(config[key], default_config[key])

    def _reset(self):
        with open(self.config_file, "w") as f:
            yaml.dump(self.DEFAULT_CONFIG, f)

    def get_by_process(self, process_name):
        def merge_configs(parent_config, child_config):
            if not set(child_config.keys()).issubset(set(parent_config.keys())):
                raise CustomException("配置错误", child_config)
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
    print(config_util.get_by_process("cloudmusic.exe"))
