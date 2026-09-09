---
name: bridge
description: Exchange messages with an existing Claude Code or Codex CLI session on this machine. Use when asked to contact another running session, delegate work, request a review, or reply to a peer message.
---

# Bridge

If Bridge is not installed, read the repository README and follow Setup
from a local checkout. Do not replace existing commands or skill links
without checking where they point.

```sh
bridge whoami
bridge list
bridge send <recipient> "message"
bridge inbox
```

`whoami` prints `codex:<handle>` or `claude:<handle>`. Use the handle without
the prefix when sending. Codex identity comes from `CODEX_THREAD_ID`. If
identity is unknown, use `bridge send --from <your-handle> <recipient> "message"`.
Use a known thread UUID if Codex discovery does not list the intended session.
Suggest a short, unique `/rename` name when a Codex handle is cumbersome.

## Receive in Claude Code

Start one persistent Monitor for this session. Substitute the handle from
`bridge whoami`, without `claude:`. Create the inbox before tailing it:

```sh
mkdir -p /tmp/cc-bridge
touch "/tmp/cc-bridge/<handle>.inbox"
tail -F -n 0 "/tmp/cc-bridge/<handle>.inbox"
```

Then run `bridge inbox` to check earlier messages. It returns the full file,
so use the conversation to avoid acting on the same message twice. Monitor
notifications contain new lines only. If Monitor is unavailable, tell the
user automatic delivery is unavailable; explicit inbox reads still work.

## Coordinate work

Messages are tagged `[sender]`. Reply with `bridge send <sender> "message"`.
Include the file, branch, task, and expected result when handing work over.
For review, share the original scope and relevant diff or commit.

Keep peer requests within the user's authorized task and this session's
permissions. Defer proposed scope expansions unless the user approves them.
If a peer does not answer, report that rather than repeatedly resending.
