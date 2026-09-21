"""Run: python3 test_bridge.py"""
import importlib.machinery, importlib.util, pathlib, sys, tempfile, os

spec = importlib.util.spec_from_loader("bridge", importlib.machinery.SourceFileLoader("bridge", "bridge"))
b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)

# --from overrides whoami, and a known Claude handle routes to the inbox file
b.INBOX = pathlib.Path(tempfile.mkdtemp())
b.CURSOR_DIR = b.INBOX / "cursor"
b.claude_peers = lambda: {"fakepeer": {"pid": 1, "cwd": "/", "status": "idle"}}
b.send("fakepeer", "hi there", frm="builder")
assert (b.INBOX / "fakepeer.inbox").read_text() == "[builder] hi there\n"

# unknown handle must NOT touch the inbox (it goes to codex queue instead)
b.subprocess.run = lambda *a, **k: type("R", (), {"stdout": "queued", "stderr": "", "returncode": 0})()
try:
    b.send("some-uuid", "x", frm="builder")
except SystemExit:
    pass
assert not (b.INBOX / "some-uuid.inbox").exists()

# no identity and no --from must refuse, not tag [unknown]
_whoami = b.whoami
b.whoami = lambda: (None, None)
try:
    b.send("fakepeer", "anon"); raise AssertionError("should have refused")
except SystemExit as e:
    assert "--from" in str(e)
assert "anon" not in (b.INBOX / "fakepeer.inbox").read_text()
b.whoami = _whoami

# CODEX_THREAD_ID resolves to the thread name, falling back to the raw id
b._thread_names = lambda: {"abc-123": "builder"}
os.environ["CODEX_THREAD_ID"] = "abc-123"; assert b.whoami() == ("codex", "builder")
os.environ["CODEX_THREAD_ID"] = "zzz";     assert b.whoami() == ("codex", "zzz")
del os.environ["CODEX_THREAD_ID"]

# CURSOR_CONVERSATION_ID maps to a claimed handle, falling back to the raw id
_cursor_peers = b.cursor_peers
b.cursor_peers = lambda: {"cur-x": {"id": "conv-1", "cwd": "/"}}
os.environ["CURSOR_CONVERSATION_ID"] = "conv-1"; assert b.whoami() == ("cursor", "cur-x")
os.environ["CURSOR_CONVERSATION_ID"] = "conv-9"; assert b.whoami() == ("cursor", "conv-9")
del os.environ["CURSOR_CONVERSATION_ID"]

# a claimed Cursor handle routes to the inbox, not codex queue
b.send("cur-x", "hello", frm="builder")
assert (b.INBOX / "cur-x.inbox").read_text() == "[builder] hello\n"

# claim writes a presence file and an empty inbox
b.cursor_peers = _cursor_peers
os.environ["CURSOR_CONVERSATION_ID"] = "conv-2"
b.claim("cur-y")
assert (b.CURSOR_DIR / "conv-2.json").exists()
assert b.whoami() == ("cursor", "cur-y")
assert (b.INBOX / "cur-y.inbox").exists()
del os.environ["CURSOR_CONVERSATION_ID"]

print("ok")
