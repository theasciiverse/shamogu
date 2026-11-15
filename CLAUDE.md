# Shamogu (Asciiverse packaging)

anaseto's Shamanic Mountain Guardian, Shamogu (Go, gruid, ISC per the
repository's LICENSE), packaged for the Asciiverse catalog (id `shamogu`,
kind `game`, genre `roguelike`). Not our code: the game stays as its
author made it; list every change in PATCHES.md and keep each one
offerable upstream (UPSTREAM.md).

- `upstream` is codeberg.org/anaseto/shamogu (branch `master`); ours is
  branch `asciiverse` (from the `v1.6.0` tag), `origin`
  github.com/theasciiverse/shamogu (private).
- Build: `CGO_ENABLED=0 go build -trimpath .` (terminal version, tcell;
  never `-tags sdl`). Go from go.mod, 1.24+. Vaults in `data/` are embedded.
- Release: tag `v<upstream version>-av.<n>` (first `v1.6.0-av.1`) and push
  it; `.github/workflows/asciiverse-release.yml` cross-builds Linux, macOS
  and Windows on one runner.
- Save, config, replays and `logs.txt` live in `$XDG_STATE_HOME/shamogu`.
  Tests and scripted runs always set scratch `HOME`, `XDG_STATE_HOME` and
  `XDG_DATA_HOME` in the same command (the old data folder is moved on
  first use), under `systemd-run --user --scope -p MemoryMax=4G`.
- The screen is 80x24, drawn at the top left of bigger terminals.
- Preview: `asciiverse/record-preview.sh ./shamogu`.
- Catalog drafts: `asciiverse/shamogu.toml` and `.md`; hub pushes are
  done from beast.
