#!/bin/bash
export PIPENV_IGNORE_VIRTUALENVS=1 
make run ARGS="$@"