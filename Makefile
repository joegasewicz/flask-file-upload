docs:
	make -C docs html

release:
	python setup.py sdist
	twine upload dist/* --verbose

test:
	pipenv run pytest -vvv

install:
	pipenv install
	pipenv install --dev
