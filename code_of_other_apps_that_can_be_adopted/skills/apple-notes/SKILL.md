---
name: apple-notes
description: Create, read, and search Apple Notes on macOS using osascript AppleScript.
always: false
script: apple_notes
metadata: {"clawlite":{"emoji":"🍎","platform":"macos","requires":{"bins":["osascript"]}}}
---

# Apple Notes

Use this skill to interact with the Apple Notes app on macOS via AppleScript.

## Platform requirement

macOS only. Verify with:
```bash
uname -s   # must return Darwin
which osascript
```

## Create a note

```bash
osascript -e '
tell application "Notes"
  tell account "iCloud"
    make new note at folder "Notes" with properties {name:"Title", body:"Body text here"}
  end tell
end tell'
```

## Read a note by name

```bash
osascript -e '
tell application "Notes"
  set theNote to note "Title" of folder "Notes" of account "iCloud"
  return body of theNote
end tell'
```

## List all notes

```bash
osascript -e '
tell application "Notes"
  set noteNames to {}
  repeat with n in notes of folder "Notes" of account "iCloud"
    set end of noteNames to name of n
  end repeat
  return noteNames
end tell'
```

## Search notes (by name substring)

```bash
osascript -e '
tell application "Notes"
  set results to {}
  repeat with n in notes of folder "Notes" of account "iCloud"
    if name of n contains "search term" then
      set end of results to name of n
    end if
  end repeat
  return results
end tell'
```

## Update/append to a note

```bash
osascript -e '
tell application "Notes"
  set theNote to note "Title" of folder "Notes" of account "iCloud"
  set body of theNote to (body of theNote) & "<br>Appended content"
end tell'
```

## Safety notes

- Notes body is HTML; use `<br>` for line breaks.
- Specify account (iCloud vs On My Mac) to avoid ambiguity.
- Requires Accessibility/Automation permission for Terminal/agent process.
