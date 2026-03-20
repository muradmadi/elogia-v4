# Agentic SDR Backend - Makefile
# Automated setup and development commands

.PHONY: help setup venv install migrate run dev test clean

# Default target
help:
	@echo "Available commands:"
	@echo "  make setup      - Create virtual environment and install dependencies"
	@echo "  make venv       - Create virtual environment only"
	@echo "  make install    - Install dependencies in existing venv"
	@echo "  make migrate    - Run database migrations"
	@echo "  make run        - Start the development server"
	@echo "  make dev        - Start server with auto-reload"
	@echo "  make test       - Run tests"
	@echo "  make clean      - Remove venv and __pycache__ directories"
	@echo "  make shell      - Activate virtual environment (Windows)"
	@echo "  make shell-unix - Activate virtual environment (Unix/Mac)"

# Create virtual environment
venv:
	@echo "Creating Python virtual environment..."
	python -m venv .venv
	@echo "Virtual environment created at .venv/"
	@echo ""
	@echo "To activate on Windows:"
	@echo "  .venv\\Scripts\\activate"
	@echo ""
	@echo "To activate on Unix/Mac:"
	@echo "  source .venv/bin/activate"

# Install dependencies
install:
	@echo "Installing dependencies from requirements.txt..."
	.venv/Scripts/pip install -r requirements.txt
	@echo "✓ Dependencies installed successfully"

# Setup everything (venv + install)
setup: venv install
	@echo ""
	@echo "✓ Setup complete!"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Copy .env.example to .env and configure your database"
	@echo "  2. Run: make migrate"
	@echo "  3. Run: make dev"
	@echo ""
	@echo "To activate virtual environment:"
	@echo "  Windows: .venv\\Scripts\\activate"
	@echo "  Unix/Mac: source .venv/bin/activate"

# Run database migrations
migrate:
	@echo "Running database migrations..."
	.venv/Scripts/alembic upgrade head
	@echo "✓ Migrations complete"

# Start development server (no reload)
run:
	@echo "Starting FastAPI server..."
	.venv/Scripts/uvicorn app.main:app --host 0.0.0.0 --port 8000

# Start development server with auto-reload
dev:
	@echo "Starting FastAPI server with auto-reload..."
	.venv/Scripts/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
test:
	@echo "Running tests..."
	.venv/Scripts/pytest -v

# Clean up development environment
clean:
	@echo "Cleaning up..."
	@if exist .venv (rmdir /s /q .venv)
	@if exist __pycache__ (rmdir /s /q __pycache__)
	@echo "✓ Cleaned up virtual environment and __pycache__ directories"

# Activate virtual environment (Windows)
shell:
	@echo "Activating virtual environment..."
	@echo "Run: .venv\\Scripts\\activate"

# Activate virtual environment (Unix/Mac)
shell-unix:
	@echo "Activating virtual environment..."
	@echo "Run: source .venv/bin/activate"

# Create initial migration (for new models)
makemigrations:
	@echo "Creating new migration..."
	.venv/Scripts/alembic revision --autogenerate -m "auto"
	@echo "✓ Migration created. Review and run: make migrate"

# Show current database status
db-status:
	@echo "Current database status:"
	.venv/Scripts/alembic current

# Show migration history
db-history:
	@echo "Migration history:"
	.venv/Scripts/alembic history --verbose
