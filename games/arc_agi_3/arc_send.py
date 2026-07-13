"""Send one or more commands to the running arc_session and print the resulting state.
Usage: arc_send.py "1"   or   "1;1;3"  (semicolon-separated)  or  "6 32 40"."""
import sys, time, pathlib, re
HERE = pathlib.Path(__file__).parent
try:
    RUN = HERE / (HERE / ".active_run").read_text().strip()
except FileNotFoundError:
    sys.exit("no .active_run pointer — start arc_session.py first")
CMD = RUN / "arc_cmd.txt"
STATE = RUN / "arc_state.txt"

def cur_seq():
    try:
        m = re.search(r"seq=(\d+)", STATE.read_text())
        return int(m.group(1)) if m else -1
    except FileNotFoundError:
        return -1

cmds = [c.strip() for c in sys.argv[1].split(";") if c.strip()]
start = cur_seq()
target = start + len(cmds)
with open(CMD, "a") as f:
    for c in cmds:
        f.write(c + "\n")

deadline = time.time() + 30
while time.time() < deadline:
    if cur_seq() >= target:
        break
    time.sleep(0.2)
print(STATE.read_text())
