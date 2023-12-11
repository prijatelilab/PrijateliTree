import logging
import os

from prijateli_tree.app.utils.constants import (
    KEY_DATABASE_URI,
    KEY_ENV,
    KEY_ENV_DEV,
    KEY_ENV_PROD,
    KEY_ENV_TESTING,
    LANGUAGE_ENGLISH,
)


# Modify later
class BaseConfig:
    def __init__(self):
        # App Settings
        self.DEBUG = False
        self.LANGUAGE = LANGUAGE_ENGLISH
        self.LOG_LEVEL = logging.DEBUG
        self.TESTING = False

        # Database Settings
        self.SQLALCHEMY_DATABASE_URI = os.getenv(KEY_DATABASE_URI)
        self.SQLALCHEMY_ECHO = False

        # Protocol Settings
        self.SITEMAP_URL_SCHEME = "http"


class DevelopmentConfig(BaseConfig):
    def __init__(self):
        super(DevelopmentConfig, self).__init__()
        self.DEBUG = True
        self.SQLALCHEMY_ECHO = True


class TestingConfig(BaseConfig):
    def __init__(self):
        super(TestingConfig, self).__init__()
        self.TESTING = True


class ProductionConfig(BaseConfig):
    def __init__(self):
        super(ProductionConfig, self).__init__()
        self.LOG_LEVEL = logging.INFO
        self.SITEMAP_URL_SCHEME = "https"


config = {
    KEY_ENV_DEV: DevelopmentConfig(),
    KEY_ENV_TESTING: TestingConfig(),
    KEY_ENV_PROD: ProductionConfig(),
}
config["default"] = config.get(
    os.environ.get(KEY_ENV, KEY_ENV_DEV), DevelopmentConfig()
)
