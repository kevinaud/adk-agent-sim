#!/usr/bin/env bash

set -e

# Parse command line arguments
JSON_MODE=false
OUTPUT_NAME=""
ARGS=()

while [[ $# -gt 0 ]]; do
    case "$1" in
        --json) 
            JSON_MODE=true
            shift
            ;;
        --output|-o)
            OUTPUT_NAME="$2"
            shift 2
            ;;
        --help|-h) 
            echo "Usage: $0 [--json] [--output NAME]"
            echo "  --json           Output results in JSON format"
            echo "  --output, -o     Override output filename (default: plan.md)"
            echo "                   Example: --output plan-fixes.md"
            echo "  --help           Show this help message"
            exit 0 
            ;;
        *) 
            ARGS+=("$1")
            shift
            ;;
    esac
done

# Get script directory and load common functions
SCRIPT_DIR="$(CDPATH="" cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

# Get all paths and variables from common functions
eval $(get_feature_paths)

# Apply output name override if provided
if [[ -n "$OUTPUT_NAME" ]]; then
    IMPL_PLAN="$FEATURE_DIR/$OUTPUT_NAME"
fi

# Check if we're on a proper feature branch (only for git repos)
check_feature_branch "$CURRENT_BRANCH" "$HAS_GIT" || exit 1

# Ensure the feature directory exists
mkdir -p "$FEATURE_DIR"

# Copy plan template if it exists and destination doesn't
TEMPLATE="$REPO_ROOT/.specify/templates/plan-template.md"
if [[ -f "$IMPL_PLAN" ]]; then
    echo "Plan file already exists at $IMPL_PLAN (skipping template copy)"
elif [[ -f "$TEMPLATE" ]]; then
    cp "$TEMPLATE" "$IMPL_PLAN"
    echo "Copied plan template to $IMPL_PLAN"
else
    echo "Warning: Plan template not found at $TEMPLATE"
    # Create a basic plan file if template doesn't exist
    touch "$IMPL_PLAN"
fi

# Output results
if $JSON_MODE; then
    printf '{"FEATURE_SPEC":"%s","IMPL_PLAN":"%s","SPECS_DIR":"%s","BRANCH":"%s","HAS_GIT":"%s"}\n' \
        "$FEATURE_SPEC" "$IMPL_PLAN" "$FEATURE_DIR" "$CURRENT_BRANCH" "$HAS_GIT"
else
    echo "FEATURE_SPEC: $FEATURE_SPEC"
    echo "IMPL_PLAN: $IMPL_PLAN" 
    echo "SPECS_DIR: $FEATURE_DIR"
    echo "BRANCH: $CURRENT_BRANCH"
    echo "HAS_GIT: $HAS_GIT"
fi

