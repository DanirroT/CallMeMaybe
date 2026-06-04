# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    Makefile                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: dmota-ri <dmota-ri@student.42lisboa.com    +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/04/10 16:50:27 by dmota-ri          #+#    #+#              #
#    Updated: 2026/05/27 17:16:07 by dmota-ri         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

NAME = Fly-in

DEPENDENCIES = pydantic mypy flake8 pygame

MAIN = main

# MAP_FILE = maps/easy/01_linear_path.txt
# MAP_FILE = maps/easy/02_simple_fork.txt
# MAP_FILE = maps/easy/03_basic_capacity.txt

# MAP_FILE = maps/medium/01_dead_end_trap.txt
# MAP_FILE = maps/medium/02_circular_loop.txt
# MAP_FILE = maps/medium/03_priority_puzzle.txt

# MAP_FILE = maps/hard/01_maze_nightmare.txt
# MAP_FILE = maps/hard/02_capacity_hell.txt
# MAP_FILE = maps/hard/03_ultimate_challenge.txt

MAP_FILE = maps/challenger/01_the_impossible_dream.txt

## Unused

# MAP_FILE = maps/easy/02_simple_fork_copy.txt
# MAP_FILE = maps/easy/03_basic_capacity_copy.txt

# MAP_FILE = maps/challenger/0X_own_map_test.txt

# MAP_FILE = maps/hard/0X_ultimate_decision.txt

OBJ = src/*.py main.py

NO_PG_MSG = PYGAME_HIDE_SUPPORT_PROMPT=1

VENV = .venv/

DEBUGGER = $(PYTHON) pdb
PYTHON = python3 -m

RM = rm -fr

.ONESHELL:

run:
	$(NO_PG_MSG) $(PYTHON) $(MAIN) $(MAP_FILE)
# 	$(NO_PG_MSG) $(PYTHON) $(MAIN) $(filter-out $@,$(MAKECMDGOALS))

test_all:
	@export PYGAME_HIDE_SUPPORT_PROMPT=1
	@echo
	@echo Easy
	@echo "\nlinear path"
	$(NO_PG_MSG) $(PYTHON) $(MAIN) maps/easy/01_linear_path.txt
	@echo "\nsimple fork"
	$(NO_PG_MSG) $(PYTHON) $(MAIN) maps/easy/02_simple_fork.txt
	@echo "\nbasic capacity"
	$(NO_PG_MSG) $(PYTHON) $(MAIN) maps/easy/03_basic_capacity.txt

# 	@echo "\nsimple fork - Copy"
# 	$(NO_PG_MSG) $(PYTHON) $(MAIN) maps/easy/02_simple_fork_copy.txt
# 	@echo "\nbasic capacity - Copy"
# 	$(NO_PG_MSG) $(PYTHON) $(MAIN) maps/easy/03_basic_capacity_copy.txt

	@echo
	@echo
	@echo Medium
	@echo "\ndead end trap"
	$(NO_PG_MSG) $(PYTHON) $(MAIN) maps/medium/01_dead_end_trap.txt
	@echo "\ncircular loop"
	$(NO_PG_MSG) $(PYTHON) $(MAIN) maps/medium/02_circular_loop.txt
	@echo "\npriority puzzle"
	$(NO_PG_MSG) $(PYTHON) $(MAIN) maps/medium/03_priority_puzzle.txt

	@echo
	@echo
	@echo Hard
	@echo "\nmaze nightmare"
	$(NO_PG_MSG) $(PYTHON) $(MAIN) maps/hard/01_maze_nightmare.txt  # map Error??
	@echo "\ncapacity hell"
	$(NO_PG_MSG) $(PYTHON) $(MAIN) maps/hard/02_capacity_hell.txt
	@echo "\nultimate challenge"
	$(NO_PG_MSG) $(PYTHON) $(MAIN) maps/hard/03_ultimate_challenge.txt

	@echo
	@echo
	@echo Challenger
	@echo "\nthe impossible dream"
	$(NO_PG_MSG) $(PYTHON) $(MAIN) maps/challenger/01_the_impossible_dream.txt

# 	@echo "\n0X_own_map_test"
# 	$(NO_PG_MSG) $(PYTHON) $(MAIN) maps/challenger/0X_own_map_test.txt

	@echo
	@echo "All Tests Done"

debug:
	$(DEBUGGER) $(MAIN).py $(MAP_FILE)

%:
	@:

install: $(VENV)
	. $(VENV)bin/activate
	pip install $(DEPENDENCIES)

$(VENV):
	$(PYTHON) venv $(VENV)

clean:
	@$(RM) ./__pycache__/ ./.mypy_cache/
	@$(RM) ./src/__pycache__/ ./src/.mypy_cache/

lint:
	@flake8 $(OBJ) || true
	@mypy --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs $(OBJ) || true

lint-strict:
	@flake8 $(OBJ) || true
	@$(PYTHON) mypy --strict $(OBJ) || true
# 	@mypy --strict $(OBJ) || true
