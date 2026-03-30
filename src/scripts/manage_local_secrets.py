from __future__ import annotations

import argparse
import getpass
from pathlib import Path
import sys

SRC_ROOT = Path(__file__).resolve().parent.parent
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from config.secrets import (
    SECRET_KEYS,
    delete_secret_from_keyring,
    get_secret_status,
    set_secret_in_keyring,
)


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    if args.command == "status":
        _print_status()
        return

    if args.command == "set":
        secret_value = args.value if args.value is not None else getpass.getpass(f"Value for {args.key}: ")
        set_secret_in_keyring(args.key, secret_value)
        print(f"Stored {args.key} in the local credential manager.")
        return

    if args.command == "delete":
        deleted = delete_secret_from_keyring(args.key)
        if deleted:
            print(f"Deleted {args.key} from the local credential manager.")
        else:
            print(f"No stored keyring entry found for {args.key}.")
        return


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage local KickAdvisor secrets without printing secret values.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("status", help="Show which secrets are configured and where they come from.")

    set_parser = subparsers.add_parser("set", help="Store a secret in the local credential manager.")
    set_parser.add_argument("key", choices=sorted(SECRET_KEYS.keys()))
    set_parser.add_argument("--value", help="Optional secret value. If omitted, you will be prompted securely.")

    delete_parser = subparsers.add_parser("delete", help="Delete a secret from the local credential manager.")
    delete_parser.add_argument("key", choices=sorted(SECRET_KEYS.keys()))
    return parser


def _print_status() -> None:
    print("KickAdvisor local secret status:\n")
    for item in get_secret_status():
        state = "configured" if item["configured"] else "missing"
        source = item["source"] or "-"
        print(f"{item['key']}: {state} | source={source} | {item['description']}")


if __name__ == "__main__":
    main()