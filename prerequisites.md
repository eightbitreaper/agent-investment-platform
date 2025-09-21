# Setup Guide: WSL + GitHub Integration

This document explains how to set up a Windows + WSL2 development environment with GitHub so you can push code directly from WSL to GitHub.  
These steps were validated on a Windows 11 machine with Ubuntu under WSL2.

---

## 1. Install WSL & Ubuntu
If you don’t already have Ubuntu installed:
```powershell
wsl --install -d Ubuntu
```
> If Ubuntu already exists, just launch it:  
> ```powershell
> wsl -d Ubuntu
> ```

---

## 2. Verify WSL version
```powershell
wsl --list --verbose
```
Confirm your distro (Ubuntu) is using **VERSION 2**. If not:
```powershell
wsl --set-version Ubuntu 2
```

---

## 3. Update packages
Inside Ubuntu (WSL shell):
```bash
sudo apt-get update && sudo apt-get upgrade -y
```

---

## 4. Install Git & GitHub CLI
```bash
sudo apt-get install -y git gh
```

---

## 5. Configure Git identity
Set your GitHub username & email:
```bash
git config --global user.name "YOUR_GITHUB_USERNAME"
git config --global user.email "your_email@example.com"
```
Check:
```bash
git config --list
```

---

## 6. Generate SSH key
```bash
mkdir -p ~/.ssh && chmod 700 ~/.ssh
ssh-keygen -t ed25519 -C "your_email@example.com" -f ~/.ssh/id_ed25519
```
Press **Enter** for no passphrase (or set one if you prefer).

Start agent & add key:
```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

---

## 7. Add SSH key to GitHub
Copy the public key:
```bash
cat ~/.ssh/id_ed25519.pub
```

On GitHub:
- Go to **Settings → SSH and GPG Keys → New SSH key**
- Title: `wsl-ed25519`
- Key: paste the output
- Save

Test connection:
```bash
ssh -T git@github.com
```
Expected output:
```
Hi <username>! You've successfully authenticated, but GitHub does not provide shell access.
```

---

## 8. Authenticate GitHub CLI
```bash
gh auth login
```
- Account: **GitHub.com**  
- Protocol: **SSH**  
- Key: select your `id_ed25519.pub`  
- Authentication: **Login with a web browser** (copy/paste the code into your browser)

Check:
```bash
gh auth status
```

---

## 9. Create project folder
Example under `D:`:
```bash
cd /mnt/d
mkdir agent-investment-platform
cd agent-investment-platform
```

Initialize Git:
```bash
git init
git branch -m main
```

---

## 10. Create repository on GitHub
From inside your folder:
```bash
gh repo create agent-investment-platform --private --source=. --remote=origin
```

If the remote fails to add, fix it manually:
```bash
git remote add origin git@github.com:YOUR_GITHUB_USERNAME/agent-investment-platform.git
```

---

## 11. First commit & push
```bash
touch README.md
git add .
git commit -m "chore: initial scaffold"
git push -u origin main
```

Check your repository at:
```
https://github.com/YOUR_GITHUB_USERNAME/agent-investment-platform
```

---

## ✅ You are ready!
At this point:
- WSL is configured with Git & GitHub access
- Repo is live on GitHub
- SSH authentication works
