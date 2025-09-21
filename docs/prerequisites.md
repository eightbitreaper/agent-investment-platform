# Prerequisites

This document explains how to set up the environment for contributing to the **Agent Investment Platform** project.  
It covers both **WSL-based setup** and **Windows-native GitHub setup**.

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
