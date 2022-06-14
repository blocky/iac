BLUE='\033[0;34m'
NC='\033[0m' # No Color

run:
	export FLASK_APP=gateway/gateway && flask run

test-unit:
	py.test tests/unit

test-live:
	py.test tests/live

test: test-unit

lint:
	@echo "\n${BLUE}Running Pylint against source and test files...${NC}\n"
	@pylint --rcfile=setup.cfg **/*.py
	@echo "\n${BLUE}Running Flake8 against source and test files...${NC}\n"
	@python -m flake8
	@echo "\n${BLUE}Running Bandit against source files...${NC}\n"
	@bandit -r --ini setup.cfg

clean:
	rm -rf tests/unit/.pytest_cache tests/live/.pytest_cache .coverage coverage.xml

veryclean: clean
	find . | grep -E "(__pycache__|\.pyc|\.pyo)" | xargs rm -rf

.PHONY: clean image-clean build-prod push test lint
