---
name: 1password
description: Retrieve secrets and vault items from 1Password using the op CLI with a service account token.
always: false
script: onepassword
metadata: {"clawlite":{"emoji":"🔑","requires":{"bins":["op"]},"auth":{"requiredEnv":["OP_SERVICE_ACCOUNT_TOKEN"]}}}
---

# 1Password

Use this skill when the user needs to retrieve secrets or credentials from 1Password.

## Auth

Set `OP_SERVICE_ACCOUNT_TOKEN` (create at https://developer.1password.com/docs/service-accounts/).

```bash
export OP_SERVICE_ACCOUNT_TOKEN="ops_..."
op whoami    # verify auth
```

## Read secrets

```bash
# Get a field from a vault item
op item get "AWS Production" --fields label=access_key_id
op item get "DB Password" --fields label=password --reveal

# Get as environment variable format
op item get "App Secrets" --format env

# Read a secret reference
op read "op://vault-name/item-name/field-name"
op read "op://Private/GitHub Token/credential"
```

## List and search

```bash
op item list                          # list all items
op item list --vault "Private"        # items in a vault
op item list --categories Login       # filter by category
op item get "item name" --format json # full item as JSON
op vault list                         # list all vaults
```

## Create/update items

```bash
op item create --category Login --title "New Item" \
  --vault Private username=user password=secret
op item edit "Item Name" password=newvalue
```

## Safety notes

- Never log or print secret values; pipe to env or use in-process only.
- Prefer `op read` over `op item get --reveal` to minimize exposure.
- Service account tokens grant broad vault access — scope minimally.
