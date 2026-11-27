#!/usr/bin/env bash
# Start the Syntra factory dashboard in the background and print its URL.
#
# The factory never starts the dashboard by itself; run this when you want it.
# Safe to run repeatedly: if this factory's dashboard is already up, it just
# prints the address. It only listens on 127.0.0.1. The port starts at
# `dashboard.port` in factory/config.json (default 8000) and moves up if taken.
set -eu

root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if command -v python3 >/dev/null 2>&1; then
  py=python3
elif command -v python >/dev/null 2>&1; then
  py=python
else
  echo "start-dashboard.sh: Python 3.10+ is required (python3 or python not found)" >&2
  exit 1
fi

exec "$py" "$root/factory/bin/dashboard" "$@"
