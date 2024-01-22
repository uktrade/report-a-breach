# report-a-breach-prototype
A prototype for the report a breach service

## Setup
The project requires Python 3.11. Backing services are provided by Docker and Docker Compose whilst the web app itself is ran as a normal process.

### 1. Setting up your virtual environment
We use Pipenv to manage our virtual environment, dependencies, and environment variables. You can install it with either of the following commands:
```
# with homebrew
pip install --user pipenv

# OR with homebrew
brew install pipenv
```
Then we need to install the requirements for the project:
```
pipenv install
```

### 2. Installing pre-commit
Install the repos pre commit hooks:\
`pre-commit install`\
Set pre-commit to autoupdate:\
`pre-commit autoupdate`


### 3. Setup your local environment variables
Copy and paste the `local.env.example` file and rename it to `.env`
```
cp local.env.example .env
```

### 4. Run the backing services
Use docker-compose to run the backing services
```
docker-compose up -d
```

### 5. Run the web server
After following the setup, use the following to run the web app

`pipenv run python manage.py runserver`

Django will provide the local url which should be http://127.0.0.1:8000/, navigate to this in your browser to see through the prototype.

## Useful commands
### Django
Along with the above runserver command, while developing on the project, \
the following will be handy when making changes to the db model:\
`pipenv run python manage.py makemigrations`\
`pipenv run python manage.py migrate`

### Dependencies
To add a new dependency to the project, use the following command:\
`pipenv install <package-name>`


