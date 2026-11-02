# Wearable Health-Monitoring ARM System - Makefile

.PHONY: help setup test run app lint clean

help:
	@echo "Available commands:"
	@echo "  make setup   - Install project dependencies"
	@echo "  make test    - Run automated pytest suite"
	@echo "  make run     - Execute CLI simulation pipeline"
	@echo "  make app     - Start FastAPI backend server on port 8000"
	@echo "  make lint    - Run code syntax and quality checks"
	@echo "  make clean   - Remove cache, bytecode, and temp files"

setup:
	python -m pip install --upgrade pip
	python -m pip install -r requirements.txt

test:
	python -m pytest tests/ -v

run:
	python -m sim.run --config config/default.yaml

app:
	python -m uvicorn backend.api:app --host 0.0.0.0 --port 8000 --reload

lint:
	python -m compileall sim backend tests

clean:
	python -c "import pathlib, shutil; [shutil.rmtree(p) for p in pathlib.Path('.').rglob('__pycache__')]"
	python -c "import pathlib, shutil; [shutil.rmtree(p) for p in pathlib.Path('.').rglob('.pytest_cache')]"
