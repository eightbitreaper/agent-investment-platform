# Local LLM Setup Guide

Comprehensive guide for setting up and configuring local Large Language Models for the Agent Investment Platform.

## Table of Contents

- [Overview](#overview)
- [System Requirements](#system-requirements)
- [Free Local Models (Hugging Face)](#free-local-models-hugging-face)
- [Ollama Setup](#ollama-setup)
- [LM Studio Integration](#lm-studio-integration)
- [Alternative Local LLM Solutions](#alternative-local-llm-solutions)
- [Configuration](#configuration)
- [Performance Optimization](#performance-optimization)
- [Troubleshooting](#troubleshooting)
- [Model Selection Guide](#model-selection-guide)

## Overview

The Agent Investment Platform supports multiple local LLM providers to ensure privacy, reduce costs, and maintain full control over your AI models. This guide covers setup for:

- **Hugging Face Models** (Free, automatically managed)
- **Ollama** (Popular local LLM server)
- **LM Studio** (User-friendly GUI solution)
- **Alternative Solutions** (GPT4All, Jan, etc.)

## System Requirements

### Minimum Requirements
- **RAM**: 8 GB (16 GB recommended)
- **Storage**: 10 GB free space for models
- **CPU**: Modern multi-core processor
- **GPU**: Optional but recommended (NVIDIA with CUDA support)

### Recommended Specifications
- **RAM**: 32 GB or more for larger models
- **GPU**: NVIDIA RTX 3060 or better with 12+ GB VRAM
- **Storage**: SSD with 50+ GB free space
- **CPU**: 8+ cores for faster inference

### GPU Requirements by Model Size
| Model Size | VRAM Required | System RAM | Performance |
|------------|---------------|------------|-------------|
| 3B - 7B    | 4-8 GB       | 8 GB       | Fast        |
| 8B - 13B   | 8-12 GB      | 16 GB      | Good        |
| 70B+       | 24+ GB       | 32+ GB     | Best        |

## Free Local Models (Hugging Face)

The platform includes built-in support for free Hugging Face models optimized for financial analysis.

### Automatic Setup

Use the automated model download script:

```powershell
# Download and configure financial models
python scripts/setup/download-models.py

# Download specific models
python scripts/setup/download-models.py --models "microsoft/Phi-3-mini-4k-instruct" "ProsusAI/finbert"

# List downloaded models
python scripts/setup/download-models.py --list
```

### Included Financial Models

#### 1. Microsoft Phi-3 Mini (2.4 GB)
- **Use Case**: General financial analysis, strategy recommendations
- **Context Length**: 4,096 tokens
- **RAM Required**: 4 GB
- **Strengths**: Fast inference, low resource usage, good reasoning

#### 2. FinBERT (0.4 GB)
- **Use Case**: Financial sentiment analysis, news classification
- **Context Length**: 512 tokens
- **RAM Required**: 2 GB
- **Strengths**: Specialized for financial text, high accuracy

#### 3. All-MiniLM-L6-v2 (0.1 GB)
- **Use Case**: Document embeddings, semantic search
- **Context Length**: 256 tokens
- **RAM Required**: 1 GB
- **Strengths**: Fast embeddings, similarity analysis

### Manual Model Management

```python
# Example: Load a model directly
from transformers import AutoTokenizer, AutoModelForCausalLM

model_name = "microsoft/Phi-3-mini-4k-instruct"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)
```

## Ollama Setup

Ollama provides an easy way to run powerful LLMs locally with a simple API. The platform includes both Docker-based and native installation options.

### Docker Setup (Recommended)

The Agent Investment Platform includes a pre-configured Ollama setup with web interface.

#### Automatic Docker Setup

```powershell
# Start Ollama services with web interface
docker-compose up ollama ollama-webui -d

# Check service status
docker-compose ps

# Access web interface at http://localhost:8080
```

**What's Included**:
- 🤖 **Ollama Server**: API endpoint at http://localhost:11434
- 💻 **Web Chat Interface**: Professional UI at http://localhost:8080
- 🧠 **GPU Acceleration**: Automatic NVIDIA GPU detection and usage
- 📊 **Pre-configured**: Ready for investment analysis

#### Download Financial Models

```powershell
# Download Llama 3.1 8B (recommended for investment analysis)
docker exec ollama-investment ollama pull llama3.1:8b

# Download additional models
docker exec ollama-investment ollama pull mistral:7b      # Faster responses
docker exec ollama-investment ollama pull codellama:7b    # Code analysis
docker exec ollama-investment ollama pull llama3.1:70b   # Best quality (requires 40GB+ RAM)
```

#### Using the Web Interface

1. **Access**: Open http://localhost:8080 in your browser
2. **No Signup**: Authentication disabled for local use
3. **Model Selection**: Choose from downloaded models in the dropdown
4. **Chat**: Start asking investment-related questions immediately

**Example Prompts**:
- "Analyze the current market sentiment for tech stocks"
- "Should I invest $10,000 in AAPL right now?"
- "Create a diversified portfolio for conservative investors"
- "What are the risks of investing in cryptocurrency?"

### Native Installation (Alternative)

#### Windows
```powershell
# Download and install from https://ollama.ai
# Or use winget
winget install Ollama.Ollama
```

#### macOS
```bash
# Download from https://ollama.ai
# Or use Homebrew
brew install ollama
```

#### Linux
```bash
# Install via script
curl -fsSL https://ollama.ai/install.sh | sh

# Or install manually
wget https://ollama.ai/download/ollama-linux-amd64
sudo mv ollama-linux-amd64 /usr/local/bin/ollama
sudo chmod +x /usr/local/bin/ollama
```

### Starting Ollama

```powershell
# Start Ollama server
ollama serve

# The server will run on http://localhost:11434
```

### Recommended Financial Models

#### For General Analysis (Fast)
```powershell
# Llama 3.1 8B - Best balance of speed and capability
ollama pull llama3.1:8b

# Mistral 7B - Alternative fast option
ollama pull mistral:7b

# Phi-3 Medium - Microsoft's efficient model
ollama pull phi3:medium
```

#### For Complex Analysis (High Quality)
```powershell
# Llama 3.1 70B - Highest quality reasoning
ollama pull llama3.1:70b

# Mixtral 8x7B - Good performance with mixture of experts
ollama pull mixtral:8x7b
```

#### For Code Analysis
```powershell
# CodeLlama for strategy code analysis
ollama pull codellama:13b
```

### Ollama Configuration

Update your environment variables:

```bash
# Set Ollama host (optional, defaults to localhost:11434)
export OLLAMA_HOST=http://localhost:11434

# Set timeout for large models
export OLLAMA_TIMEOUT=300

# GPU configuration (if available)
export OLLAMA_GPU_LAYERS=35  # Adjust based on VRAM
```

### Docker Services Configuration

The platform's `docker-compose.yml` includes optimized Ollama configuration:

```yaml
# Ollama service with GPU support
ollama:
  image: ollama/ollama:latest
  container_name: ollama-investment
  ports:
    - "11434:11434"
  volumes:
    - ollama_data:/root/.ollama
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: all
            capabilities: [gpu]

# Professional web interface
ollama-webui:
  image: ghcr.io/open-webui/open-webui:main
  container_name: ollama-webui
  ports:
    - "8080:8080"
  environment:
    - OLLAMA_BASE_URL=http://ollama:11434
    - WEBUI_NAME=🚀 AI Investment Assistant
    - ENABLE_SIGNUP=false
```

### Managing Docker Services

```powershell
# Start services
docker-compose up ollama ollama-webui -d

# Stop services
docker-compose stop ollama ollama-webui

# View logs
docker-compose logs -f ollama
docker-compose logs -f ollama-webui

# Restart services
docker-compose restart ollama ollama-webui
```

## LM Studio Integration

LM Studio provides a user-friendly GUI for running local LLMs with built-in model management.

### Installation

1. Download LM Studio from [https://lmstudio.ai](https://lmstudio.ai)
2. Install the application
3. Launch LM Studio

### Recommended Models for LM Studio

#### Download from LM Studio's Model Library:

1. **Meta Llama 3.1 8B Instruct**
   - File: `Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf`
   - Size: ~4.9 GB
   - Use: General financial analysis

2. **Mistral 7B Instruct**
   - File: `Mistral-7B-Instruct-v0.3-Q4_K_M.gguf`
   - Size: ~4.4 GB
   - Use: Fast analysis and classification

3. **Phi-3 Medium**
   - File: `Phi-3-medium-4k-instruct-Q4_K_M.gguf`
   - Size: ~7.9 GB
   - Use: Balanced performance

### LM Studio Configuration

1. **Start Local Server**:
   - Click "Local Server" tab
   - Load your chosen model
   - Start server on `http://localhost:1234`

2. **Server Settings**:
   - Context Length: 4096-8192 tokens
   - Temperature: 0.1 for analysis, 0.3 for strategy
   - Max Tokens: 2048
   - Enable GPU acceleration if available

3. **Platform Integration**:
   ```yaml
   # Add to config/llm-config.yaml
   providers:
     lmstudio:
       host: "http://localhost:1234"
       api_key: "lm-studio"  # Default API key
       timeout: 120
   ```

## Alternative Local LLM Solutions

### GPT4All

Free, privacy-focused LLM solution:

```powershell
# Install GPT4All
pip install gpt4all

# Or download GUI from https://gpt4all.io
```

**Recommended Models**:
- Mistral 7B OpenOrca
- Llama 2 7B Chat
- Orca Mini 3B

### Jan (ChatGPT Alternative)

Open-source ChatGPT alternative:

1. Download from [https://jan.ai](https://jan.ai)
2. Install and launch
3. Download models through the interface
4. Configure API endpoint integration

### Text Generation WebUI

Advanced solution for developers:

```bash
git clone https://github.com/oobabooga/text-generation-webui.git
cd text-generation-webui
pip install -r requirements.txt
python server.py --api
```

## Configuration

### Platform LLM Configuration

Edit `config/llm-config.yaml` to configure your local LLM setup:

```yaml
# Set default provider
default:
  provider: "ollama"  # or "huggingface", "lmstudio"
  model: "llama3.1:8b"
  temperature: 0.1

# Configure providers
providers:
  ollama:
    host: "http://localhost:11434"
    models:
      - name: "llama3.1:8b"
        use_cases: ["general", "analysis"]
      - name: "llama3.1:70b"
        use_cases: ["complex_analysis", "strategy"]

  lmstudio:
    host: "http://localhost:1234"
    api_key: "lm-studio"

# Task assignments
task_assignments:
  stock_analysis:
    primary: "llama3.1:8b"
    fallback: "microsoft/Phi-3-mini-4k-instruct"
```

### Environment Variables

Create or update your `.env` file:

```bash
# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_TIMEOUT=300

# LM Studio Configuration
LMSTUDIO_HOST=http://localhost:1234
LMSTUDIO_API_KEY=lm-studio

# Hugging Face Configuration
HF_HOME=models/.huggingface_cache
```

## Performance Optimization

### GPU Acceleration

#### NVIDIA CUDA Setup
```powershell
# Install CUDA toolkit (version 11.8 or 12.x)
# Download from https://developer.nvidia.com/cuda-downloads

# Install PyTorch with CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

#### AMD ROCm (Linux)
```bash
# Install ROCm
sudo apt install rocm-dev rocm-libs
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm5.4.2
```

### Memory Optimization

#### Model Quantization
```yaml
# Use quantized models for lower memory usage
ollama_models:
  - "llama3.1:8b-q4_0"  # 4-bit quantization
  - "llama3.1:8b-q8_0"  # 8-bit quantization
```

#### Batch Processing
```python
# Configure batch processing for efficiency
optimization:
  batch_size: 4
  max_sequence_length: 2048
  gradient_checkpointing: true
```

### CPU Optimization

```bash
# Set CPU thread count
export OMP_NUM_THREADS=8
export MKL_NUM_THREADS=8

# Use CPU-optimized models
pip install intel-extension-for-pytorch  # Intel CPUs
```

## Troubleshooting

### Common Issues

#### Ollama Connection Errors
```powershell
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama service
ollama serve

# Check firewall settings (Windows)
netsh advfirewall firewall add rule name="Ollama" dir=in action=allow protocol=TCP localport=11434
```

#### Memory Issues
```powershell
# Check available RAM
Get-ComputerInfo | Select-Object TotalPhysicalMemory, AvailablePhysicalMemory

# Use smaller models or quantization
ollama pull llama3.1:8b-q4_0  # 4-bit quantized version
```

#### GPU Not Detected
```python
# Check GPU availability
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"GPU count: {torch.cuda.device_count()}")

# For Ollama
ollama run llama3.1:8b --verbose  # Check GPU usage
```

#### Model Download Failures
```powershell
# Clear Ollama cache
rm -rf ~/.ollama/models

# Re-download models
ollama pull llama3.1:8b

# For Hugging Face models
python -c "import shutil; shutil.rmtree('models/.huggingface_cache', ignore_errors=True)"
python scripts/setup/download-models.py
```

### Performance Issues

1. **Slow Inference**:
   - Enable GPU acceleration
   - Use quantized models
   - Reduce context length
   - Increase system RAM

2. **High Memory Usage**:
   - Use smaller models (7B instead of 70B)
   - Enable quantization
   - Reduce batch size
   - Close other applications

3. **Connection Timeouts**:
   - Increase timeout values in config
   - Check network connectivity
   - Verify server is running
   - Monitor system resources

## Model Selection Guide

### By Use Case

| Use Case | Recommended Model | Size | Reasoning |
|----------|------------------|------|-----------|
| General Analysis | Llama 3.1 8B | 5 GB | Best balance of performance and speed |
| Quick Classification | Phi-3 Mini | 2.4 GB | Fast inference, low resource usage |
| Sentiment Analysis | FinBERT | 0.4 GB | Specialized for financial sentiment |
| Complex Strategy | Llama 3.1 70B | 40+ GB | Highest reasoning capability |
| Code Analysis | CodeLlama 13B | 7 GB | Optimized for code understanding |
| Document Embeddings | All-MiniLM-L6-v2 | 0.1 GB | Fast semantic embeddings |

### By System Specs

| RAM | GPU VRAM | Recommended Models |
|-----|----------|-------------------|
| 8 GB | None | Phi-3 Mini, FinBERT |
| 16 GB | 4-6 GB | Llama 3.1 8B, Mistral 7B |
| 32 GB | 8-12 GB | Llama 3.1 8B, Mixtral 8x7B |
| 64+ GB | 16+ GB | Llama 3.1 70B, Multiple models |

### Performance Comparison

| Model | Speed | Quality | Memory | Best For |
|-------|-------|---------|---------|----------|
| Phi-3 Mini | [PASS][PASS][PASS][PASS] | [PASS][PASS] | [PASS][PASS][PASS][PASS] | Quick analysis |
| Llama 3.1 8B | [PASS][PASS][PASS] | [PASS][PASS][PASS] | [PASS][PASS] | General use |
| Llama 3.1 70B | [PASS] | [PASS][PASS][PASS][PASS] | [PASS] | Complex reasoning |
| FinBERT | [PASS][PASS][PASS][PASS] | [PASS][PASS][PASS] | [PASS][PASS][PASS][PASS] | Sentiment only |

## Related Documentation

- [Installation Guide](installation-guide.md) - Complete platform setup
- [Configuration Guide](configuration-guide.md) - LLM and strategy configuration
- [Troubleshooting Guide](../troubleshooting/common-issues.md) - Common problems and solutions
- [API Reference](../api/README.md) - Technical API documentation

## Next Steps

1. Choose your preferred local LLM solution
2. Install and configure the selected provider
3. Download appropriate models for your use case
4. Update the platform configuration
5. Test the setup with the validation script
6. Review the [Configuration Guide](configuration-guide.md) for advanced settings

---

For questions or issues with local LLM setup, please refer to the [Troubleshooting Guide](../troubleshooting/common-issues.md) or check the project's GitHub issues.
