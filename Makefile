# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    Makefile                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: dmota-ri <dmota-ri@student.42lisboa.com    +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/04/10 16:50:27 by dmota-ri          #+#    #+#              #
#    Updated: 2026/06/19 00:34:53 by dmota-ri         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

NAME = Fly-in

# DEPENDENCIES = pydantic mypy flake8 protobuf accelerate

# Extra?? - protobuf, accelerate

# /etc/resolv.conf

# nameserver 8.8.8.8
# nameserver 1.1.1.1

SRC = src

OBJ = $(SRC)/*.py

VENV = .venv/

DEBUGGER = $(PYTHON) pdb
PYTHON = python3 -m
UV_RUN = uv run python -m

RM = rm -fr

.ONESHELL:

run:
	@$(UV_RUN) $(SRC) $(filter-out $@,$(MAKECMDGOALS))

NOW = $(shell date +%m-%d_%H:%M)

record:
	@$(UV_RUN) $(SRC) $(filter-out $@,$(MAKECMDGOALS)) | tee Historic/$(NOW).log

#  2>&1
debug:
	@$(DEBUGGER) $(MAIN).py $(MAP_FILE)

%:
	@:

install: $(VENV)

	. $(VENV)bin/activate
	uv sync
# 	uv pip install $(DEPENDENCIES)

$(VENV):
	uv venv $(VENV)

clean:
	@$(RM) ./__pycache__/ ./.mypy_cache/
	@$(RM) ./$(SRC)/__pycache__/ ./$(SRC)/.mypy_cache/

lint:
	@$(UV_RUN) flake8 $(OBJ) || true
	@$(UV_RUN) mypy --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs $(OBJ) || true

lint-strict:
	@$(UV_RUN) flake8 $(OBJ) || true
	@$(UV_RUN) mypy --strict $(OBJ) || true
# 	@mypy --strict $(OBJ) || true
