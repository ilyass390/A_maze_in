PURPLE := \033[1;35m
RESET  := \033[0m

define log
	@printf "$(PURPLE)%s$(RESET)\n" "$1"
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
	poetry run flake8 .
	$(call log,mypy)
	poetry run mypy . \
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs
