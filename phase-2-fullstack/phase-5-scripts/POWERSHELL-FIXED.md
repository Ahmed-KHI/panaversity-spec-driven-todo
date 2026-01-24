# PowerShell Script Fixed ✅

## Issue
The `deploy-phase5-complete.ps1` script had PowerShell syntax errors related to special characters in strings.

## Errors Fixed

### 1. Special Character Escaping
**Problem:** The `<` character in `<pod-name>` was being interpreted as PowerShell's redirection operator.

**Solution:** Changed `<pod-name>` to `[pod-name]` in the output message.

### 2. Quote Consistency  
**Problem:** Inconsistent quote usage causing terminator issues.

**Solution:** Used single quotes for literal strings that don't need variable expansion.

## Script Status: ✅ READY TO RUN

The script is now syntactically correct and ready for deployment.

## How to Run

### Prerequisites
Ensure you have:
- Minikube
- kubectl  
- Helm
- Dapr CLI
- Docker Desktop (running)

### Execute Script

```powershell
cd "I:\hackathon II-full-stack web application\phase-2-fullstack\phase-5-scripts"
.\deploy-phase5-complete.ps1
```

### What It Does
1. ✅ Checks all prerequisites
2. ✅ Starts Minikube (4 CPUs, 8GB RAM)
3. ✅ Initializes Dapr on Kubernetes
4. ✅ Installs Strimzi Kafka operator
5. ✅ Creates namespaces (todo-app, kafka)
6. ✅ Deploys Kafka cluster with topics
7. ✅ Deploys PostgreSQL database
8. ✅ Applies secrets
9. ✅ Deploys Dapr components
10. ✅ Builds Docker images
11. ✅ Deploys application
12. ✅ Shows access instructions

### Expected Time
10-15 minutes for complete deployment

### Troubleshooting
If you encounter issues, check:
- Docker Desktop is running
- You have 4 CPU cores and 8GB RAM available
- Port 8080 is not in use
- No other Minikube cluster is running

## Alternative: Use Bash Script (Linux/Mac)

If you're on Linux/Mac or WSL, use the bash version:

```bash
cd phase-2-fullstack/phase-5-scripts
chmod +x deploy-phase5-complete.sh
./deploy-phase5-complete.sh
```

---

**Status:** ✅ Script Syntax FIXED and READY  
**Date:** January 23, 2026
