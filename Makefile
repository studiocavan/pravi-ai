.PHONY: help setup docker-build docker-up docker-down docker-logs k8s-deploy k8s-delete clean

# Default target
help:
	@echo "Pravi AI - Available Commands:"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make setup              - Run automated setup script"
	@echo "  make install            - Install dependencies manually"
	@echo ""
	@echo "Docker Commands:"
	@echo "  make docker-build       - Build Docker images"
	@echo "  make docker-up          - Start all Docker services"
	@echo "  make docker-down        - Stop all Docker services"
	@echo "  make docker-logs        - View Docker logs"
	@echo "  make docker-restart     - Restart Docker services"
	@echo "  make docker-clean       - Remove all Docker resources"
	@echo "  make docker-multi-gpu   - Start with multi-GPU support"
	@echo ""
	@echo "Kubernetes Commands:"
	@echo "  make k8s-deploy         - Deploy to Kubernetes"
	@echo "  make k8s-status         - Check Kubernetes status"
	@echo "  make k8s-logs           - View Kubernetes logs"
	@echo "  make k8s-delete         - Delete from Kubernetes"
	@echo "  make k8s-scale-up       - Scale up backend"
	@echo "  make k8s-scale-down     - Scale down backend"
	@echo ""
	@echo "Development:"
	@echo "  make dev                - Start development server"
	@echo "  make test               - Run tests"
	@echo "  make lint               - Run linters"
	@echo "  make clean              - Clean temporary files"
	@echo ""

# Setup
setup:
	@chmod +x scripts/setup.sh
	@./scripts/setup.sh

install:
	@echo "Installing backend dependencies..."
	@cd backend && python3 -m venv venv && . venv/bin/activate && pip install -r requirements.txt
	@echo "✓ Installation complete"

# Docker commands
docker-build:
	@echo "Building Docker images..."
	@docker-compose build
	@echo "✓ Build complete"

docker-up:
	@echo "Starting Docker services..."
	@docker-compose up -d
	@echo "✓ Services started"
	@echo ""
	@echo "Access points:"
	@echo "  Frontend: http://localhost:3000"
	@echo "  Backend:  http://localhost:8000"
	@echo "  Docs:     http://localhost:8000/docs"

docker-down:
	@echo "Stopping Docker services..."
	@docker-compose down
	@echo "✓ Services stopped"

docker-logs:
	@docker-compose logs -f

docker-restart:
	@echo "Restarting Docker services..."
	@docker-compose restart
	@echo "✓ Services restarted"

docker-clean:
	@echo "Cleaning Docker resources..."
	@docker-compose down -v
	@docker system prune -f
	@echo "✓ Cleanup complete"

docker-multi-gpu:
	@echo "Starting with multi-GPU support..."
	@docker-compose --profile multi-gpu up -d
	@echo "✓ Multi-GPU services started"

# Kubernetes commands
k8s-deploy:
	@echo "Deploying to Kubernetes..."
	@kubectl apply -f k8s/namespace.yaml
	@kubectl apply -f k8s/ollama-deployment.yaml
	@echo "Waiting for Ollama to be ready..."
	@kubectl wait --for=condition=ready pod -l app=ollama -n pravi-ai --timeout=300s
	@kubectl apply -f k8s/backend-deployment.yaml
	@kubectl create configmap frontend-files --from-file=frontend/ -n pravi-ai --dry-run=client -o yaml | kubectl apply -f -
	@kubectl apply -f k8s/frontend-deployment.yaml
	@kubectl apply -f k8s/ingress.yaml
	@echo "✓ Deployment complete"
	@echo ""
	@echo "Check status: make k8s-status"

k8s-status:
	@echo "Kubernetes Status:"
	@kubectl get all -n pravi-ai

k8s-logs:
	@echo "Backend logs:"
	@kubectl logs -f deployment/backend -n pravi-ai

k8s-delete:
	@echo "Deleting from Kubernetes..."
	@kubectl delete namespace pravi-ai
	@echo "✓ Deleted"

k8s-scale-up:
	@echo "Scaling up backend to 5 replicas..."
	@kubectl scale deployment backend --replicas=5 -n pravi-ai
	@echo "✓ Scaled up"

k8s-scale-down:
	@echo "Scaling down backend to 2 replicas..."
	@kubectl scale deployment backend --replicas=2 -n pravi-ai
	@echo "✓ Scaled down"

# Development
dev:
	@echo "Starting development servers..."
	@echo "Terminal 1: Ollama"
	@echo "Terminal 2: Backend"
	@echo "Terminal 3: Frontend"
	@echo ""
	@echo "Run in separate terminals:"
	@echo "  1. ollama serve"
	@echo "  2. cd backend && source venv/bin/activate && python main.py"
	@echo "  3. cd frontend && python -m http.server 3000"

test:
	@echo "Running tests..."
	@cd backend && . venv/bin/activate && pytest

lint:
	@echo "Running linters..."
	@cd backend && . venv/bin/activate && flake8 . && black --check .

clean:
	@echo "Cleaning temporary files..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@rm -rf logs/*.log 2>/dev/null || true
	@echo "✓ Cleanup complete"
