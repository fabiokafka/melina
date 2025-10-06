#!/bin/bash
cd $(dirname "$0")
source .venv/bin/activate
export FLASK_APP=src/main.py
export FLASK_ENV=production
gunicorn -w 4 -b 0.0.0.0:5000 src.main:app

