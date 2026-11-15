# Changes for upstream

Hi! The Asciiverse build of Shamogu carries one small change, written
so it can be taken or left as it is. PATCHES.md lists it with the
packaging files.

## Save, config, replays and logs in the XDG state folder (`io.go`)

`DataDir()` used `$XDG_DATA_HOME/shamogu`. The XDG base directory spec
has since added `$XDG_STATE_HOME` (default `~/.local/state`) for state
that should persist between runs but is not important data to carry
between machines: saves, history, logs. `DataDir()` now uses
`$XDG_STATE_HOME/shamogu` outside Windows, and when that folder does
not exist yet but `$XDG_DATA_HOME/shamogu` does, it renames the old one
across first, so existing saves, settings and replays come along.
Windows still uses `%LOCALAPPDATA%\shamogu`. A small `xdgDir()` helper
reads an XDG variable with its default.

## Licence note

The repository's `LICENSE` is the ISC-style notice, while the itch.io page
says BSD 2-clause for the code and CC BY 4.0 for the assets. We list
ISC, from the file. If the itch page is the one you mean, a line in the
README would settle it for packagers.

Thank you for Shamogu!
