from typing import Any

from invoke import task


@task
def test(context: Any) -> None:
    context.run("pipenv run pytest tests/")


@task
def unittest(context: Any) -> None:
    context.run("pipenv run pytest tests/test_unit")


@task
def testserver(context: Any) -> None:
    context.run("pipenv run python django_app/manage.py runserver --settings=config.settings.test")


@task
def frontend_tests(context: Any) -> None:
    context.run("pipenv run pytest tests/test_frontend")


@task
def makemigrations(context: Any, app: str | None = None) -> None:
    print("Running manage.py makemigrations")
    if app:
        command = f"pipenv run python django_app/manage.py makemigrations {app}"
    else:
        command = "pipenv run python django_app/manage.py makemigrations"
    context.run(command)


@task
def migrate(context: Any, app: str | None = None) -> None:
    print("Running manage.py migrate")
    if app:
        command = f"pipenv run python django_app/manage.py migrate {app}"
    else:
        command = "pipenv run python django_app/manage.py migrate"
    context.run(command)


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
