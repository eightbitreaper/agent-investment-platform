# Agent Investment Platform - Prerequisites

This document outlines the system requirements and setup prerequisites for the **Agent Investment Platform**. The platform is designed to work cross-platform with a focus on Windows PowerShell compatibility.

## 🎯 Quick Requirements Summary

**Essential:**
- **Python 3.9+** (core platform and MCP servers)
- **Git** (version control and repository management)
- **VS Code** (recommended development environment)

**Optional but Recommended:**
- **Node.js 18+** (for JavaScript MCP servers)
- **Docker** (for containerized deployment)
- **API Keys** (Polygon, NewsAPI, etc. for full functionality)

---

## 🛠️ Development Environment Setup

The Agent Investment Platform uses VS Code as the primary development environment with comprehensive workspace configuration.

### 1. Install VS Code

Download and install VS Code from: [https://code.visualstudio.com/](https://code.visualstudio.com/)

**Installation Options:**
- ✅ "Add to PATH (requires shell restart)"
- ✅ "Register Code as an editor for supported file types"
- ✅ "Add 'Open with Code' action to Windows Explorer context menu"

The project includes a complete **`.vscode/`** workspace configuration with:
- **20 automation tasks** for development, testing, and deployment
- **85+ optimized settings** for Python, MCP, and financial development
- **Recommended extensions** for the best development experience

### 2. Essential VS Code Extensions

The project recommends these extensions for optimal development:

**Core Extensions:**
- **Python** - Python language support and debugging
- **Pylance** - Advanced Python language server
- **GitHub Copilot** - AI-powered code assistance (optional)

**MCP Development:**
- **JSON** - Configuration file editing
- **YAML** - Configuration file support

All recommended extensions are listed in `.vscode/extensions.json` and will be suggested automatically when you open the workspace.

### 3. Verify VS Code Setup

Test your VS Code installation:

```powershell
# Verify VS Code is in PATH
code --version

# Open the project workspace
code d:\code\agent-investment-platform
```

The workspace will automatically load optimized settings and suggest recommended extensions.

---

## 📁 Project Setup and Git Configuration

### 1. Clone the Repository

**Option A: HTTPS Clone (Recommended)**
```powershell
cd d:\code
git clone https://github.com/your-username/agent-investment-platform.git
cd agent-investment-platform
```

**Option B: SSH Clone (if SSH keys configured)**
```powershell
cd d:\code
git clone git@github.com:your-username/agent-investment-platform.git
cd agent-investment-platform
```

3. Initialize git:
   ```bash
   git init
   git branch -m main
   ```

4. Configure Git identity:
   ```bash
   git config --global user.name "your-username"
   git config --global user.email "your-email@example.com"
   ```

5. Generate an SSH key (if not done already):
   ```bash
   ssh-keygen -t ed25519 -C "your_email@example.com"
   eval "$(ssh-agent -s)"
   ssh-add ~/.ssh/id_ed25519
   ```

6. Add the public key to GitHub:
   ```bash
   cat ~/.ssh/id_ed25519.pub
   ```
   Copy the key → go to **GitHub → Settings → SSH and GPG keys → New SSH key**.

7. Authenticate GitHub CLI:
   ```bash
   sudo apt-get update && sudo apt-get install -y gh
   gh auth login            # choose GitHub.com, SSH, and browser login
   ```

8. Create the repo (private):
   ```bash
   gh repo create agent-investment-platform --private --source=. --remote=origin
   git add .
   git commit -m "chore: initial scaffold"
   git push -u origin main
   ```

---

## Option B: Using Windows GitHub Setup (VS Code Insiders + Windows Git)

This option keeps everything on the Windows side so you can work directly from **VS Code Insiders (Windows)** without WSL.

### 1. Install Git for Windows
- Download from: [https://git-scm.com/download/win](https://git-scm.com/download/win)
- During installation:
  - Select *“Git from the command line and also from 3rd-party software”*
  - Enable *“Use bundled OpenSSH”*

Verify:
```powershell
git --version
```

### 2. Generate SSH Key
```powershell
mkdir $HOME\.ssh -ErrorAction SilentlyContinue
ssh-keygen -t ed25519 -C "eightbitreaper@windows" -f $HOME\.ssh\id_ed25519
```

### 3. Enable and Start ssh-agent
Run **PowerShell as Administrator**:
```powershell
Set-Service -Name ssh-agent -StartupType Automatic
Start-Service -Name ssh-agent
Get-Service -Name ssh-agent   # should show Status: Running
```

### 4. Add the Key to ssh-agent
```powershell
ssh-add $env:USERPROFILE\.ssh\id_ed25519
ssh-add -l   # confirm key is listed
```

### 5. Add Key to GitHub
Get the public key:
```powershell
Get-Content $env:USERPROFILE\.ssh\id_ed25519.pub
```
Copy → GitHub → Settings → **SSH and GPG Keys → New SSH key** → paste → Save.

---

## 🐍 Python Environment Setup

The Agent Investment Platform requires **Python 3.9+** for MCP server functionality.

### 1. Install Python

**Verify Existing Installation:**
```powershell
python --version
# Should show Python 3.9.0 or higher
```

**If Python needs installation:**
- **Windows**: Download from [python.org](https://www.python.org/downloads/)
- **Installation**: ✅ "Add Python to PATH"

### 2. Install Project Dependencies

Navigate to the project directory and install required packages:
```powershell
cd d:\code\agent-investment-platform
pip install -r requirements.txt
```

The project includes all necessary dependencies for:
- **MCP Server Framework** (`mcp`, `pydantic`)
- **Financial Data APIs** (`yfinance`, `requests`)
- **Development Tools** (`pytest`, `black`, `pylint`)

### 3. Verify Python Setup

Test that Python and MCP dependencies are working:
```powershell
# Verify MCP installation
python -c "import mcp; print('MCP installed successfully')"

# Run a quick environment check
python scripts/health-check.py
```

---

## 🔧 Optional Components

### API Keys (For Full Functionality)

The platform can work with limited functionality using mock data, but for live financial data, you'll need:

**Polygon API:**
```powershell
# Get free API key from: https://polygon.io/
# Add to .env file:
# POLYGON_API_KEY=your-key-here
```

**NewsAPI (Optional):**
```powershell
# Get free API key from: https://newsapi.org/register
# Add to config/api_config.json:
# "NEWS_API_KEY": "your-key-here"
```

### Node.js (Optional)

For JavaScript-based MCP servers or additional tooling:
```powershell
# Download from: https://nodejs.org/
# Verify installation:
node --version
npm --version
```

### Docker (Optional)

For containerized deployment:
```powershell
# Download Docker Desktop from: https://www.docker.com/products/docker-desktop
# Verify installation:
docker --version
docker-compose --version
```

---

## ✅ Verification Checklist

Before starting development, ensure you have:

- [ ] **VS Code** installed with Python extension
- [ ] **Python 3.9+** in PATH
- [ ] **Git** configured with your identity
- [ ] **Project repository** cloned and accessible
- [ ] **Dependencies installed** via `pip install -r requirements.txt`
- [ ] **Health check passed** via `python scripts/health-check.py`

**Next Steps:**
1. See [CONTRIBUTING.md](CONTRIBUTING.md) for development workflow
2. Check [README.md](../README.md) for project overview
3. Review [architecture.md](architecture.md) for system design

---

## 🆘 Need Help?

**Common Issues:**
- **Python not found**: Ensure Python is added to PATH during installation
- **Permission errors**: Run PowerShell as Administrator for system-wide changes
- **Module import errors**: Verify `pip install -r requirements.txt` completed successfully

**Resources:**
- [Project Documentation](../docs/)
- [Contributing Guidelines](CONTRIBUTING.md)
- [Architecture Overview](architecture.md)
