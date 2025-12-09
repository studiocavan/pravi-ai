# Pravi AI - Quick Start Guide

Choose your preferred method to get Pravi AI running in minutes.

## 🚀 Method 1: Automated Setup (Recommended)

**Best for**: First-time users, development

**Linux/macOS/Git Bash:**
```bash
./scripts/setup.sh
```

**Windows (Command Prompt/PowerShell):**
```cmd
scripts\setup.bat
```

This interactive script will:
- ✓ Check requirements
- ✓ Install dependencies
- ✓ Download models
- ✓ Configure everything
- ✓ Start the application

**Time**: 5-10 minutes

---

## 🐳 Method 2: Docker (Easy)

**Best for**: Quick deployment, testing

```bash
# Start everything
make docker-up

# Or manually:
docker-compose up -d
```

**Access**:
- Frontend: http://localhost:3000
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

**Time**: 2-3 minutes (after initial image pull)

**First time?** Download a model:
```bash
docker exec -it pravi-ollama ollama pull mistral:7b
```

---

## ☸️ Method 3: Kubernetes (Production)

**Best for**: Production, scalability

```bash
# Deploy everything
make k8s-deploy

# Or manually:
kubectl apply -f k8s/
```

**Access**:
```bash
# Port forward to access
kubectl port-forward svc/frontend 3000:80 -n pravi-ai
```

**Time**: 5-10 minutes

---

## 💻 Method 4: Manual (Development)

**Best for**: Developers, customization

### Terminal 1: Ollama
```bash
ollama serve
```

### Terminal 2: Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

### Terminal 3: Frontend
```bash
cd frontend
python -m http.server 3000
```

**Access**: http://localhost:3000

**Time**: 10-15 minutes

---

## 🎯 Which Method Should I Use?

| Method | Pros | Cons | Best For |
|--------|------|------|----------|
| **Automated** | Easy, interactive, configures everything | Requires manual model download | First-time users |
| **Docker** | Fast, isolated, reproducible | Requires Docker | Quick testing |
| **Kubernetes** | Scalable, production-ready, resilient | Complex setup | Production |
| **Manual** | Full control, easy debugging | Most steps | Development |

---

## 📋 Prerequisites by Method

### Automated Setup
- ✓ Python 3.8+
- ✓ 10GB disk space
- ✓ Internet connection

### Docker
- ✓ Docker 20.10+
- ✓ Docker Compose 2.0+
- ✓ 15GB disk space
- ✓ Optional: NVIDIA Docker for GPU

### Kubernetes
- ✓ Kubernetes cluster
- ✓ kubectl configured
- ✓ 50GB+ storage
- ✓ Ingress controller

### Manual
- ✓ Python 3.8+
- ✓ Ollama
- ✓ 10GB disk space

---

## 🔥 Super Quick Start (Docker)

The absolute fastest way:

```bash
# Clone and start
git clone <repo-url>
cd pravi-ai
make docker-up

# Download a model (in another terminal)
docker exec -it pravi-ollama ollama pull phi3:mini

# Open browser
open http://localhost:3000
```

**Done!** You should see the chat interface.

---

## ⚡ Common Next Steps

### Download Better Models

```bash
# Small & fast (4GB VRAM)
ollama pull phi3:mini

# Balanced (5GB VRAM) - Recommended
ollama pull mistral:7b

# High quality (8GB VRAM)
ollama pull llama3.1:8b

# Code specialist
ollama pull codellama:7b
```

### Enable Multi-GPU

See [MULTI_GPU_SETUP.md](MULTI_GPU_SETUP.md:1) for dual GPU setup.

### Add Documents

Use the web UI:
1. Click "Add Document"
2. Paste content
3. Add source name
4. Submit

### Enable MCP Tools

```bash
npm install -g @modelcontextprotocol/server-filesystem
```

Then toggle MCP in the UI.

---

## 🆘 Troubleshooting

### "Ollama not found"
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh  # Linux
brew install ollama  # macOS
```

### "LLM shows as offline"
```bash
# Start Ollama
ollama serve

# Or check if running
pgrep ollama
```

### "Port 8000 already in use"
```bash
# Find and kill the process
lsof -ti:8000 | xargs kill -9
```

### "Docker containers won't start"
```bash
# Check logs
docker-compose logs

# Rebuild
docker-compose down
docker-compose build
docker-compose up
```

### "Out of memory"
Use smaller model:
```bash
ollama pull phi3:mini  # Only needs 4GB
```

---

## 📚 Next Steps

1. ✅ Get it running (you're here!)
2. 📖 Read [README.md](README.md:1) for features
3. 🔧 Check [DEPLOYMENT.md](DEPLOYMENT.md:1) for advanced setup
4. 🚀 Try [MULTI_GPU_SETUP.md](MULTI_GPU_SETUP.md:1) for 2x performance
5. 💡 Explore examples in `examples/`

---

## 🎓 Learning Path

**Beginner**:
1. Use automated setup
2. Try the example questions
3. Add your own documents

**Intermediate**:
1. Deploy with Docker
2. Try different models
3. Enable MCP tools

**Advanced**:
1. Set up multi-GPU
2. Deploy to Kubernetes
3. Customize for your needs

---

## 💡 Pro Tips

1. **Start small**: Use `phi3:mini` first, upgrade later
2. **GPU matters**: Big difference in speed with GPU
3. **Document everything**: Better RAG = better answers
4. **Experiment**: Try different models for different tasks
5. **Monitor**: Watch GPU usage with `nvidia-smi`

---

## 🎉 You're Ready!

Pick a method above and get started. Most users should start with the **Automated Setup** or **Docker** method.

Need help? Check:
- [DEPLOYMENT.md](DEPLOYMENT.md:1) - Detailed deployment guide
- [SETUP_GUIDE.md](SETUP_GUIDE.md:1) - Comprehensive setup instructions
- `examples/` - Code examples
- `/docs` endpoint - API documentation (when running)

Happy chatting! 🤖
