.PHONY: clean coverage test tests

clean:
	find . -name '*.pyc' -delete
	rm -rf dist

coverage:
	coverage run `which testify` --verbose --summary tests
	coverage report --include=./py_razor_client/* -m

tests: test

test:
	testify tests
