run:
	@uvicorn dio_fastapi_tdd.main:app --reload

precommit-install:
	@poetry run pre-commit install

test:
	@poetry run pytest
