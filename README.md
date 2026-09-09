# Bridge

Let Claude Code and Codex talk to each other.

Plan in Codex. Hand work to Claude. Get questions and results back in the
same session, without copying messages between windows.

## Try it with your agent

Copy this into Claude Code or Codex:

```text
Read https://github.com/ishu86/bridge and follow its SKILL.md to set up messaging between my running Claude Code and Codex sessions.
```

## Setup

From a local checkout, run:

```sh
mkdir -p ~/.local/bin ~/.claude/skills ~/.codex/skills
ln -s "$PWD/bridge" ~/.local/bin/bridge
ln -s "$PWD" ~/.claude/skills/bridge
ln -s "$PWD" ~/.codex/skills/bridge
```

Keep `~/.local/bin` on your PATH. If a link already exists, check its target
before changing it.

In Claude, ask: **"Use the bridge skill and start watching my inbox."**
In Codex, ask: **"Use the bridge skill. Ask <Claude handle> to implement
<task>, then review its changes."** Run `bridge list` to find the handles.

## Commands

```sh
bridge whoami
bridge list
bridge send worker "Implement the retry logic in src/client.py. Reply with the diff and test results."
bridge send planner "Ready for review. The retry tests pass."
bridge inbox
```

`whoami` prints `codex:planner` or `claude:worker`. Use the name after the
colon when sending. Outside an agent session, supply your label with
`bridge send --from planner worker "message"`.

Each session keeps its own context and permissions. Bridge does not manage
worktrees or merge changes. Give simultaneous workers separate worktrees
or separate files.

## How it works

Codex receives messages through `codex queue`. Claude receives them through
a persistent Monitor tailing `/tmp/cc-bridge/<handle>.inbox`.

Codex identifies itself with `CODEX_THREAD_ID`. Claude uses its process and
session registry. The script uses Python's standard library.

## Requirements and limits

- Tested live on macOS with Codex CLI 0.153.4 and Claude Code 2.1.263.
  Requires Python 3 and both CLIs. Linux is unverified; Windows is unsupported.
- Claude needs the [Monitor tool](https://code.claude.com/docs/en/tools-reference#monitor-tool).
  Its availability depends on version, provider, and settings. The watcher
  stops when the session ends.
- `inbox` prints all saved messages, including ones already read. Messages
  sent before the watcher starts need an explicit inbox read. Temporary files
  can disappear on reboot or system cleanup.
- Session discovery reads internal files and can break after CLI updates.
  Codex process-start matching can miss or misidentify resumed sessions;
  use a known thread UUID when the list is wrong.
- Use distinct handles across both agents. A discovered Claude handle takes
  precedence. Sender labels are not authenticated.
- A detected watcher does not prove receipt. Multi-line messages become
  separate watcher events. This tool is for one user on one machine.

Only Claude Code and Codex are supported. Another agent would need its own
session discovery, identity, and live-message delivery integration.

## Development

```sh
python3 test_bridge.py
```

MIT licensed. See [LICENSE](LICENSE).
