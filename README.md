  * [Setup](#setup)
    + [1. Setting up your virtual environment](#1-setting-up-your-virtual-environment)
    + [2. Installing pre-commit](#2-installing-pre-commit)
    + [3. Setup your local environment variables](#3-setup-your-local-environment-variables)
    + [4. Setup AWS localstack](#4-setup-aws-localstack)
    + [5. Run the backing services](#5-run-the-backing-services)
    + [6. Setup local custom domains](#6-setup-local-custom-domains)
    + [7. Run the web server](#7-run-the-web-server)
  * [Useful commands](#useful-commands)
    + [Django](#django)
    + [Dependencies](#dependencies)
    + [Localstack](#localstack)
    + [Testing](#testing)
      - [End-to-End tests](#end-to-end-tests)
    + [Single Sign On (SSO)](#single-sign-on--sso-)
  * [Standards](#standards)
    + [Linting and Formatting](#linting-and-formatting)
    + [Branches](#branches)
    + [Commits](#commits)
    + [Pull Requests](#pull-requests)
    + [Local development tools](#local-development-tools)

# report-a-breach-prototype
A prototype for the report a breach service.

## Setup
The project requires Python 3.11. Backing services are provided by Docker whilst the web app itself is ran as a normal process with Pipenv.

### 1. Setting up your virtual environment
We use Pipenv to manage our virtual environment, dependencies, and environment variables. You can install it with either of the following commands:
```
# without homebrew
pip install --user pipenv

# OR with homebrew
brew install pipenv
```
Once installed, we need to install the requirements for the project:
```
pipenv install --dev
```

If you're using homebrew, install libmagic:
```
brew install libmagic
```

Now we need to activate the virtual environment:
```
pipenv shell
```

### 2. Installing pre-commit
Install the repos pre commit hooks:
```
pre-commit install
```
Set pre-commit to autoupdate:
```
pre-commit autoupdate
```


### 3. Setup your local environment variables
Copy and paste the `.env.example` file and rename it to `.env`:
```
cp .env.example .env
```
Ask your colleagues to provide the missing values in your `.env` file.

### 4. Setup AWS localstack

Configure the AWS CLI:
```
aws configure
```

You can use the following dummy credentials that are provided by AWS. Alternatively, you can use your own credentials
if you have an AWS account, Localstack does not validate them anyway:
```
AWS Access Key ID : AKIAIOSFODNN7EXAMPLE
AWS Secret Access Key : wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
Default region : eu-west-2
```

### 5. Run the backing services
Use docker-compose to run the backing services
```
docker-compose up -d
```

Collect the apps static files:

```
invoke collectstatic
```

### 6. Setup local custom domains
Add the below to your `/etc/hosts` file:
```
127.0.0.1       report-a-suspected-breach
127.0.0.1       view-a-suspected-breach
```

### 7. Load the submodules
The first time you clone the repo, you may need to initialise the submodule:
```
git submodule update --init
```

### 8. Run the web server
After following the setup, use the following to run the web app:

`invoke runserver`

Django will provide the local url which should be http://127.0.0.1:8000/. As we use the django sites framework, this will no longer resolve by default. \
To view the report-a-suspected-breach app navigate to: http://report-a-suspected-breach:8000/ \
To view the view-a-suspected-breach app, navigate to: http://view-a-suspected-breach:8000/

## Useful commands
### Django
Along with the above runserver command, while developing on the project, \
the following will be handy when making changes to the db model:

```
invoke makemigrations
invoke migrate
```

### Dependencies
To add a new dependency to the project, use the following command:

```
pipenv install <package-name>
```

### Localstack
We use Localstack to emulate AWS services locally, specifically S3. Two buckets are created on container startup:

- `temporary-document-bucket` that's used to temporarily store uploaded files
- `permanent-document-bucket` that's used to store uploaded files permanently

Localstack works similarly to the awscli. For example, to see objects inside the `temporary-document-bucket` bucket, run command:\
```
awslocal s3 ls temporary-document-bucket
```

### Updating the list of sanctions regimes
We store the list of Sanction regimes in a private git submodule located in `django_app/sanctions_regimes`.
The first time you clone the repo, you may need to initialise the submodule:
```
git submodule update --init
```
If this list has changed, you can update it from the latest version of the submodule by running the following command:
```
git submodule update --remote --merge
```

### Testing

#### End-to-End tests
We use playwright for end-to-end testing.
To run the end-to-end tests for report a breach, start the django server using the test config settings:

```
pipenv run python manage.py runserver --settings=config.settings.test
```

To run end-to-end tests only:\
```
pipenv run pytest tests/test_frontend
```

A useful command for writing end-to-end tests is:
```
pipenv run playwright codegen http://report-a-suspected-breach:8000/
```

### Single Sign On (SSO)
The app works out of the box with Mock SSO, which is part of the Docker Compose setup. If the OAuth 2.0 flow isn't working,
try setting the `AUTHBROKER_URL` to `docker.for.mac.localhost:8080` or `host.docker.internal:8080`
(value varies across platforms). This is because the Mock SSO service (configured with the AUTHBROKER_URL)
must be accessible from outside of docker-compose for the authorization redirect, and also from within docker-compose
to make the access token POST request.

## Standards
### Linting and Formatting
We use:
- [black](https://github.com/psf/black) to ensure consistent formatting across the project.
- [flake8](https://flake8.pycqa.org/en/latest/) to lint the project and flag any common code smells.
- [isort](https://pycqa.github.io/isort/) to ensure imports are ordered correctly.
- [djhtml](https://pypi.org/project/djhtml/) to format and indent our HTML, CSS, and JS files

We use [pre-commit](https://pre-commit.com/) to run all of the above before every commit.

Typing is used throughout the app. We have followed the best practices outlined in [Typing Best Practices](https://typing.readthedocs.io/en/latest/source/best_practices.html)

### Branches
All branches should be created from the `main` branch and be named after the JIRA ticket they are related to. e.g. DST-1234

### Commits
All commits should be made to a branch and not directly to `main`.\
The commit message should contain a clear and concise description of the changes made.

### Pull Requests
All pull requests should be made to `main` and should be named after the JIRA ticket they are related to and a short
description of the functionality implemented. e.g. DST-1234 - Implementing S3 buckets

### Local development tools
We use python-invoke to run various commands in regard to django and linting/formatting. \
These are maintained in tasks.py

All methods in the file can be run by typing `invoke {command}`.\
Note that any command with underscores needs to be called with a `-` instead. \
For example, the following task in tasks.py;
```
@task
def frontend_tests(context: Any) -> None:
    context.run("pipenv run pytest tests/test_frontend")
```
Will be invoked by calling `invoke frontend-tests`

MyPy is used to sanity check typing but is not currently enforced. \
To run mypy against the django_app, call `invoke mypy`

### Accessing the viewer portal

The first time accessing the viewer portal you will automatically be logged in as `vyvyan.holland@email.com` through the
mock Staff SSO server. This user will by default not be able to access the viewer portal as `is_active` is set to False in the DB.

Create a superuser with `pipenv run django_app/manage.py createsuperuser` and log in to the admin panel (`http://view-a-licence:8000/admin`) with the superuser credentials.

In order to access the viewer portal, run the django make_admin_user management command ([details here](https://uktrade.atlassian.net/wiki/spaces/TS1/pages/4664950873/Admin+user+for+viewer+portal)) using `vyvyan.holland@email.com` as the email.
