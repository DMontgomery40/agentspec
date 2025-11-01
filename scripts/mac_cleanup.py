#!/usr/bin/env python3
import os
import sys
import shutil
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Tuple


def print_agentspec():
    print("[AGENTSPEC] Reading spec for mac_cleanup.main")
    print("[AGENTSPEC] What: Clean macOS user caches, Xcode artifacts, stale logs, and common package manager caches without touching user data or system files.")
    print("[AGENTSPEC] Deps: brew, npm, yarn, pnpm, pip, conda, qlmanage, xcrun (best-effort, optional)")
    print("[AGENTSPEC] Guardrails:")
    print("[AGENTSPEC]   - DO NOT delete user Documents/Downloads/Desktop/Photos or Application Support data")
    print("[AGENTSPEC]   - DO NOT use sudo or modify outside the user home directory")
    print("[AGENTSPEC]   - DO NOT prune Docker images/containers automatically")
    print("[AGENTSPEC]   - DO NOT delete browser profiles or empty Trash automatically")


def human_bytes(n: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(n)
    for u in units:
        if size < 1024.0 or u == units[-1]:
            return f"{size:.2f} {u}"
        size /= 1024.0


def path_size(path: Path) -> int:
    try:
        if not path.exists() and not path.is_symlink():
            return 0
        if path.is_symlink():
            # Count only the link itself, not the target
            return path.lstat().st_size
        if path.is_file():
            return path.stat().st_size
        total = 0
        for p in path.rglob("*"):
            try:
                if p.is_symlink():
                    total += p.lstat().st_size
                elif p.is_file():
                    total += p.stat().st_size
            except Exception:
                pass
        return total
    except Exception:
        return 0


def remove_path(p: Path) -> int:
    size = path_size(p)
    try:
        if p.is_dir() and not p.is_symlink():
            shutil.rmtree(p, ignore_errors=True)
        else:
            try:
                p.unlink()
            except FileNotFoundError:
                pass
    except Exception:
        pass
    return size


def remove_dir_contents(dir_path: Path, exclude_names=None) -> int:
    exclude = set(exclude_names or [])
    total = 0
    if not dir_path.exists():
        return 0
    for entry in dir_path.iterdir():
        if entry.name in exclude:
            continue
        total += remove_path(entry)
    return total


def remove_older_than(dir_path: Path, days: int) -> int:
    if not dir_path.exists():
        return 0
    cutoff = time.time() - days * 86400
    total = 0
    for entry in dir_path.iterdir():
        try:
            mtime = entry.stat().st_mtime
        except Exception:
            continue
        if mtime < cutoff:
            total += remove_path(entry)
    return total


def keep_newest_n_directories(dir_path: Path, keep: int) -> int:
    if not dir_path.exists():
        return 0
    entries = [e for e in dir_path.iterdir() if e.is_dir()]
    entries.sort(key=lambda p: p.stat().st_mtime if p.exists() else 0, reverse=True)
    total = 0
    for e in entries[keep:]:
        total += remove_path(e)
    return total


def run_cmd(cmd: List[str]) -> Tuple[int, str, str]:
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
    except FileNotFoundError:
        return 127, "", "not found"
    except Exception as e:
        return 1, "", str(e)


def has_cmd(name: str) -> bool:
    rc, _, _ = run_cmd(["bash", "-lc", f"command -v {name} >/dev/null 2>&1 && echo yes || echo no"])
    return rc == 0


def free_bytes_before_after() -> tuple[int, int]:
    st = os.statvfs(str(Path.home()))
    return st.f_bsize * st.f_bavail, int(time.time())


def main():
    """
    Clean macOS junk files for the current user.

    ---agentspec
    what: |
      Removes common junk safely for the current macOS user account:
      - Clears user cache directories (~/Library/Caches, ~/.cache)
      - Removes Xcode DerivedData, prunes Archives (older than 120 days),
        and trims iOS DeviceSupport to the 3 most recent entries
      - Deletes stale logs in ~/Library/Logs older than 30 days
      - Prunes package manager caches when available (brew, npm, yarn, pnpm,
        pip, conda)
      - Refreshes Quick Look cache and removes unavailable iOS simulators

      It avoids system directories and user content, and does not require sudo.

    deps:
      calls:
        - remove_dir_contents()
        - remove_older_than()
        - keep_newest_n_directories()
        - run_cmd(["brew", "cleanup", "-s", "--prune=all"]) (optional)
        - run_cmd(["npm", "cache", "clean", "--force"]) (optional)
        - run_cmd(["yarn", "cache", "clean"]) (optional)
        - run_cmd(["pnpm", "store", "prune"]) (optional)
        - run_cmd(["pip", "cache", "purge"]) (optional)
        - run_cmd(["conda", "clean", "-a", "-y"]) (optional)
        - run_cmd(["qlmanage", "-r", "cache"]) (optional)
        - run_cmd(["xcrun", "simctl", "delete", "unavailable"]) (optional)
      called_by:
        - CLI invocation: scripts/mac_cleanup.py
      environment:
        - macOS user environment; no sudo required

    why: |
      Caches and build artifacts can consume significant disk space on macOS.
      Removing them is safe because they are regenerated on demand. This tool
      targets predictable, recoverable data and leaves user documents and
      system areas untouched to minimize risk.

    guardrails:
      - DO NOT delete user Documents, Desktop, Downloads, Photos, or mail data
      - DO NOT use sudo or modify anything outside the user's home directory
      - DO NOT prune Docker images/containers/volumes automatically
      - DO NOT delete browser profiles or Application Support data
      - DO NOT empty Trash automatically; user should decide

    changelog:
      - "2025-10-31: Initial implementation of macOS user cleanup"
    ---/agentspec
    """

    print_agentspec()

    start_free, _ = free_bytes_before_after()

    total_removed = 0
    tasks = []

    home = Path.home()

    # 1) User caches
    caches = [
        home / "Library" / "Caches",
        home / ".cache",
    ]
    for c in caches:
        removed = remove_dir_contents(c)
        tasks.append((f"Clear contents of {c}", removed))
        total_removed += removed

    # 2) Xcode artifacts
    derived = home / "Library" / "Developer" / "Xcode" / "DerivedData"
    removed = remove_dir_contents(derived)
    tasks.append((f"Clear Xcode DerivedData {derived}", removed))
    total_removed += removed

    archives = home / "Library" / "Developer" / "Xcode" / "Archives"
    removed = remove_older_than(archives, days=120)
    tasks.append((f"Remove Xcode Archives older than 120 days {archives}", removed))
    total_removed += removed

    devices = home / "Library" / "Developer" / "Xcode" / "iOS DeviceSupport"
    removed = keep_newest_n_directories(devices, keep=3)
    tasks.append((f"Keep newest 3 iOS DeviceSupport in {devices}", removed))
    total_removed += removed

    # 3) Logs (stale)
    logs = home / "Library" / "Logs"
    removed = remove_older_than(logs, days=30)
    tasks.append((f"Remove logs older than 30 days in {logs}", removed))
    total_removed += removed

    # 4) Package manager caches (best-effort)
    # Homebrew
    if has_cmd("brew"):
        rc, out, err = run_cmd(["brew", "cleanup", "-s", "--prune=all"])  # may take time
        tasks.append(("Homebrew cleanup", 0))
        if out:
            print(out)
        if err and rc != 0:
            print(f"brew cleanup error: {err}")

    # npm
    if has_cmd("npm"):
        rc, out, err = run_cmd(["npm", "cache", "clean", "--force"])
        tasks.append(("npm cache clean", 0))
        if err and rc != 0:
            print(f"npm cache error: {err}")

    # yarn
    if has_cmd("yarn"):
        rc, out, err = run_cmd(["yarn", "cache", "clean"])
        tasks.append(("yarn cache clean", 0))
        if err and rc != 0:
            print(f"yarn cache error: {err}")

    # pnpm
    if has_cmd("pnpm"):
        rc, out, err = run_cmd(["pnpm", "store", "prune"])
        tasks.append(("pnpm store prune", 0))
        if err and rc != 0:
            print(f"pnpm prune error: {err}")

    # pip (try both pip and pip3)
    pip_names = []
    if has_cmd("pip"):
        pip_names.append("pip")
    if has_cmd("pip3"):
        pip_names.append("pip3")
    for pn in pip_names:
        rc, out, err = run_cmd([pn, "cache", "purge"])
        tasks.append((f"{pn} cache purge", 0))
        if err and rc != 0:
            print(f"{pn} cache error: {err}")

    # conda
    if has_cmd("conda"):
        rc, out, err = run_cmd(["conda", "clean", "-a", "-y"])
        tasks.append(("conda clean -a -y", 0))
        if err and rc != 0:
            print(f"conda clean error: {err}")

    # 5) Quick Look cache reset
    if has_cmd("qlmanage"):
        run_cmd(["qlmanage", "-r", "cache"])  # clear Quick Look cache
        run_cmd(["qlmanage", "-r"])  # restart Quick Look server
        tasks.append(("Quick Look cache reset", 0))

    # 6) Remove unavailable simulators (safe)
    if has_cmd("xcrun"):
        rc, out, err = run_cmd(["xcrun", "simctl", "delete", "unavailable"])
        tasks.append(("Delete unavailable iOS simulators", 0))
        if err and rc != 0:
            print(f"xcrun simctl error: {err}")

    end_free, _ = free_bytes_before_after()
    freed_estimate = start_free - end_free + total_removed  # start_free may change due to package manager cleanup; add measured removals

    print("\nCleanup summary:")
    for desc, bytes_removed in tasks:
        if bytes_removed > 0:
            print(f"- {desc}: {human_bytes(bytes_removed)} removed")
        else:
            print(f"- {desc}")

    print(f"\nEstimated space reclaimed: {human_bytes(total_removed)} (from direct deletions)")
    if freed_estimate > 0:
        print(f"Estimated net free change (includes tool cleanups): {human_bytes(freed_estimate)}")
    print("Note: Package manager cleanups may reclaim additional space not counted above.")
    print("Guardrail reminder: No user documents or Application Support data were removed.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted.")
        sys.exit(130)
