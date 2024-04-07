import os

from everett.manager import (
    ConfigManager,
    ConfigOSEnv,
    ConfigEnvFileEnv,
)


config_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(config_dir, '.conf')

config = ConfigManager([
    ConfigOSEnv(),
    ConfigEnvFileEnv(config_path),
])
