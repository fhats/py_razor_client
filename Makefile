.PHONY: clean coverage test tests

clean:

coverage:
	coverage run `which testify` --verbose --summary tests
	coverage report --include=./py_razor_client/* -m

tests: test

test:
	testify tests
