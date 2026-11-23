#!/usr/bin/env python3
"""
ManageIt 9Router Provider

Adds the ManageIt AI Gateway provider to 9Router's SQLite database.

Features:
- Registers provider node (openai-compatible-chat-manageit)
- Registers connection with API key
- Adds only FREE models to customModels scope
- Safe: does not overwrite existing data unless --force is used
- Dry-run mode for testing

Usage:
    python3 manageit_9router.py --config config.yaml
    python3 manageit_9router.py --config config.yaml --force
    python3 manageit_9router.py --config config.yaml --dry-run

Models (all FREE):
    manageit/claude-haiku-5.5       # Anthropic
    manageit/nemotron-3-ultra-550b-a55b:free  # NVIDIA
    manageit/qwen3.6-35b-a3b-fp8    # Qwen
    manageit/qwen3.8-27b            # Qwen
"""

import argparse
import json
import os
import sys
import sqlite3
from datetime import datetime
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

# Default free models (only these, no paid models)
FREE_MODELS = {
    "manageit/claude-haiku-5.5": {
        "providerAlias": "manageit",
        "id": "claude-haiku-5.5",
        "type": "llm",
        "name": "ManageIt: claude-haiku-5.5",
    },
    "manageit/nemotron-3-ultra-550b-a55b:free": {
        "providerAlias": "manageit",
        "id": "nemotron-3-ultra-550b-a55b:free",
        "type": "llm",
        "name": "ManageIt: nemotron-3-ultra-550b-a55b:free",
    },
    "manageit/qwen3.6-35b-a3b-fp8": {
        "providerAlias": "manageit",
        "id": "qwen3.6-35b-a3b-fp8",
        "type": "llm",
        "name": "ManageIt: qwen3.6-35b-a3b-fp8",
    },
    "manageit/qwen3.8-27b": {
        "providerAlias": "manageit",
        "id": "qwen3.8-27b",
        "type": "llm",
        "name": "ManageIt: qwen3.8-27b",
    },
}

NODE_ID = "openai-compatible-chat-manageit"
CONN_ID = "conn-manageit"
BASE_URL = "https://ai.manageit.dev/api/v1"
DEFAULT_MODEL = "nemotron-3-ultra-550b-a55b:free"


def load_config(config_path):
    """Load config from YAML file or environment variables."""
    config = {
        "api_key": os.environ.get("MANAGEIT_AI_TOKEN", ""),
        "base_url": os.environ.get("MANAGEIT_BASE_URL", BASE_URL),
        "db_path": os.environ.get("G9ROUTER_DB", str(Path.home() / ".9router" / "db" / "data.sqlite")),
        "node_id": NODE_ID,
        "conn_id": CONN_ID,
    }

    if config_path and os.path.exists(config_path):
        if yaml is None:
            print("Error: PyYAML is not installed. Install with: pip install pyyaml", file=sys.stderr)
            sys.exit(1)
        with open(config_path) as f:
            file_config = yaml.safe_load(f) or {}
        config.update(file_config)

    api_key = config.get("api_key", "")
    if not api_key:
        print("Error: api_key is required. Set MANAGEIT_AI_TOKEN env var or in config.yaml", file=sys.stderr)
        sys.exit(1)

    return config


def get_current_nodes(conn):
    """Check if node/connection already exist."""
    c = conn.cursor()
    c.execute("SELECT id, data FROM providerNodes WHERE id=?", (NODE_ID,))
    node = c.fetchone()
    c.execute("SELECT id, data FROM providerConnections WHERE id=?", (CONN_ID,))
    conn_row = c.fetchone()
    return node, conn_row


def register_node(conn, config, dry_run=False):
    """Register the provider node in providerNodes table."""
    sql = """
        INSERT OR REPLACE INTO providerNodes (id, type, name, data, createdAt, updatedAt)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    data = json.dumps({
        "prefix": "manageit",
        "apiType": "chat",
        "baseUrl": config["base_url"],
        "nodeName": "ManageIt AI",
    }, ensure_ascii=False)
    now = datetime.now().isoformat()
    params = (config["node_id"], "openai-compatible", "ManageIt AI", data, now, now)

    if dry_run:
        print(f"[DRY-RUN] Would insert node: {params[:3]}")
        return

    c = conn.cursor()
    c.execute(sql, params)
    conn.commit()
    print(f"[OK] Node registered: {config['node_id']}")


def register_connection(conn, config, dry_run=False):
    """Register the connection in providerConnections table."""
    sql = """
        INSERT OR REPLACE INTO providerConnections
        (id, provider, authType, name, email, priority, isActive, data, createdAt, updatedAt)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    data = json.dumps({
        "defaultModel": DEFAULT_MODEL,
        "apiKey": config["api_key"],
        "testStatus": "active",
        "prefix": "manageit",
        "apiType": "chat",
        "baseUrl": config["base_url"],
        "nodeName": "ManageIt AI",
        "models": list(FREE_MODELS.keys()),
        "providerSpecificData": {
            "prefix": "manageit",
            "apiType": "chat",
            "baseUrl": config["base_url"],
            "nodeName": "ManageIt AI",
            "connectionProxyEnabled": False,
        },
    }, ensure_ascii=False)
    now = datetime.now().isoformat()
    params = (
        config["conn_id"],
        config["node_id"],
        "apikey",
        "ManageIt AI",
        "",
        1,
        1,
        data,
        now,
        now,
    )

    if dry_run:
        print(f"[DRY-RUN] Would insert connection: {params[:4]}")
        return

    c = conn.cursor()
    c.execute(sql, params)
    conn.commit()
    print(f"[OK] Connection registered: {config['conn_id']}")


def register_custom_models(conn, config, models=None, dry_run=False):
    """Register free models in kv table (scope=customModels)."""
    if models is None:
        models = FREE_MODELS

    scope = "customModels"
    node_slug = config["node_id"].replace("openai-compatible-chat-", "")
    c = conn.cursor()
    for model_id, meta in models.items():
        # model_id uses "manageit/..." prefix; remove it for the key
        model_key = model_id.split("/", 1)[1] if "/" in model_id else model_id
        key = f"{node_slug}|{model_key}|llm"
        value = json.dumps(meta, ensure_ascii=False)
        # Only insert if not exists
        c.execute("SELECT 1 FROM kv WHERE scope=? AND key=?", (scope, key))
        if c.fetchone():
            continue

        insert_sql = """
            INSERT OR REPLACE INTO kv (scope, key, value)
            VALUES (?, ?, ?)
        """
        params = (scope, key, value)
        if dry_run:
            print(f"[DRY-RUN] Would insert custom model: {key}")
            continue

        c.execute(insert_sql, params)
        conn.commit()
        print(f"[OK] Custom model added: {model_id}")


def restart_9router(dry_run=False):
    """Restart 9Router service."""
    # Try launchctl first
    try:
        import subprocess
        if dry_run:
            print("[DRY-RUN] Would restart 9Router via launchctl")
            return
        subprocess.run(
            ["launchctl", "kickstart", "-k", f"gui/{os.getuid()}/ai.hermes.9router"],
            check=True,
            capture_output=True,
            text=True,
        )
        print("[OK] 9Router restarted")
    except subprocess.CalledProcessError as e:
        print(f"[WARN] Failed to restart via launchctl: {e.stderr}", file=sys.stderr)
    except FileNotFoundError:
        print("[WARN] launchctl not available", file=sys.stderr)

    # Fallback: try to kill and respawn
    try:
        import subprocess
        subprocess.run(
            ["pkill", "-f", "ai.hermes.9router"],
            check=True,
            capture_output=True,
            text=True,
        )
        print("[OK] 9Router process killed")
    except subprocess.CalledProcessError:
        pass


def main():
    parser = argparse.ArgumentParser(
        description="Add ManageIt AI Gateway to 9Router",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--config", "-c",
        help="Path to YAML config file",
    )
    parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="Overwrite existing connection if present",
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Show what would be done without making changes",
    )
    parser.add_argument(
        "--free-only", action="store_true",
        help="Only register free models (default: yes)",
    )
    args = parser.parse_args()

    config = load_config(args.config)

    if not args.dry_run:
        print(f"\n{'='*50}")
        print("   ManageIt 9Router Provider Setup")
        print(f"{'='*50}\n")

    # Connect to database
    db_path = Path(config["db_path"])
    if not db_path.exists():
        print(f"Error: 9Router database not found at {db_path}", file=sys.stderr)
        sys.exit(1)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    # Check existing data
    node, conn_row = get_current_nodes(conn)
    if node and not args.force:
        print(f"[!] Node already exists: {node[0]}", file=sys.stderr)
        print(f"[!] Use --force to overwrite", file=sys.stderr)
    else:
        register_node(conn, config, dry_run=args.dry_run)
        register_connection(conn, config, dry_run=args.dry_run)
        print(f"[OK] Node and connection registered")

    # Add free models (always add, even in dry-run)
    if args.free_only:
        print(f"\n{'='*50}")
        print("   Adding free models to customModels...")
        register_custom_models(conn, config, models=FREE_MODELS, dry_run=args.dry_run)
        print(f"{'='*50}\n")
    else:
        # Add free models by default
        print(f"   Adding free models to customModels...")
        register_custom_models(conn, config, models=FREE_MODELS, dry_run=args.dry_run)
        print(f"   Done adding free models: {len(FREE_MODELS)}\n")

    if args.free_only:
        print(f"\n{'='*50}")
        print("   Adding free models to customModels...")
        register_custom_models(conn, config, models=FREE_MODELS, dry_run=args.dry_run)
        print(f"{'='*50}\n")

    # Restart 9Router
    if not args.dry_run:
        if not args.force or not node:
            restart_9router(dry_run=args.dry_run)
        else:
            print(f"[OK] 9Router not restarted (forced overwrite)\n")

    print(f"\nDone! Models registered: {len(FREE_MODELS)}")
    print("Visit http://127.0.0.1:20128/v1/models to verify.\n")


if __name__ == "__main__":
    main()
