from invoke import task


@task
def pylint(context, directory):
    print(f"Running pylint in {directory}")
    context.run(f"pylint {directory}")


@task
def pytest(context, project):
    print(f"Running tests with coverage against {project}")
    # TODO: this requires testing config
    context.run(f"pytest --cov={project} tests/")


@task
def makemigrations(context, app="report_a_breach"):
    print("Running manage.py makemigrations")
    context.run(f"pipenv run python django_app/manage.py makemigrations {app}")


@task
def migrate(context, app="report_a_breach"):
    print("Running manage.py migrate")
    base_command = "pipenv run python django_app/manage.py migrate"
    if app:
        base_command += f" {app}"
    context.run(base_command)


@task
def runserver(context):
    context.run("pipenv run python django_app/manage.py runserver", hide=False, pty=True)


@task
def createsuperuser(context):
    context.run("pipenv run python django_app/manage.py createsuperuser", hide=False, pty=True)


@task
def collectstatic(context):
    context.run("pipenv run python django_app/manage.py collectstatic --no-input", hide=False, pty=True)


@task
def black(context, directory="."):
    print("Running black formatting")
    context.run(f"pipenv run black {directory}")
