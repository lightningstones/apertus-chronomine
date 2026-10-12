.PHONY: run build dev test

# Starts the project in Docker container (judges requirement)
run:
	docker compose up --build

# Build the docker container without running
build:
	docker compose build

# Local development mode with uvicorn (no docker required)
dev:
	uvicorn src.backend.main:app --host 0.0.0.0 --port 8000 --reload

# Run unit tests and benchmark evaluation
test:
	pytest tests/ -v

# Generate PDF Technical Report (max 6 pages)
pdf:
	python scripts/generate_pdf.py
