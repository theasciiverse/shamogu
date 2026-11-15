#!/bin/sh
# Records the 100x30 catalog preview, asciiverse/shamogu.cast
# (hub/RECORDING.md): choosing the Four-Headed Hydra as primary spirit,
# then the guardian exploring the dungeon and fighting its corrupted
# beasts, played by asciiverse/drive.py, and quitting at the end. The
# game draws its 80x24 screen at the top left. asciinema records a tmux pane (own socket, no
# status line, no user config) that drive.py reads and plays into.
# Needs asciinema 3 and tmux.
#   asciiverse/record-preview.sh ./shamogu
set -eu
binary=$(cd "$(dirname "$1")" && pwd)/$(basename "$1")
here=$(cd "$(dirname "$0")" && pwd)
out=$here/shamogu.cast
home=$(mktemp -d)
trap 'tmux -L avrec kill-server 2>/dev/null; rm -rf "$home"' EXIT
mkdir "$home/bin" && cp "$binary" "$home/bin/shamogu"
cd "$home"  # nothing in the recording names a local path
export HOME="$home" XDG_STATE_HOME="$home/state" XDG_DATA_HOME="$home/data" \
  PATH="$home/bin:$PATH" USER=player LOGNAME=player \
  TERM=xterm-256color COLORTERM=truecolor LANG=C.UTF-8
tmux -L avrec -f /dev/null new-session -d -s rec -x 100 -y 30 "shamogu" \; set -g status off
python3 -I "$here/drive.py" avrec rec &
drive=$!
asciinema rec --headless --overwrite -q \
  --window-size 100x30 --idle-time-limit 2 \
  --capture-env "TERM,COLORTERM,LANG" --title "Shamogu" \
  --command "tmux -L avrec attach -t rec" "$out"
wait "$drive"
