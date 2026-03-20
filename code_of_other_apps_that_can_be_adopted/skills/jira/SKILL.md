---
name: jira
description: Create, read, transition, and comment on Jira issues via the Jira REST API v3.
always: false
script: jira
requirements: {"env":["JIRA_BASE_URL","JIRA_EMAIL","JIRA_API_TOKEN"]}
metadata: {"clawlite":{"emoji":"🎯","auth":{"requiredEnv":["JIRA_BASE_URL","JIRA_EMAIL","JIRA_API_TOKEN"]}}}
---

# Jira

Use this skill when the user wants to manage Jira issues, transitions, or comments.

## Auth

Set:
- `JIRA_BASE_URL` — e.g. `https://yourorg.atlassian.net`
- `JIRA_EMAIL` — Atlassian account email
- `JIRA_API_TOKEN` — from https://id.atlassian.com/manage-profile/security/api-tokens

```bash
AUTH=$(echo -n "$JIRA_EMAIL:$JIRA_API_TOKEN" | base64)
BASE="$JIRA_BASE_URL/rest/api/3"
```

## Issues

```bash
# Get an issue
curl -s -H "Authorization: Basic $AUTH" -H "Accept: application/json" \
  "$BASE/issue/PROJ-123"

# Search with JQL
curl -s -H "Authorization: Basic $AUTH" -H "Accept: application/json" \
  "$BASE/search?jql=project=PROJ+AND+status='In Progress'&maxResults=20"

# Create an issue
curl -s -X POST -H "Authorization: Basic $AUTH" \
  -H "Content-Type: application/json" -H "Accept: application/json" \
  "$BASE/issue" \
  -d '{"fields":{"project":{"key":"PROJ"},"summary":"Issue title","issuetype":{"name":"Bug"},"description":{"type":"doc","version":1,"content":[{"type":"paragraph","content":[{"type":"text","text":"Description"}]}]}}}'
```

## Transitions

```bash
# Get available transitions
curl -s -H "Authorization: Basic $AUTH" "$BASE/issue/PROJ-123/transitions"

# Perform a transition (e.g. move to Done)
curl -s -X POST -H "Authorization: Basic $AUTH" \
  -H "Content-Type: application/json" \
  "$BASE/issue/PROJ-123/transitions" \
  -d '{"transition":{"id":"31"}}'
```

## Comments

```bash
# Add a comment
curl -s -X POST -H "Authorization: Basic $AUTH" \
  -H "Content-Type: application/json" \
  "$BASE/issue/PROJ-123/comment" \
  -d '{"body":{"type":"doc","version":1,"content":[{"type":"paragraph","content":[{"type":"text","text":"Comment text"}]}]}}'
```

## Safety notes

- Descriptions and comments use Atlassian Document Format (ADF), not plain text.
- Fetch transitions before calling transition endpoint — IDs differ per project.
- Never delete issues; use "Won't Do" or "Cancelled" transitions instead.
