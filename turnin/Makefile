# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    Makefile                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: dmota-ri <dmota-ri@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/04/10 16:50:27 by dmota-ri          #+#    #+#              #
#    Updated: 2026/07/17 20:35:13 by dmota-ri         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

NAME = Fly-in

# DEPENDENCIES = pydantic mypy flake8 protobuf accelerate dotenv

SRC = src

OBJ = $(SRC)/*.py

VENV = .venv/

DEBUGGER = $(PYTHON) pdb
PYTHON = python3 -m
UV_RUN = uv run python -m

RM = rm -fr

.ONESHELL:

run:
	@$(UV_RUN) $(SRC)

run_time:
	@time -f "\n\nTotal Run Time: %E" $(UV_RUN) $(SRC)

debug:
	@$(DEBUGGER) $(MAIN).py

install: $(VENV)

	. $(VENV)bin/activate
	uv sync

$(VENV):
	uv venv $(VENV)

clean:
	@$(RM) ./__pycache__/ ./.mypy_cache/
	@$(RM) ./$(SRC)/__pycache__/ ./$(SRC)/.mypy_cache/
	@$(RM) ./llm_sdk/__pycache__/ ./llm_sdk/.mypy_cache/
	@$(RM) data/output

lint:
	@$(UV_RUN) flake8 $(OBJ) || true
	@$(UV_RUN) mypy --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs $(OBJ) || true

lint-strict:
	@$(UV_RUN) flake8 $(OBJ) || true
	@$(UV_RUN) mypy --strict $(OBJ) || true

%:
	@:
