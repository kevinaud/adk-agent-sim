#! /bin/bash

bash .devcontainer/setup-env.sh

# Playwright browsers are pre-installed in the container image
# No need to run playwright install here

if [ -s /tmp/.gh_token_file ]; then
  cat /tmp/.gh_token_file | gh auth login --with-token
else
  echo 'WARN: No GitHub token found. Skipping auto-login.'
fi