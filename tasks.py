from invoke import task


@task
def pylint(context, directory):
    print(f"Running pylint in {directory}")
    context.run(f"pylint {directory}")


@task
def pytest_cov(context, project):
    print(f"Running tests with coverage against {project}")
    # TODO: test with and without config
    context.run(f"pytest --cov={project} tests/")


@task
def migrate(context):
    print(f"Running migrate")
    context.run(f"pipenv run python manage.py migrate")


@task
def black(context, directory="."):
    print(f"Running black formatting")
    context.run(f"pipenv run black {directory}")
