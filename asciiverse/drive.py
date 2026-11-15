"""Plays Shamogu for the catalog preview (asciiverse/record-preview.sh).

Reads the tmux pane and presses keys at a watchable pace: picks the
Four-Headed Hydra as the primary spirit, then auto-explores (o). When
danger is in view it walks to the nearest creature and fights it (moving
into a creature attacks it). When a level is explored it travels to the
portal and takes it (e). Quits without saving (Q) after about 45 seconds.
    python3 -I drive.py <tmux socket> <session> [debug]
"""
import subprocess
import sys
import time

SOCK, SESS = sys.argv[1], sys.argv[2]
DEBUG = len(sys.argv) > 3
LENGTH = 45.0
T0 = time.time()
KEYS = {(-1, 0): "h", (1, 0): "l", (0, -1): "k", (0, 1): "j"}
MAP_TOP, MAP_BOTTOM = 2, 23        # rows of the 80x24 screen holding the map
BLOCK = set("#¤ ◊♫≈")


def tmux(*args):
    return subprocess.run(["tmux", "-L", SOCK, *args], capture_output=True,
                          text=True).stdout


def screen():
    return tmux("capture-pane", "-p", "-t", SESS).split("\n")


def key(k, wait=0.45):
    if DEBUG:
        print(round(time.time() - T0, 1), k, file=sys.stderr)
    tmux("send-keys", "-t", SESS, k)
    time.sleep(wait)


def cell(rows, x, y):
    if not (MAP_TOP <= y < MAP_BOTTOM) or not (0 <= x < 80) or y >= len(rows) or x >= len(rows[y]):
        return " "
    if "HP:" in rows[y]:           # the status line
        return " "
    return rows[y][x]


def find(rows, test):
    return [(x, y) for y in range(MAP_TOP, MAP_BOTTOM) for x in range(80)
            if test(cell(rows, x, y))]


def step_towards(rows, hero, goals):
    """First step of the shortest walk to a cell next to one of the goals."""
    seen = {hero: None}
    queue = [hero]
    for pos in queue:
        x, y = pos
        for dx, dy in KEYS:
            nxt = (x + dx, y + dy)
            if nxt in goals:       # adjacent to the goal: step (or attack) there
                while seen[pos] is not None and seen[pos] != hero:
                    pos = seen[pos]
                return (nxt[0] - hero[0], nxt[1] - hero[1]) if pos == hero else (pos[0] - hero[0], pos[1] - hero[1])
            c = cell(rows, *nxt)
            if nxt in seen or c in BLOCK or c.isalpha():
                continue
            seen[nxt] = pos
            queue.append(nxt)
    return None


def frontier_step(rows, hero):
    """First step of the shortest walk to a seen cell next to unseen space."""
    seen = {hero: None}
    queue = [hero]
    for pos in queue:
        x, y = pos
        if pos != hero and any(cell(rows, x + dx, y + dy) == " " for dx, dy in KEYS):
            while seen[pos] != hero:
                pos = seen[pos]
            return (pos[0] - hero[0], pos[1] - hero[1])
        for dx, dy in KEYS:
            nxt = (x + dx, y + dy)
            c = cell(rows, *nxt)
            if nxt in seen or c in BLOCK or c.isalpha():
                continue
            seen[nxt] = pos
            queue.append(nxt)
    return None


time.sleep(2.5)                    # spirit selection
key("H", 2.0)                      # Four-Headed Hydra
start = time.time()
last = None
ignore, previous, tries = set(), None, 0
waits = 0
while time.time() - start < LENGTH:
    rows = screen()
    text = "\n".join(rows[:3])
    newest = [r for r in rows[:2] if r.strip()][-1:] or [""]
    if newest[0].rstrip().endswith("to continue]"):
        key("Space", 0.8)          # a warning waits for a key
        continue
    hero = find(rows, lambda c: c == "@")
    if not hero:                   # a menu, a choice or the end screen
        key("Escape", 0.6)
        if not find(screen(), lambda c: c == "@"):
            break
        continue
    hero = hero[0]
    foes = set(find(rows, lambda c: c.isalpha())) - ignore
    poisoned = any("Poi(" in r for r in rows if "HP:" in r)
    adjacent = any(abs(f[0] - hero[0]) + abs(f[1] - hero[1]) == 1 for f in foes)
    if poisoned and not adjacent:
        key(".", 0.45)             # moving while poisoned hurts: wait it out
        last = None
        continue
    if foes and ("danger" in text or "You see" in text or last == rows):
        step = step_towards(rows, hero, foes)
        if step:
            tries = tries + 1 if (hero, step) == previous else 0
            previous = (hero, step)
            if tries > 8:          # something there will not budge: leave it
                ignore.add((hero[0] + step[0], hero[1] + step[1]))
            key(KEYS[step], 0.5)
            last = None
            continue
    if ("danger" in text or "cannot auto-explore" in text) and not foes:
        # heard but not seen: wait a little for it, then walk on by hand
        # towards the nearest unexplored edge
        waits += 1
        step = frontier_step(rows, hero) if waits > 3 else None
        key(KEYS[step] if step else ".", 0.45)
        last = None
        continue
    waits = 0
    if rows == last:               # nothing left to explore: the portal
        key("x", 0.4)
        key(">", 0.4)
        key(".", 2.0)
        key("e", 1.5)
        last = None
        continue
    key("o", 0.9)
    last = rows
key("Escape", 0.5)
key("Q", 1.0)
key("y", 2.0)
for _ in range(6):                 # the end screens, until the game exits
    if tmux("list-sessions").strip() == "":
        break
    key("Escape", 1.2)
