# Variables
PYTHON      = python3
VENV        = venv
PIP         = $(VENV)/bin/pip
PY          = $(VENV)/bin/python
MAIN        = pac-man.py
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
	rm -rf build dist
	rm -rf pacman_release pacman_release.zip

lint:
	@echo "$(GREEN)Running linter...(flake8 + mypy)...$(RESET)"
	$(VENV)/bin/flake8 . --exclude=$(VENV)
	$(VENV)/bin/mypy --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs . --exclude $(VENV)

lint-strict:
	@echo "$(GREEN)Running linter -strict...$(RESET)"
	$(VENV)/bin/flake8 . --exclude=$(VENV)
	$(VENV)/bin/mypy --strict . --exclude $(VENV)

package:
	@echo "$(GREEN)Building executable with PyInstaller...$(RESET)"
	$(VENV)/bin/pyinstaller --onefile --noconsole pac-man.py
	@echo "$(GREEN)Preparing release folder...$(RESET)"
	@rm -rf pacman_release pacman_release.zip
	@mkdir -p pacman_release
	@cp -r dist/pac-man* pacman_release/
	@cp -r assets pacman_release/
	@cp config.json pacman_release/
	@cp instructions.txt pacman_release/
	@echo "$(GREEN)Zipping the release...$(RESET)"
	@zip -r pacman_release.zip pacman_release/
	@echo "$(GREEN)Done! pacman_release.zip is ready$(RESET)"