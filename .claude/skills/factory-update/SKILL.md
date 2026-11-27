---
name: factory-update
description: Update this project's installed Syntra factory to a newer Syntra version without losing project-specific tailoring.
argument-hint: <path-or-git-url-of-syntra>
disable-model-invocation: true
---

# Update the installed factory

Bring this project's factory up to date with a newer Syntra. The argument is a
local checkout of Syntra or its git URL. If none is given, use the `source`
recorded in `factory/.installed.json`; if that is missing too, ask for it.

`factory/bin/update` does the mechanical part. It sorts files by
`factory/manifest.json` in the source: generic files are replaced, project-
tailored files are never touched, `config.json` only gains new keys. Read its
header (`factory/bin/update --help`) if anything below is unclear. Never edit
`factory/jobs/` by hand, and never push.

## Steps

1. **Start clean.** `git status --short`. If the factory's files have
   uncommitted changes, ask the user to commit them first (the `/factory-commit`
   skill does it) so the update lands as a reviewable diff.
2. **No work in flight.** Jobs that are not merged or rejected block the update.
   List them and ask whether to finish or reject them first. Use `--force`
   only if the user says so.
3. **Dry run.** `python3 factory/bin/update <source>`. Show the user the plan.
   - `update` / `add`: safe, will be applied.
   - `EDITED`: the user changed a generic file (or it has no baseline). It is
     skipped. Show the diff against upstream, ask what to do, and only then
     re-run with `--force` or merge by hand.
   - `review`: upstream changed a project-tailored file (a playbook, `checks.sh`,
     the triage or reviewer agents). The printed diff is what changed upstream.
4. **Apply.** `python3 factory/bin/update <source> --apply`.
5. **Merge tailored files by hand.** For each `review` file, apply the upstream
   change to the project's version while keeping its project-specific content.
   Never replace such a file with the template. A new `adapted_new` template
   (a file the project didn't have) must be tailored before it is used.
6. **Check `factory/config.json`.** New keys were filled with upstream defaults;
   confirm they suit the project (for example `concurrency`).
7. **Verify, as INSTALL.md step 3 does:** `bash factory/checks.sh` exits 0,
   `factory/bin/job queue` runs, `python3 -m json.tool factory/config.json`
   succeeds, and every `.claude/agents/*.md` still has only the frontmatter keys
   `name`, `description`, `tools`, `model` (and `hooks` on `builder.md`).
8. **Commit.** Stay on the current branch. Commit the update, including
   `factory/.installed.json`, with a one-line message, and show the diff. Ask
   before pushing.

If the project predates `factory/bin/update` (no `factory/.installed.json`),
copy the source's `factory/bin/update` into the project first, then run `factory/bin/update <source> --adopt`
once to record a baseline, then continue from step 3. Files edited since the
install show as `EDITED` on that first run, which is the safe default.
