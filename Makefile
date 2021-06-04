docs:
	make -C docs make html

release:
	python setup.py sdist
	twine upload dist/* --verbose

test:
	pipenv run pytest -vvv

install:
	pipenv install
	pipenv install --dev

tox:
	pipenv run tox