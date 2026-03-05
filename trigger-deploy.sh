#!/usr/bin/env bash
# Triggers the manga-deploy GitHub Actions workflow via API.
# Usage: ./trigger-deploy.sh <github-pat>
# Get a PAT at: https://github.com/settings/tokens (needs repo + workflow scopes)

set -euo pipefail

REPO="aaas24/code_library"
WORKFLOW="manga-deploy.yml"
BRANCH="main"

TOKEN="${1:-${GITHUB_TOKEN:-}}"

if [[ -z "$TOKEN" ]]; then
  echo "Error: provide a GitHub PAT as first argument or set GITHUB_TOKEN env var."
  echo "  Usage: $0 ghp_yourtoken"
  echo "  Or:    GITHUB_TOKEN=ghp_yourtoken $0"
  exit 1
fi

echo "Triggering workflow '$WORKFLOW' on branch '$BRANCH'..."

HTTP_STATUS=$(curl -s -o /tmp/gh_trigger_response.json -w "%{http_code}" \
  -X POST \
  -H "Authorization: token $TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  "https://api.github.com/repos/${REPO}/actions/workflows/${WORKFLOW}/dispatches" \
  -d "{\"ref\":\"${BRANCH}\"}")

if [[ "$HTTP_STATUS" == "204" ]]; then
  echo "Success! Workflow triggered. Check progress at:"
  echo "  https://github.com/${REPO}/actions"
else
  echo "Failed (HTTP $HTTP_STATUS):"
  cat /tmp/gh_trigger_response.json
  exit 1
fi
