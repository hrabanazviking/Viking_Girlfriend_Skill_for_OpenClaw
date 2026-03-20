---
name: linear
description: Manage Linear issues, projects, and cycles via the Linear GraphQL API.
always: false
script: linear
requirements: {"env":["LINEAR_API_KEY"]}
metadata: {"clawlite":{"emoji":"📐","auth":{"requiredEnv":["LINEAR_API_KEY"]}}}
---

# Linear

Use this skill when the user wants to create, update, search, or triage Linear issues and projects.

## Auth

Set `LINEAR_API_KEY` (from https://linear.app/settings/api).

```bash
ENDPOINT="https://api.linear.app/graphql"
HEADERS='-H "Authorization: $LINEAR_API_KEY" -H "Content-Type: application/json"'
```

## Search issues

```graphql
query {
  issues(filter: { state: { name: { eq: "In Progress" } } }, first: 20) {
    nodes { id identifier title priority state { name } assignee { name } }
  }
}
```

```bash
curl -s -X POST "$ENDPOINT" \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query":"{ issues(first:20){nodes{id identifier title state{name}}} }"}'
```

## Create an issue

```graphql
mutation {
  issueCreate(input: {
    title: "Fix login bug"
    description: "Steps to reproduce..."
    teamId: "TEAM_ID"
    priority: 2
  }) {
    issue { id identifier url }
  }
}
```

## Update issue state

```graphql
mutation {
  issueUpdate(id: "ISSUE_ID", input: { stateId: "STATE_ID" }) {
    issue { id state { name } }
  }
}
```

## Get teams and states

```graphql
query { teams { nodes { id name states { nodes { id name } } } } }
```

## Safety notes

- Always retrieve `teamId` and `stateId` before mutations.
- Priority values: 0=No priority, 1=Urgent, 2=High, 3=Medium, 4=Low.
