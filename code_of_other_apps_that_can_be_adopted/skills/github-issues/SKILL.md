---
name: github-issues
description: List, create, close, comment on, and triage GitHub issues and pull requests via the gh CLI.
always: false
script: gh_issues
metadata: {"clawlite":{"emoji":"🐙","requires":{"bins":["gh","git"]},"auth":{"optionalEnv":["GH_TOKEN"]}}}
---

# GitHub Issues

Use this skill for GitHub issue and PR management using the `gh` CLI.

## Auth

```bash
gh auth status        # verify active session
gh auth login         # interactive login
# or set GH_TOKEN env var for headless operation
```

## Issues

```bash
gh issue list --repo owner/repo --state open --limit 20
gh issue list --repo owner/repo --label bug --assignee @me
gh issue view 123 --repo owner/repo
gh issue create --repo owner/repo --title "Title" --body "Body" --label bug
gh issue close 123 --repo owner/repo
gh issue comment 123 --repo owner/repo --body "comment text"
gh issue edit 123 --repo owner/repo --add-label "priority:high"
```

## Pull Requests

```bash
gh pr list --repo owner/repo --state open
gh pr view 456 --repo owner/repo
gh pr create --title "Fix bug" --body "Fixes #123" --base main
gh pr merge 456 --squash --repo owner/repo
gh pr review 456 --approve --body "LGTM"
```

## Search

```bash
gh issue list --search "is:issue is:open label:bug" --repo owner/repo
gh pr list --search "is:pr is:open review-requested:@me"
```

## Safety notes

- Require explicit approval before closing or merging.
- Never force-push or rewrite history without explicit user instruction.
