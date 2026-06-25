"""common.config.Config"""
#########################################################
# Builtin packages
#########################################################
from configparser import ConfigParser

#########################################################
# 3rd party packages
#########################################################
# (None)

#########################################################
# Own packages
#########################################################
from utils import Singleton


class Config(Singleton):
    """
    Usage:
        1. $ cp common/config/config.ini.template common/config/config.ini
        2. put values in each keys in config.ini
        *you can change a path of config.ini in the __initialize func

        e.g.
            from common.config import Config
            config = Config().config
            lp = config["LOG"]["PATH"]
    """
    __config = None

    def __init__(self):
        self.__config = self.__initialize()

    @property
    def config(self) -> ConfigParser:
        """Getter for __config

        Returns:
            self.__config (ConfigParser): Private property __config
        """
        return self.__config

    def __initialize(self) -> ConfigParser:
        config_file = 'common/config/config.ini'

        if self.__config is not None:
            return self.__config

        config = ConfigParser()
        config.read(config_file, encoding="utf-8")

        if config["APP"]["ENV"] == "DEV":
            config_file = 'common/config/config.dev.ini'
            config.read(config_file, encoding="utf-8")
            return config

        return config
