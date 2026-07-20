#!/usr/bin/env python3
"""
Academic Assistant — One-Click Setup Script

Usage:
    python setup.py                   # interactive mode
    python setup.py --path /path/to/project
    python setup.py --dry-run         # preview without making changes
"""

import json
import os
import shutil
import sys
import subprocess
import argparse
from pathlib import Path


# ── Colors ──────────────────────────────────────────────
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"


def info(msg):    print(f"  {CYAN}ℹ{RESET} {msg}")
def ok(msg):      print(f"  {GREEN}✔{RESET} {msg}")
def warn(msg):    print(f"  {YELLOW}⚠{RESET} {msg}")
def error(msg):   print(f"  {RED}✘{RESET} {msg}")
def section(msg): print(f"\n{BOLD}── {msg} ──{RESET}")


def find_openclaw_config() -> Path | None:
    """Try to locate OpenClaw config in common locations."""
    candidates = [
        # Linux / macOS
        Path.home() / ".openclaw" / "openclaw.json",
        Path.home() / ".config" / "openclaw" / "openclaw.json",
        # Windows (from WSL or native)
        Path("/mnt/c/Users") / os.environ.get("USER", "") / ".openclaw" / "openclaw.json",
    ]

    # Search under /mnt/c/Users/ for potential Windows users
    mnt_users = Path("/mnt/c/Users")
    if mnt_users.exists():
        for user_dir in mnt_users.iterdir():
            if user_dir.is_dir():
                win_path = user_dir / ".openclaw" / "openclaw.json"
                if win_path.exists():
                    candidates.append(win_path)

    for p in candidates:
        if p and p.exists():
            return p
    return None


def merge_agent_config(base_config: dict, new_agents: list) -> dict:
    """Merge new agents into existing OpenClaw config."""
    config = base_config.copy()

    if "agents" not in config:
        config["agents"] = {"list": []}
    if "list" not in config["agents"]:
        config["agents"]["list"] = []

    existing_ids = {a.get("id") for a in config["agents"]["list"]}
    merged = list(config["agents"]["list"])

    for agent in new_agents:
        if agent.get("id") in existing_ids:
            warn(f"Agent '{agent['id']}' already exists, skipping")
        else:
            merged.append(agent)
            ok(f"Added agent: {agent.get('id', '?')}")

    # Merge defaults
    if "defaults" in new_agents and "defaults" not in config.get("agents", {}):
        config.setdefault("agents", {}).setdefault("defaults", {})
        if not config["agents"]["defaults"]:
            config["agents"]["defaults"] = new_agents["defaults"]
            ok("Merged agent defaults")

    config["agents"]["list"] = merged
    return config


def normalize_paths(agent_config: dict, project_root: str) -> dict:
    """Normalize agent workspace paths to match user's environment."""
    config = json.loads(json.dumps(agent_config))  # deep copy

    for agent in config.get("list", []):
        ws = agent.get("workspace", "")
        if "academic-assistant" in ws:
            # Replace the path prefix with the actual project root
            agent["workspace"] = str(Path(project_root) / "agents-workspace" / Path(ws).name)
    return config


def check_openclaw_installed() -> bool:
    """Check if OpenClaw CLI is available."""
    try:
        result = subprocess.run(
            ["openclaw", "--version"],
            capture_output=True, text=True, timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def run_setup(project_root: str, dry_run: bool = False):
    """Main setup routine."""
    root = Path(project_root).resolve()

    print(f"{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}  Academic Assistant — Setup{RESET}")
    print(f"  Project: {root}")
    if dry_run:
        print(f"  {YELLOW}Mode: Dry Run (no changes will be made){RESET}")
    print(f"{BOLD}{'='*60}{RESET}")

    # ── 1. Validate project ─────────────────────────────
    section("1/5  Validating Project Structure")

    required_paths = [
        "config/openclaw.agents.json",
        "config/default.yaml",
        "shared/scripts/store_to_db_a.py",
    ]

    all_ok = True
    for rp in required_paths:
        p = root / rp
        if p.exists():
            ok(f"Found {rp}")
        else:
            warn(f"Missing {rp}")
            all_ok = False

    if not all_ok:
        error("Project structure is incomplete. Are you in the right directory?")
        return False

    ok("Project structure looks good")

    # ── 2. Check OpenClaw ───────────────────────────────
    section("2/5  Checking OpenClaw Runtime")

    installed = check_openclaw_installed()
    if installed:
        ok("OpenClaw CLI is available")
    else:
        warn("OpenClaw CLI not found in PATH")
        warn("Make sure OpenClaw is installed before using the agents")

    # ── 3. Merge Agent Config ────────────────────────────
    section("3/5  Merging Agent Configuration")

    # Read project agent config
    with open(root / "config" / "openclaw.agents.json") as f:
        project_agent_config = json.load(f)

    # Normalize paths
    normalized = normalize_paths(project_agent_config["agents"], str(root))

    # Find and read OpenClaw config
    openclaw_cfg_path = find_openclaw_config()
    if openclaw_cfg_path:
        ok(f"Found OpenClaw config at: {openclaw_cfg_path}")

        with open(openclaw_cfg_path) as f:
            base_config = json.load(f)

        merged = merge_agent_config(base_config, normalized.get("list", []))

        if not dry_run:
            # Backup
            backup_path = openclaw_cfg_path.with_suffix(".json.bak")
            if not backup_path.exists():
                shutil.copy2(openclaw_cfg_path, backup_path)
                ok(f"Backup created at: {backup_path}")

            with open(openclaw_cfg_path, "w", encoding="utf-8") as f:
                json.dump(merged, f, ensure_ascii=False, indent=2)
            ok(f"Updated: {openclaw_cfg_path}")
        else:
            info(f"[DRY RUN] Would update: {openclaw_cfg_path}")
    else:
        warn("OpenClaw config not found — creating default config")
        if not dry_run:
            target_dir = Path.home() / ".openclaw"
            target_dir.mkdir(parents=True, exist_ok=True)
            target = target_dir / "openclaw.json"
            merged = normalized
            with open(target, "w", encoding="utf-8") as f:
                json.dump({"agents": merged}, f, ensure_ascii=False, indent=2)
            ok(f"Created: {target}")
        else:
            info("[DRY RUN] Would create default config at ~/.openclaw/openclaw.json")

    # ── 4. Create Data Directories ──────────────────────
    section("4/5  Setting Up Data Directories")

    data_dirs = [
        "data/task_storage",
        "logs",
    ]

    for d in data_dirs:
        p = root / d
        if not p.exists():
            if not dry_run:
                p.mkdir(parents=True, exist_ok=True)
                ok(f"Created: {d}/")
            else:
                info(f"[DRY RUN] Would create: {d}/")
        else:
            ok(f"Exists: {d}/")

    # Check shared data dirs
    for d in ["shared/db_a", "shared/db_b"]:
        p = root / d
        if p.exists() and any(p.iterdir()):
            info(f"Data exists in {d}/")

    # ── 5. Final Summary ────────────────────────────────
    section("5/5  Summary")

    print()
    ok("Setup complete!" if not dry_run else "[DRY RUN] Preview complete")
    print()
    print(f"  {BOLD}Next steps:{RESET}")
    print(f"   1. Restart OpenClaw Gateway:")
    print(f"      $ openclaw gateway restart")
    print()
    print(f"   2. Start chatting with your academic assistant")
    print()
    print(f"  {BOLD}Useful commands:{RESET}")
    print(f"     Demo data:  python {root / 'shared/scripts/store_to_db_a.py'} --help")
    print(f"     Restart:    openclaw gateway restart")
    print(f"     Status:     openclaw status")
    print()

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Academic Assistant — One-Click Setup"
    )
    parser.add_argument(
        "--path", "-p",
        default=None,
        help="Path to the academic-assistant project root"
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Preview changes without applying them"
    )
    args = parser.parse_args()

    # Auto-detect project root
    project_root = args.path
    if not project_root:
        # Try current directory
        cwd = Path.cwd()
        if (cwd / "config" / "openclaw.agents.json").exists():
            project_root = str(cwd)
        else:
            # Try common locations
            candidates = [
                Path("/mnt/c/Users") / os.environ.get("USER", "") / "Desktop",
                Path.home(),
            ]
            # Search for academic-assistant in common dirs
            for base in candidates:
                for child in base.rglob("academic-assistant"):
                    if (child / "config" / "openclaw.agents.json").exists():
                        project_root = str(child)
                        break

            if not project_root:
                print(f"{RED}Error: Could not find project root.{RESET}")
                print("Usage: python setup.py --path /path/to/academic-assistant")
                sys.exit(1)

    success = run_setup(project_root, dry_run=args.dry_run)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
