#!/usr/bin/env bash

set -e
set -x

export mode="development"
# export PYTHONPATH=$(pwd)

python app/backend_pre_start.py

uvicorn app.main:app