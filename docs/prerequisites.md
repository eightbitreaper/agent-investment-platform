# Prerequisites

This document explains how to set up the environment for contributing to the **Agent Investment Platform** project.  
It covers both **WSL-based setup** and **Windows-native GitHub setup**.

---

## VS Code Insiders and GitHub Copilot Setup

Before configuring GitHub, set up your development environment with VS Code Insiders and GitHub Copilot.

### 1. Install VS Code Insiders

VS Code Insiders provides access to the latest features and updates.

1. Download VS Code Insiders from: [https://code.visualstudio.com/insiders/](https://code.visualstudio.com/insiders/)
2. Run the installer and follow the installation wizard
3. During installation, make sure to check:
   - ✅ "Add to PATH (requires shell restart)"
   - ✅ "Register Code as an editor for supported file types"
   - ✅ "Add 'Open with Code' action to Windows Explorer file context menu"
   - ✅ "Add 'Open with Code' action to Windows Explorer directory context menu"

### 2. Install and Configure GitHub Copilot Extension

GitHub Copilot provides AI-powered code suggestions and assistance.

1. **Open VS Code Insiders**

2. **Install GitHub Copilot Extension:**
   - Press `Ctrl+Shift+X` to open Extensions
   - Search for "GitHub Copilot"
   - Click **Install** on the official GitHub Copilot extension by GitHub

3. **Sign in to GitHub:**
   - After installation, VS Code will prompt you to sign in
   - Click **Sign in to GitHub** in the notification
   - This will open your browser to authenticate with GitHub
   - Authorize VS Code Insiders to access your GitHub account

4. **Verify Copilot is Active:**
   - Open any code file (`.js`, `.py`, `.md`, etc.)
   - Start typing code - you should see grayed-out suggestions from Copilot
   - Press `Tab` to accept suggestions or `Esc` to dismiss them

5. **Configure Copilot Settings (Optional):**
   - Press `Ctrl+,` to open Settings
   - Search for "copilot"
   - Adjust settings like:
     - `github.copilot.enable` - Enable/disable Copilot
     - `github.copilot.inlineSuggest.enable` - Enable inline suggestions

### 3. Verify Installation

Test that everything is working:

1. Open VS Code Insiders from command line:
   ```powershell
   code-insiders --version
   ```

2. Create a test file and verify Copilot suggestions appear when typing code

---

## Option A: Using WSL (Ubuntu) with GitHub

1. Ensure WSL is installed and Ubuntu is available:
   ```powershell
   wsl --list --verbose
   ```

2. Navigate to your working directory:
   ```bash
   cd /mnt/d
   mkdir agent-investment-platform
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

### 6. Test Connection
```powershell
ssh -T git@github.com
```
Expected output:
```
Hi eightbitreaper! You've successfully authenticated, but GitHub does not provide shell access.
```

### 7. Update Remote in Repo
In your project folder (`D:\agent-investment-platform`):
```powershell
cd D: gent-investment-platform
git remote -v
# if needed:
git remote set-url origin git@github.com:eightbitreaper/agent-investment-platform.git
```

### 8. Push to GitHub
```powershell
git pull --tags origin main
git push
```

---

## Summary

- Use **Option A (WSL)** if you want a Linux-based workflow (with Docker, Linux packages, etc.).  
- Use **Option B (Windows)** if you want a pure Windows-native workflow with VS Code Insiders.

Both paths ensure that contributors can authenticate with GitHub and push/pull successfully.
