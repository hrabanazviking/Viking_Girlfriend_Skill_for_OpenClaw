---
name: trello
description: Manage Trello boards, lists, and cards via the Trello REST API.
always: false
script: trello
requirements: {"env":["TRELLO_API_KEY","TRELLO_TOKEN"]}
metadata: {"clawlite":{"emoji":"📋","auth":{"requiredEnv":["TRELLO_API_KEY","TRELLO_TOKEN"]}}}
---

# Trello

Use this skill when the user wants to manage Trello boards, lists, or cards.

## Auth

Set `TRELLO_API_KEY` and `TRELLO_TOKEN` (from https://trello.com/power-ups/admin).

```bash
BASE="https://api.trello.com/1"
AUTH="key=$TRELLO_API_KEY&token=$TRELLO_TOKEN"
```

## Boards

```bash
# List all boards for the authenticated user
curl -s "$BASE/members/me/boards?$AUTH&fields=id,name,url"

# Get a board's lists
curl -s "$BASE/boards/{board_id}/lists?$AUTH"

# Get all cards on a board
curl -s "$BASE/boards/{board_id}/cards?$AUTH"
```

## Lists

```bash
# Get cards in a list
curl -s "$BASE/lists/{list_id}/cards?$AUTH"

# Create a list on a board
curl -s -X POST "$BASE/lists?$AUTH" \
  -d "name=New List&idBoard={board_id}&pos=bottom"
```

## Cards

```bash
# Create a card
curl -s -X POST "$BASE/cards?$AUTH" \
  -d "name=Card Title&idList={list_id}&desc=Description"

# Move a card to another list
curl -s -X PUT "$BASE/cards/{card_id}?$AUTH" \
  -d "idList={target_list_id}"

# Add a comment
curl -s -X POST "$BASE/cards/{card_id}/actions/comments?$AUTH" \
  -d "text=Comment text"

# Archive (close) a card
curl -s -X PUT "$BASE/cards/{card_id}?$AUTH" -d "closed=true"

# Add a label
curl -s -X POST "$BASE/cards/{card_id}/labels?$AUTH" \
  -d "color=red&name=Priority"
```

## Safety notes

- Archiving a card is reversible; deleting is not — prefer archive.
- Always resolve board/list IDs before card operations.
