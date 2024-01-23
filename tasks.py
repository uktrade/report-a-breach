from invoke import task


@task
def pylint(context, directory):
    print(f"Running pylint in {directory}")
    context.run(f"pylint {directory}")


@task
def pytest_cov(context, directory):
    print(f"Running tests with coverage in {directory}")


@task
def migrate(context):
    print(f"Running migrate")
    context.run(f"pipenv run python manage.py migrate")


@task
def black(context, directory="."):
    print(f"Running black formatting")
    context.run(f"pipenv run black {directory}")
