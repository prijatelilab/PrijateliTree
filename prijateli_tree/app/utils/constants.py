# Config Constants
KEY_DATABASE_URI = "DATABASE_URL"
KEY_DEBUG = "DEBUG"
KEY_ENV = "ENV"
KEY_ENV_DEV = "development"
KEY_ENV_PROD = "production"
KEY_ENV_TESTING = "testing"
KEY_LOGIN_SECRET = "LOGIN_SECRET_KEY"

# user id for system
SYSTEM_ID = 0

# File Constants
FILE_MODE_READ = "r"
STANDARD_ENCODING = "utf-8"

# Game Constants
BALL_BLUE = "B"
BALL_RED = "R"
NETWORK_TYPE_INTEGRATED = "integrated"
NETWORK_TYPE_SEGREGATED = "segregated"
NETWORK_TYPE_SELF_SELECTED = "self-selected"
ROLE_ADMIN = "admin"
ROLE_STUDENT = "student"
ROLE_SUPER_ADMIN = "super-admin"
NUMBER_OF_ROUNDS = 10

# Language Constants
LANGUAGE_ALBANIAN = "al"
LANGUAGE_ENGLISH = "en"
LANGUAGE_MACEDONIAN = "mk"
LANGUAGE_TURKISH = "tr"

# Point Constants
WINNING_SCORE = 100
DENIR_FACTOR = 0.25

# Validating Regex Constants
REGEX_EMAIL = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"
# Source link: https://stackoverflow.com/a/51829465
REGEX_PHONE_NUMBER = (
    r"^(?:\d{8}(?:\d{2}(?:\d{2})?)?|\(\+?\d{2,3}\)\s?(?:\d{4}[\s*.-]?\d{4}"
    r"|\d{3}[\s*.-]?\d{3}|\d{2}([\s*.-]?)\d{2}\1\d{2}(?:\1\d{2})?))$"
)
