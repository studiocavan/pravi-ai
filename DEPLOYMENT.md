# Pravi AI - Deployment Guide

Complete guide for deploying Pravi AI using different methods: manual installation, Docker, and Kubernetes.

## Table of Contents

1. [Quick Setup (Automated)](#quick-setup-automated)
2. [Docker Deployment](#docker-deployment)
3. [Kubernetes Deployment](#kubernetes-deployment)
4. [Manual Installation](#manual-installation)
5. [Production Considerations](#production-considerations)

---

## Quick Setup (Automated)

The fastest way to get started is using our automated setup script.

### Prerequisites

- Python 3.8+
- Git (optional)
- Ollama (or the script will help install it)

### Run Setup Script

```bash
# Clone the repository (or download and extract)
git clone <repository-url>
cd pravi-ai

# Run automated setup
chmod +x scripts/setup.sh
./scripts/setup.sh
```

The script will:
- ✓ Check system requirements
- ✓ Install missing dependencies
- ✓ Set up Python virtual environment
- ✓ Install backend packages
- ✓ Download Ollama models
- ✓ Configure the application
- ✓ Optionally start the services

---

## Docker Deployment

Deploy Pravi AI using Docker for containerized, reproducible environments.

### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- NVIDIA Docker (for GPU support)

### Basic Deployment

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### With GPU Support

Edit `docker-compose.yml` and uncomment the GPU sections:

```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: 1
          capabilities: [gpu]
```

Then start:

```bash
docker-compose up -d
```

### Multi-GPU Setup

```bash
# Start with multi-GPU profile
docker-compose --profile multi-gpu up -d
```

This starts:
- Ollama on GPU 0 (port 11434)
- Ollama on GPU 1 (port 11435)
- Backend with multi-GPU enabled
- Frontend

### Download Models

```bash
# Access Ollama container
docker exec -it pravi-ollama bash

# Download model
ollama pull mistral:7b

# For multi-GPU, download to second instance
docker exec -it pravi-ollama-gpu1 bash
ollama pull codellama:7b
```

### Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Docker Commands Reference

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f [service_name]

# Restart a service
docker-compose restart backend

# Stop services
docker-compose stop

# Remove everything
docker-compose down -v

# Check status
docker-compose ps
```

### Persistent Data

Data is stored in Docker volumes:
- `ollama_data`: Ollama models and data
- `chroma_db`: Vector database
- `./logs`: Application logs
- `./data`: User documents

### Updating

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d
```

---

## Kubernetes Deployment

Deploy Pravi AI on Kubernetes for production-scale deployments.

### Prerequisites

- Kubernetes cluster (1.20+)
- kubectl configured
- At least 3 nodes (recommended)
- 50GB storage available
- Ingress controller (nginx)
- Optional: GPU operator for GPU support

### Quick Deploy

```bash
# Create namespace and deploy all components
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -n pravi-ai

# Wait for all pods to be ready
kubectl wait --for=condition=ready pod -l app=backend -n pravi-ai --timeout=300s
```

### Step-by-Step Deployment

#### 1. Create Namespace

```bash
kubectl apply -f k8s/namespace.yaml
```

#### 2. Deploy Ollama

```bash
kubectl apply -f k8s/ollama-deployment.yaml

# Wait for Ollama to be ready
kubectl wait --for=condition=ready pod -l app=ollama -n pravi-ai --timeout=300s

# Download model
kubectl exec -it deployment/ollama -n pravi-ai -- ollama pull mistral:7b
```

#### 3. Deploy Backend

```bash
kubectl apply -f k8s/backend-deployment.yaml

# Check logs
kubectl logs -f deployment/backend -n pravi-ai
```

#### 4. Deploy Frontend

```bash
# First, create ConfigMap with frontend files
kubectl create configmap frontend-files \
  --from-file=frontend/ \
  -n pravi-ai

# Deploy frontend
kubectl apply -f k8s/frontend-deployment.yaml
```

#### 5. Setup Ingress (Optional)

```bash
# Edit ingress.yaml with your domain
vim k8s/ingress.yaml

# Apply ingress
kubectl apply -f k8s/ingress.yaml
```

### GPU Support in Kubernetes

#### Prerequisites

Install NVIDIA GPU Operator:

```bash
kubectl apply -f https://raw.githubusercontent.com/NVIDIA/gpu-operator/master/deployments/gpu-operator/values.yaml
```

#### Enable GPU in Deployment

Edit `k8s/ollama-deployment.yaml` and uncomment:

```yaml
resources:
  limits:
    nvidia.com/gpu: "1"
nodeSelector:
  nvidia.com/gpu: "true"
```

### Access the Application

```bash
# Get the LoadBalancer IP
kubectl get svc frontend -n pravi-ai

# Or use port forwarding
kubectl port-forward svc/frontend 3000:80 -n pravi-ai
```

Visit http://localhost:3000

### Scaling

```bash
# Scale backend
kubectl scale deployment backend --replicas=5 -n pravi-ai

# Scale frontend
kubectl scale deployment frontend --replicas=3 -n pravi-ai
```

### Monitoring

```bash
# View all resources
kubectl get all -n pravi-ai

# Describe a pod
kubectl describe pod <pod-name> -n pravi-ai

# View logs
kubectl logs -f deployment/backend -n pravi-ai

# Execute commands in pod
kubectl exec -it deployment/backend -n pravi-ai -- bash
```

### Updating

```bash
# Update deployment
kubectl set image deployment/backend backend=pravi-ai-backend:v2 -n pravi-ai

# Rollback if needed
kubectl rollout undo deployment/backend -n pravi-ai

# Check rollout status
kubectl rollout status deployment/backend -n pravi-ai
```

### Cleanup

```bash
# Delete all resources
kubectl delete namespace pravi-ai

# Or delete specific components
kubectl delete -f k8s/
```

---

## Manual Installation

For development or custom setups.

### Prerequisites

- Python 3.8+
- Node.js 16+ (for MCP)
- Ollama
- Git

### Step-by-Step

#### 1. Clone Repository

```bash
git clone <repository-url>
cd pravi-ai
```

#### 2. Install Backend

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### 3. Install Ollama

```bash
# Linux
curl -fsSL https://ollama.com/install.sh | sh

# macOS
brew install ollama

# Download model
ollama pull mistral:7b
```

#### 4. Configure

Create `backend/.env`:

```env
ENABLE_MULTI_GPU=false
MULTI_GPU_CONFIG=balanced
HOST=0.0.0.0
PORT=8000
OLLAMA_HOST=http://localhost:11434
```

#### 5. Start Services

Terminal 1 - Ollama:
```bash
ollama serve
```

Terminal 2 - Backend:
```bash
cd backend
source venv/bin/activate
python main.py
```

Terminal 3 - Frontend:
```bash
cd frontend
python -m http.server 3000
```

#### 6. Access

Open http://localhost:3000

---

## Production Considerations

### Security

1. **API Keys**: Never commit API keys to Git
2. **HTTPS**: Use TLS certificates in production
3. **Authentication**: Add user authentication
4. **Rate Limiting**: Implement rate limiting
5. **CORS**: Configure CORS properly

### Performance

1. **Caching**: Enable response caching
2. **CDN**: Use CDN for frontend assets
3. **Load Balancing**: Use load balancer for multiple backends
4. **Database**: Use persistent storage for ChromaDB
5. **Monitoring**: Add Prometheus/Grafana monitoring

### Reliability

1. **Health Checks**: Configure proper health checks
2. **Auto-restart**: Use systemd or supervisor
3. **Logging**: Centralize logs (ELK stack)
4. **Backups**: Regular backups of data
5. **Alerts**: Set up alerting for failures

### Scaling

#### Horizontal Scaling

```bash
# Docker Compose
docker-compose up -d --scale backend=3

# Kubernetes
kubectl scale deployment backend --replicas=5 -n pravi-ai
```

#### Vertical Scaling

Increase resource limits in:
- Docker: `docker-compose.yml`
- Kubernetes: `k8s/*-deployment.yaml`

### Monitoring Stack

```yaml
# Add to docker-compose.yml
prometheus:
  image: prom/prometheus
  ports:
    - "9090:9090"
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml

grafana:
  image: grafana/grafana
  ports:
    - "3001:3000"
  depends_on:
    - prometheus
```

### Backup Strategy

```bash
# Backup ChromaDB
docker cp pravi-backend:/app/chroma_db ./backups/chroma_db_$(date +%Y%m%d)

# Backup Ollama models
docker cp pravi-ollama:/root/.ollama ./backups/ollama_$(date +%Y%m%d)
```

### CI/CD Pipeline

Example GitHub Actions:

```yaml
name: Deploy
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build and push Docker image
        run: |
          docker build -t pravi-ai-backend:${{ github.sha }} .
          docker push pravi-ai-backend:${{ github.sha }}
      - name: Deploy to Kubernetes
        run: |
          kubectl set image deployment/backend backend=pravi-ai-backend:${{ github.sha }}
```

---

## Troubleshooting

### Docker Issues

**Problem**: Container won't start
```bash
# Check logs
docker-compose logs backend

# Rebuild image
docker-compose build --no-cache backend
```

**Problem**: GPU not detected
```bash
# Check NVIDIA Docker
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi
```

### Kubernetes Issues

**Problem**: Pod CrashLoopBackOff
```bash
# Check pod logs
kubectl logs <pod-name> -n pravi-ai

# Describe pod for events
kubectl describe pod <pod-name> -n pravi-ai
```

**Problem**: PVC pending
```bash
# Check storage class
kubectl get storageclass

# Check PVC status
kubectl get pvc -n pravi-ai
```

### General Issues

**Problem**: Out of memory
- Reduce model size
- Increase container memory limits
- Scale down replicas

**Problem**: Slow responses
- Check GPU utilization
- Scale up backend replicas
- Use smaller models

---

## Support

For issues and questions:
- GitHub Issues: <repository-issues-url>
- Documentation: README.md, SETUP_GUIDE.md
- Examples: `examples/` directory

## Resources

- [Docker Documentation](https://docs.docker.com)
- [Kubernetes Documentation](https://kubernetes.io/docs)
- [Ollama Documentation](https://ollama.com)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
