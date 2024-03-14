import environ

from .base import *  # noqa

env = environ.Env(
    DEBUG=(bool, False),
)

TEST_EMAIL_VERIFY_CODE = True

HEADLESS = env.bool("HEADLESS", default=True)

BASE_FRONTEND_TESTING_URL = env.str("BASE_FRONTEND_TESTING_URL", default="http://localhost:8000")
