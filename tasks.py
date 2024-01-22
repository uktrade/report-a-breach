from invoke import task

# This needs to be a separate utility repo


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
    context.run(f"python manage.py migrate")
