# report-a-breach-prototype
Initial poc and prototype work for the report a trade sanctions breach service.

### Setup
The project requires Python 3.11

```
# create your virtual env
virtualenv venv

# activate it
source venv/bin/activate

# install the requirements
pip install -r requirements.txt

# run pip freeze if any new dependencies are added
pip freeze > requirements.txt
```

Ensure pre-commit is installed properly:\
`pre-commit --version`\
Install the repos pre commit hooks:\
`pre-commit install`\
Set pre-commit to autoupdate:\
`pre-commit autoupdate`

Install Postgresql (MacOs)
https://www.postgresql.org/download/macosx/

Setup your local environment variables
```
cd core
touch .env
```
The project currently requires 3 env variables. SECRET_KEY, DB_USER, DB_PASSWORD.
SECRET_KEY can be generated using the django get_random_secret_key method. The DB_USER and DB_PASSWORD will need to
be populated with your local postgresql user and password. Note: the name of the prototype DB is "breach_prototype" and it should be configured to run from port 5432.
5432 is the default port Django will use for the backend postgresql engine.

Install node via the web or homebrew (optional - not needed for current prototype)
`brew install node`

Initialize npm (optional)

`npm init`

### Run the prototype
After following the setup (except for the optional node install), use the following to run the web app \
`python manage.py runserver`\
Django will provide the local url which should be http://127.0.0.1:8000/ \
Navigate to http://127.0.0.1:8000/report_a_breach in your browser to run through the prototype. \
Important to note that at this stage in the prototype, gov notify will not work unless you provide a DBT email address.

### Useful django commands
Along with the above runserver command, while developing on the project, \
the following will be handy when making changes to the db model:\
`python manage.py makemigrations`\
`python manage.py migrate`
