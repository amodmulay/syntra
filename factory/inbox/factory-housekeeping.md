<!-- factory-issue: 18 -->
# Factory housekeeping

Small fixes found in a project review: the factory skill says concurrency is currently 3 while config.json says 5 (state it as configurable instead); `job queue` prints `concurrency N reached` for held topics even when nothing is running (say the free slots were taken by the topics above); `job` with no arguments crashes on a Windows console because the usage text contains `→`; finished topics stay in `factory/inbox/` forever (archive them or hide them); `HANDOVER.md` is a stale chat transcript and `screenshots/` is committed with spaces in file names (remove or move them).
