#! /bin/bash

bash .devcontainer/setup-env.sh

uv run playwright install --with-deps

if [ -s /tmp/.gh_token_file ]; then
  cat /tmp/.gh_token_file | gh auth login --with-token
else
  echo 'WARN: No GitHub token found. Skipping auto-login.'
fi