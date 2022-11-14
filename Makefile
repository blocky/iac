BLUE=\033[0;34m
NC=\033[0m # No Color
pyiac ?= python -m iac

run:
	@python -m iac

test-unit:
	@py.test

test-live:
	@py.test --pyiac="$(pyiac)" tests/live

test: test-unit

format:
	@echo "\n${BLUE}Running Black against source and test files...${NC}\n"
	@black .

lint:
	@echo "\n${BLUE}Running Black against source and test files...${NC}\n"
	@black . --check
	@echo "\n${BLUE}Running Pylint against source...${NC}\n"
	@pylint iac/**
	@echo "\n${BLUE}Running Pylint against tests...${NC}\n"
	@pylint -d invalid-name tests/**
	@echo "\n${BLUE}Running Flake8 against source and test files...${NC}\n"
	@python -m flake8p
	@echo "\n${BLUE}Running Bandit against source files...${NC}\n"
	@bandit -r . -c "pyproject.toml"
	@echo "\n${BLUE}Running poetry check against pyproject.toml...${NC}\n"
	@poetry check

clean:
	@find -type f -name coverage.xml -delete
	@find -type f -name .coverage -delete
	@find -type d -name .pytest_cache -exec rm -rf {} +

veryclean: clean
	@find . | grep -E "(__pycache__|\.pyc|\.pyo)" | xargs rm -rf

.PHONY: clean image-clean build-prod push test lint
