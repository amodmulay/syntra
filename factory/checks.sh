#!/usr/bin/env bash
# This project's checks. Exit 0 only when the branch is fit to review.
#
# The gate runs this from the main checkout's copy of this file, with a job's
# worktree as the working directory. Keep it fast, deterministic and
# non-interactive: no watch modes, no prompts, nothing that rewrites files.
#
# This project is currently just a tiny calculator module under src/, tested
# with the standard library's unittest — no external dependencies to install.
set -euo pipefail

python3 -m py_compile src/*.py
python3 -m unittest discover -s tests -v
