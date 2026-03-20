---
name: notion
description: Read, search, create, and update Notion pages and databases via the Notion API.
always: false
script: notion
requirements: {"env":["NOTION_API_KEY"]}
metadata: {"clawlite":{"emoji":"📝","auth":{"requiredEnv":["NOTION_API_KEY"]}}}
---

# Notion

Use this skill when the user wants to interact with Notion pages, databases, or workspaces.

## Auth

Set `NOTION_API_KEY` (Integration token from https://www.notion.so/my-integrations).

## Base URL

```
https://api.notion.com/v1
Headers: Authorization: Bearer $NOTION_API_KEY
         Notion-Version: 2022-06-28
         Content-Type: application/json
```

## Key endpoints

```
POST /search                          # search pages/databases by query
GET  /pages/{page_id}                 # read a page
POST /pages                           # create a page
PATCH /pages/{page_id}                # update page properties
GET  /databases/{database_id}/query   # query a database
POST /databases/{database_id}/query   # filter/sort database rows
GET  /blocks/{block_id}/children      # read page content blocks
PATCH /blocks/{block_id}              # update a block
POST /blocks/{block_id}/children      # append blocks to a page
```

## Search example

```bash
curl -s -X POST https://api.notion.com/v1/search \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json" \
  -d '{"query":"meeting notes","filter":{"value":"page","property":"object"}}'
```

## Safety notes

- Never delete pages without explicit user confirmation.
- Prefer PATCH (update) over recreating pages.
