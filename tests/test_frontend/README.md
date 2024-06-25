# End-to-End tests
We use playwright for end-to-end testing.
To run the end-to-end tests for report a breach, start the django server using the test config settings:\
`pipenv run python manage.py runserver --settings=config.settings.test`

To run end-to-end tests only:\
`pipenv run pytest tests/test_frontend`\

Currently, end-to-end test must be run as testfiles separately
e.g. `pipenv run pytest tests/test_frontend/test_supply_chain/test_about_the_supplier` as there are some issues when they are run as a full test-suite.

## Test structure
Tests are currently organised in folders corresponding to the sections of the tasklist. Within each folder, each view/form wizard step of report-a-suspected-breach will have it's own testfile.


## Create new tests
A useful command for writing end-to-end tests is:\
`pipenv run playwright codegen http://report-a-suspected-breach:8000/`
