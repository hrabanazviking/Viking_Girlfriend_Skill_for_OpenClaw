---
name: obsidian
description: Read, write, and search local Obsidian vault markdown files via the filesystem.
always: false
script: obsidian
requirements: {"env":["OBSIDIAN_VAULT"]}
metadata: {"clawlite":{"emoji":"💎","requires":{"bins":["find","grep"]}}}
---

# Obsidian

Use this skill when the user wants to interact with their local Obsidian vault (markdown files).

## Vault location

Check `OBSIDIAN_VAULT` env var or ask the user. Default paths:
- macOS: `~/Documents/Obsidian` or `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/`
- Linux: `~/obsidian` or `~/Documents/obsidian`

## Operations

### Search notes
```bash
grep -r "query" "$OBSIDIAN_VAULT" --include="*.md" -l
grep -r "query" "$OBSIDIAN_VAULT" --include="*.md" -n
```

### Read a note
```bash
cat "$OBSIDIAN_VAULT/path/to/note.md"
```

### List all notes
```bash
find "$OBSIDIAN_VAULT" -name "*.md" | sort
```

### Create or append a note
```bash
# Create new
cat > "$OBSIDIAN_VAULT/folder/new-note.md" <<EOF
---
created: $(date -I)
tags: [tag1, tag2]
---

# Title

Content here.
EOF

# Append
echo "\n## New Section\n\ncontent" >> "$OBSIDIAN_VAULT/existing-note.md"
```

### Search by frontmatter tag
```bash
grep -r "tags:.*mytag" "$OBSIDIAN_VAULT" --include="*.md" -l
```

## Safety notes

- Always resolve `$OBSIDIAN_VAULT` before operating.
- Do not delete notes without explicit user confirmation.
- Preserve existing frontmatter when updating files.
