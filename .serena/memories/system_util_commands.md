# System Utility Commands (Darwin)

Basics
- List files: `ls -la`
- Change dir: `cd <path>`
- Copy/move: `cp -R src dst`, `mv old new`
- Remove: `rm file`, `rm -rf dir`

Search
- Preferred fast search: `rg "pattern"` (ripgrep), list files: `rg --files`
- Fallback (BSD grep): `grep -R "pattern" .`
- Find files: `find . -name "*.py"`

Viewing/Editing
- Head/tail: `sed -n '1,200p' file`, `tail -n 100 file`
- In-place edit (BSD sed requires suffix): `sed -i '' -e 's/old/new/g' file`

System Differences (macOS/BSD)
- `stat`: use `stat -f "%z %N" file` (not GNU `-c`)
- `md5`: use `md5 file` (GNU uses `md5sum`)

Git Essentials
- Status/diff: `git status`, `git diff`
- Log/blame: `git log --oneline --decorate --graph`, `git blame path`
- Focused log: `git log -p -1 -- path`

Python
- Use `python3` explicitly when needed: `python3 -m pytest -v`
- Virtualenvs via `uv`, `venv`, or `pipx` if preferred.

Tox/Pytest
- `tox`, `tox -e py311`, `pytest -v`
