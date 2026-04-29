# Variables
PYTHON      = python3
VENV        = venv
PIP         = $(VENV)/bin/pip
PY          = $(VENV)/bin/python
MAIN        = MON_RENDUGRAPHIQUEPROPREETPASDEGUELASSECOEMMETOI.py
CONFIG      = config.json

# Couleurs
GREEN       = \033[0;32m
RESET       = \033[0m

.PHONY: install run debug clean lint lint-strict

install:
	@echo "$(GREEN)Installing environment and dependencies...$(RESET)"
	@$(PYTHON) -m venv $(VENV)
	@$(PIP) install -q --upgrade pip
	@$(PIP) install -q flake8 mypy
	@if [ -f requirements.txt ]; then $(PIP) install -r requirements.txt; fi

run:
	@echo "$(GREEN)Launching game...$(RESET)"
	$(PY) $(MAIN) $(CONFIG)

debug:
	@echo "$(GREEN)Launching in debug mode...$(RESET)"
	$(PY) -m pdb $(MAIN) $(CONFIG)

clean:
	@echo "$(GREEN)Cleaning temporary files...$(RESET)"
	rm -rf __pycache__ .mypy_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

lint:
	@echo "$(GREEN)Running linter...(flake8 + mypy)...$(RESET)"
	$(VENV)/bin/flake8 .
	$(VENV)/bin/mypy --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs .

lint-strict:
	@echo "$(GREEN)Running linter -strict...$(RESET)"
	$(VENV)/bin/flake8 .
	$(VENV)/bin/mypy --strict .