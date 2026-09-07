#!/usr/bin/env bash
set -euo pipefail

rg -n -i --hidden \
  --glob '!.git/**' \
  --glob '!*.safetensors' \
  --glob '!*.gguf' \
  --glob '!scripts/check_secrets.sh' \
  '(ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|hf_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|BEGIN (RSA|OPENSSH|EC) PRIVATE KEY|password[[:space:]]*[:=].{8,}|access_token[[:space:]]*[:=].{8,})' \
  . && {
    echo "Potential secret found" >&2
    exit 1
  }

echo "No matching secret patterns found."
