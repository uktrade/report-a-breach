from typing import Any

from invoke import task


@task
def test(context: Any) -> None:
    context.run("pipenv run pytest tests/")


@task
def unittest(context: Any) -> None:
    context.run("pipenv run pytest tests/test_unit")


@task
def frontend_tests(context: Any) -> None:
    context.run("pipenv run pytest tests/test_frontend")


@task
def makemigrations(context: Any, app: str = "report_a_suspected_breach") -> None:
    print("Running manage.py makemigrations")
    context.run(f"pipenv run python django_app/manage.py makemigrations {app}")


@task
def migrate(context: Any, app: str = "report_a_suspected_breach") -> None:
    print("Running manage.py migrate")
    base_command = f"pipenv run python django_app/manage.py migrate {app}"
    context.run(base_command)


@task
def runserver(context: Any) -> None:
    context.run("pipenv run python django_app/manage.py runserver", hide=False, pty=True)


@task
def createsuperuser(context: Any) -> None:
    context.run("pipenv run python django_app/manage.py createsuperuser", hide=False, pty=True)


@task
def collectstatic(context: Any) -> None:
    context.run("pipenv run python django_app/manage.py collectstatic --no-input", hide=False, pty=True)


@task
def black(context: Any, directory: str = ".") -> None:
    print("Running black formatting")
    context.run(f"pipenv run black {directory}")


@task
def mypy(context: Any, module: str = "django_app") -> None:
    context.run(f"mypy {module}", hide=False, pty=True)
