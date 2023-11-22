#!/usr/bin/env python
from distutils.core import setup

import setuptools

setup(
    name="report-a-breach-prototype",
    version="0.0.1",
    description="Report a trade sanctions breach app",
    packages=setuptools.find_packages(),
    install_requires=[
        "dj-database-url",
        "django",
        "django-dotenv",
        "django-extra-fields",
        "django-filter",
        "django-fsm",
        "django-health-check",
        "django-polymorphic",
        "django-webpack-loader",
        "django_extensions",
        "djangorestframework",
        "psycopg2-binary",
    ],
)
