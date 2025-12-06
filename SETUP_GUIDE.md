# Pravi AI - Complete Setup Guide

This guide will walk you through setting up the Pravi AI application from scratch.

## System Requirements

### Minimum Requirements
- **CPU**: Modern multi-core processor
- **RAM**: 8GB system RAM
- **GPU**: Optional, but recommended (4GB+ VRAM)
- **Storage**: 10GB free space for models
- **OS**: Linux, macOS, or Windows

### Recommended Requirements
- **CPU**: 8+ cores
- **RAM**: 16GB system RAM
- **GPU**: NVIDIA GPU with 8GB+ VRAM
- **Storage**: 20GB+ free space

## Step-by-Step Installation

### Step 1: Install Python

Ensure you have Python 3.8 or higher:

```bash
python --version
# Should show Python 3.8.x or higher
```

If not installed:
- **Linux (Ubuntu/Debian)**: `sudo apt install python3 python3-pip python3-venv`
- **macOS**: `brew install python3`
- **Windows**: Download from [python.org](https://www.python.org/downloads/)

### Step 2: Install Ollama

Ollama is required to run local LLMs.

#### Linux
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

#### macOS
```bash
brew install ollama
```

#### Windows
1. Download installer from [ollama.com](https://ollama.com)
2. Run the installer
3. Ollama will start automatically

### Step 3: Download and Start a Model

Choose a model based on your GPU:

#### For 4-6GB GPU (Start here)
```bash
ollama pull mistral:7b
```

#### For 8-10GB GPU
```bash
ollama pull llama3.1:8b
```

#### For 4GB GPU or CPU only
```bash
ollama pull phi3:mini
```

Start Ollama server:
```bash
ollama serve
```

Leave this terminal running. Open a new terminal for the next steps.

### Step 4: Clone/Download the Repository

```bash
# If you have git
git clone <repository-url>
cd pravi-ai

# Or download and extract the ZIP file
```

### Step 5: Set Up the Backend

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

If you encounter errors, try:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 6: Start the Backend

```bash
# Make sure you're in the backend directory with venv activated
python main.py
```

You should see:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Leave this terminal running.

### Step 7: Open the Frontend

Open a new terminal:

```bash
cd frontend
python -m http.server 3000
```

Or simply open `frontend/index.html` directly in your browser.

### Step 8: Access the Application

Open your browser and go to:
- `http://localhost:3000` (if using http.server)
- Or open `frontend/index.html` directly

You should see the Pravi AI interface with green status indicators.

## Verification

Check that everything is working:

1. **Status Indicators**: All three (LLM, RAG, MCP) should show green dots
2. **Test Query**: Try asking "What is Python?"
3. **Response**: You should get a response from the local LLM

## Optional: Set Up MCP (Advanced)

### Install Node.js

MCP servers require Node.js:

- **Linux (Ubuntu/Debian)**:
  ```bash
  curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
  sudo apt-get install -y nodejs
  ```

- **macOS**: `brew install node`
- **Windows**: Download from [nodejs.org](https://nodejs.org)

### Install an MCP Server

```bash
npm install -g @modelcontextprotocol/server-filesystem
```

This allows the AI to access files (in a controlled way).

### Enable in the UI

In the frontend, click the "Enable MCP Tools" checkbox.

## Troubleshooting

### Issue: "Connection refused" or backend not accessible

**Solution:**
1. Check backend is running: `http://localhost:8000/health`
2. Check no firewall is blocking port 8000
3. Try restarting the backend

### Issue: "LLM offline" (red dot)

**Solution:**
1. Check Ollama is running: `ollama list`
2. Restart Ollama: `ollama serve`
3. Verify model is downloaded: `ollama list`

### Issue: Slow responses

**Solutions:**
1. Use a smaller model: `ollama pull phi3:mini`
2. Check GPU is being used (NVIDIA GPU required)
3. Close other GPU-intensive applications

### Issue: Backend crashes on startup

**Solutions:**
1. Check Python version: `python --version` (needs 3.8+)
2. Reinstall dependencies:
   ```bash
   pip uninstall -r requirements.txt -y
   pip install -r requirements.txt
   ```
3. Check for port conflicts (port 8000)

### Issue: "Module not found" errors

**Solution:**
```bash
# Make sure venv is activated
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: CUDA/GPU not detected

**Solution:**
- Ollama automatically uses GPU if available
- Verify with: `nvidia-smi` (should show GPU info)
- If no GPU, Ollama will use CPU (slower but works)

## Model Management

### List installed models
```bash
ollama list
```

### Remove a model
```bash
ollama rm mistral:7b
```

### Update a model
```bash
ollama pull mistral:7b
```

### Check model info
```bash
ollama show mistral:7b
```

## Performance Tips

### For Best Performance

1. **Use GPU**: Ensure NVIDIA GPU drivers are installed
2. **Right-size model**: Don't use models larger than your VRAM
3. **Close other apps**: Free up GPU memory
4. **SSD storage**: Store models on SSD for faster loading

### Memory Usage by Model

| Model | VRAM (GPU) | RAM (CPU) | Speed |
|-------|------------|-----------|-------|
| phi3:mini | 4GB | 8GB | Fast |
| mistral:7b | 5GB | 10GB | Fast |
| llama3.1:8b | 8GB | 12GB | Medium |
| gemma2:9b | 9GB | 14GB | Medium |

## Advanced Configuration

### Change Backend Port

Edit `backend/main.py`:
```python
uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
```

Update `frontend/app.js`:
```javascript
const API_BASE_URL = 'http://localhost:8080';
```

### Use Different Model

Edit `backend/llm_service.py`:
```python
self.default_model = "phi3:mini"  # Change here
```

### Customize RAG Settings

Edit `backend/rag_service.py`:
```python
# Change number of results returned
top_k = 5  # Increase for more context

# Change embedding model
# (edit in collection creation)
```

## Running in Production

### Using Docker (Optional)

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Running as a Service

Create a systemd service (Linux):

```ini
[Unit]
Description=Pravi AI Backend
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/pravi-ai/backend
ExecStart=/path/to/pravi-ai/backend/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## Getting Help

1. Check the main README.md
2. Review API docs at `http://localhost:8000/docs`
3. Look at example code in `examples/` directory
4. Check Ollama docs at [ollama.com](https://ollama.com)

## Next Steps

Once everything is running:

1. **Add custom documents**: Use the "Add Document" button
2. **Experiment with models**: Try different models
3. **Enable MCP**: Explore tool integration
4. **Review examples**: Learn from code in `examples/`
5. **Customize**: Modify the UI and backend to your needs

## Uninstallation

To remove everything:

```bash
# Remove models
ollama rm mistral:7b
ollama rm llama3.1:8b

# Uninstall Ollama
# Linux: sudo rm -rf /usr/local/bin/ollama
# macOS: brew uninstall ollama
# Windows: Use Control Panel

# Remove Python environment
cd pravi-ai/backend
rm -rf venv

# Remove the directory
cd ../..
rm -rf pravi-ai
```

## FAQ

**Q: Do I need an internet connection?**
A: Only for initial setup (downloading models). After that, everything runs locally.

**Q: Can I use this without a GPU?**
A: Yes! It will use CPU but will be slower. Use phi3:mini for best CPU performance.

**Q: How much does this cost?**
A: It's completely free! No API costs since everything runs locally.

**Q: Is my data private?**
A: Yes! Nothing is sent to external servers. Everything stays on your machine.

**Q: Can I use commercial LLM APIs instead?**
A: Yes, check the `examples/` directory for OpenAI and Anthropic integration examples.

**Q: How do I update the application?**
A: Pull the latest code and restart the backend. Models stay cached.
