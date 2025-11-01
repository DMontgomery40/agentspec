#!/usr/bin/env python3
import os
import sys
import subprocess
from pathlib import Path


def print_agentspec():
    print("[AGENTSPEC] Reading spec for docker_aggressive_prune.main")
    print("[AGENTSPEC] What: Aggressively prune Docker builder caches, unused images, stopped containers, unused networks, and unused volumes. Does NOT stop running containers.")
    print("[AGENTSPEC] Deps: docker CLI and Docker Desktop/Engine must be available.")
    print("[AGENTSPEC] Guardrails:")
    print("[AGENTSPEC]   - DO NOT stop or remove running containers")
    print("[AGENTSPEC]   - DO NOT use sudo or touch host system files")
    print("[AGENTSPEC]   - DO NOT remove data outside Docker-managed volumes and caches")


def run_cmd(cmd):
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


def main():
    """
    Aggressively prune Docker resources without stopping running containers.

    ---agentspec
    what: |
      Performs a comprehensive Docker cleanup for local development environments:
      - Prunes BuildKit/builder caches (docker builder prune --all)
      - Prunes all unused images, stopped containers, unused networks
      - Prunes all unused volumes

      Running containers are untouched. This is intended to reclaim disk space
      aggressively while avoiding disruption to active workloads.

    deps:
      calls:
        - docker system df -v (for before/after)
        - docker builder prune --all --force
        - docker buildx prune -af (optional)
        - docker system prune -a --volumes -f
      environment:
        - Docker CLI and engine/desktop available to current user

    why: |
      Docker caches and unused resources can silently accumulate many gigabytes.
      Pruning these is safe for development because Docker can recreate them as
      needed. Keeping running containers intact avoids disrupting current work.

    guardrails:
      - DO NOT stop or remove running containers
      - DO NOT use sudo or modify host files; operate only via docker CLI
      - DO NOT remove non-Docker files; only prune via docker commands

    changelog:
      - "2025-10-31: Initial aggressive Docker prune utility"
    ---/agentspec
    """
    print_agentspec()

    if not has_cmd("docker"):
        print("Docker CLI not found. Please install Docker Desktop or Docker Engine.")
        sys.exit(1)

    # Show pre-clean state
    print("\n[Docker] Before prune: docker system df -v")
    rc, out, err = run_cmd(["docker", "system", "df", "-v"])
    if out:
        print(out)
    if err and rc != 0:
        print(f"docker system df error: {err}")

    # Count running containers for safety context
    _, running, _ = run_cmd(["bash", "-lc", "docker ps -q | wc -l"])
    print(f"[Docker] Running containers: {running.strip()}")

    # 1) Builder cache prune
    print("\n[Docker] Pruning builder cache (docker builder prune --all --force)...")
    rc, out, err = run_cmd(["docker", "builder", "prune", "--all", "--force"])
    if out:
        print(out)
    if err and rc != 0:
        print(f"builder prune error: {err}")

    # 1b) Buildx cache prune (best-effort)
    rc, _, _ = run_cmd(["bash", "-lc", "docker buildx version >/dev/null 2>&1"])
    if rc == 0:
        print("[Docker] Pruning buildx cache (docker buildx prune -af)...")
        rc2, out2, err2 = run_cmd(["docker", "buildx", "prune", "-af"])
        if out2:
            print(out2)
        if err2 and rc2 != 0:
            print(f"buildx prune error: {err2}")

    # 2) System prune (images, containers, networks, volumes)
    print("\n[Docker] Pruning unused images/containers/networks/volumes (docker system prune -a --volumes -f)...")
    rc, out, err = run_cmd(["docker", "system", "prune", "-a", "--volumes", "-f"])
    if out:
        print(out)
    if err and rc != 0:
        print(f"system prune error: {err}")

    # Show post-clean state
    print("\n[Docker] After prune: docker system df -v")
    rc, out, err = run_cmd(["docker", "system", "df", "-v"])
    if out:
        print(out)
    if err and rc != 0:
        print(f"docker system df error: {err}")

    print("\nGuardrail reminder: No running containers were stopped.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted.")
        sys.exit(130)

