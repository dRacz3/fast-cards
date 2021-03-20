prepare:
	python -m virutalenv .ve
	source .ve/bin/activate
	pip install -r requirements.txt

test:
	pytest --cov-report html --cov=src tests

format:
	black src tests

lint:
	mypy src tests

lnf:
	black src tests
	mypy src tests
