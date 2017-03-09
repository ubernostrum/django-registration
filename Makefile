PACKAGE_NAME=registration
TESTING_VENV_NAME=${PACKAGE_NAME}_test

ifndef PYTHON_VERSION
PYTHON_VERSION=3.6.0
endif

ifndef DJANGO_VERSION
DJANGO_VERSION=1.10
endif

.PHONY: clean
clean:
	python setup.py clean
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg*/
	rm -rf ${PACKAGE_NAME}/__pycache__/
	rm -rf ${PACKAGE_NAME}/tests/__pycache__/
	find ${PACKAGE_NAME} -type f -name '*.pyc' -delete
	rm -f MANIFEST
	rm -rf coverage .coverage .coverage*
	pip uninstall -y Django

.PHONY: venv
venv:
	[ -e ~/.pyenv/versions/${TESTING_VENV_NAME} ] && \
	echo "\033[1;33mA ${TESTING_VENV_NAME} pyenv already exists. Skipping pyenv creation.\033[0m" || \
	pyenv virtualenv ${PYTHON_VERSION} ${TESTING_VENV_NAME}
	pyenv local ${TESTING_VENV_NAME}
	pip install --upgrade pip setuptools

.PHONY: teardown
teardown: clean
	pyenv uninstall -f ${TESTING_VENV_NAME}
	rm .python-version

.PHONY: django
django:
	pip install Django~=${DJANGO_VERSION}.0

.PHONY: test_dependencies
test_dependencies:
	[ -e test_requirements.txt ] && \
	pip install -r test_requirements.txt || \
	echo "\033[1;33mNo test_requirements.txt found. Skipping install of test_requirements.txt.\033[0m"
	pip install -r test_requirements.txt

.PHONY: lint
lint: test_dependencies
	flake8 ${PACKAGE_NAME}

.PHONY: test
test: django lint
	[ -e requirements.txt ] \
	&& pip install -r requirements.txt || \
	echo "\033[1;33mNo requirements.txt found. Skipping install of requirements.txt.\033[0m"
	pip install -e .
	coverage run ${PACKAGE_NAME}/runtests.py
	coverage report -m
