from invoke import task

# TBD if this will be used in conjunction with or as an alternative to docker-compose for local dev.


@task
def pylint(context, directory):
    print(f"Running pylint in {directory}")
    context.run(f"pylint {directory}")


@task
def pytest_cov(context, directory):
    print(f"Running tests with coverage in {directory}")
