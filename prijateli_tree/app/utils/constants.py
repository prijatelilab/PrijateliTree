# Config Constants
KEY_DATABASE_URI = "SQLALCHEMY_DATABASE_URI"
KEY_DEBUG = "DEBUG"
KEY_ENV = "ENV"
KEY_ENV_DEV = "development"
KEY_ENV_PROD = "production"
KEY_ENV_TESTING = "testing"

# Game Constants
NETWORK_TYPE_INTEGRATED = "integrated"
NETWORK_TYPE_SEGREGATED = "segregated"
NETWORK_TYPE_SELF_SELECTED = "self-selected"

# Validating Regex Constants
REGEX_EMAIL = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"
# Source link: https://stackoverflow.com/a/51829465
REGEX_PHONE_NUMBER = (
    r"^(?:\d{8}(?:\d{2}(?:\d{2})?)?|\(\+?\d{2,3}\)\s?(?:\d{4}[\s*.-]?\d{4}"
    r"|\d{3}[\s*.-]?\d{3}|\d{2}([\s*.-]?)\d{2}\1\d{2}(?:\1\d{2})?))$"
)
