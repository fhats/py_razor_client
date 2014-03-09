.PHONY: clean coverage test tests

clean:
	find . -name '*.pyc' -delete

coverage:
	coverage run `which testify` --verbose --summary tests
	coverage report --include=./py_razor_client/* -m

tests: test

test:
	testify tests
