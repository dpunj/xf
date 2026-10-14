#!/usr/bin/env bash
set -euo pipefail

# Print the plaintext of the Apple Notes note named "XF" (the raw training log).
note_name="${1:-XF}"

osascript - "$note_name" <<'APPLESCRIPT'
on run argv
  set noteName to item 1 of argv
  tell application "Notes"
    set matches to (notes of default account whose name is noteName)
    if (count of matches) is 0 then error "No Apple Note named '" & noteName & "'. Create it first."
    return plaintext of item 1 of matches
  end tell
end run
APPLESCRIPT
