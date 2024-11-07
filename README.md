# Assignment

## Installation & setup
`git clone git@github.com:salmpan/assignment.git`

### Create a Python virtual environment and activate it
```
cd assignment
python3 -m venv env
source env/bin/activate`
```
### Install dependencies
`pip install -r requirements.txt` 

## Run API and import data
`uvicorn main:app --reload`

When API is launched, a new SQLITE DB, including all required tables, is created. This happens if DB or tables don't exist allready.

* API is accessible at localhost:8000
* API documentation (Swagger) is available at localhost:8000/docs
* In order to import data from Star Wars API, simply `HTTP GET http://localhost:8000/import`

## Unit tests
* In order to run tests, type `pytest`
* In order to run tests and produce a coverage report, type: `pytest --cov`

## Notes
* For available endpoints please refer to documentation
* This API imports data from Star Wars API. You can access or search them by name but you can't import your own data.
* `HTTP GET http://localhost:8000/import` invokes importer functionality. A new entry is added in case no such entry (by SW API id) exists allready in local DB.
