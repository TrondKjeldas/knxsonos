

.PHONY: build
build:
	python setup.py build bdist
	python setup.py build sdist

.PHONY: install
install:
	python setup.py install --user

.PHONY: upload
upload:
	twine upload dist/*
	
.PHONY: test
test:
	coverage run -m unittest discover -s test/

clean:
	rm -Rf dist build
	rm -Rf knxsonos.egg-info
