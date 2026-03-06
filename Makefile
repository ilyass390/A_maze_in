CYAN    := \033[36m
GREEN   := \033[32m
YELLOW  := \033[33m
BOLD    := \033[1m
RESET   := \033[0m

define log
	@echo ""
	@echo "$(CYAN)$(BOLD)╔══════════════════════════════════════╗$(RESET)"
	@echo "$(CYAN)$(BOLD)║  $(GREEN)▶ $(YELLOW)$(1)$(CYAN)$(BOLD)$(RESET)"
	@echo "$(CYAN)$(BOLD)╚══════════════════════════════════════╝$(RESET)"
	@echo ""
endef

.PHONY: install run debug clean lint

install:
	$(call log,Installing dependencies)
	poetry install --no-root

run:
	$(call log,Running a_maze_ing)
	poetry run python a_maze_ing.py config.txt

debug:
	$(call log,Debug mode)
	poetry run python -m pdb a_maze_ing.py config.txt

clean:
	$(call log,Cleaning up)
	rm -rf __pycache__ .mypy_cache

lint:
	$(call log,flake8)
	python3 -m flake8 .
	$(call log,mypy)
	python3 -m mypy . \
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs
