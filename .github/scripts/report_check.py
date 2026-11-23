#!/usr/bin/env python3
"""Looks at a problem report - an issue that GT-Hub's "Share A Report" opened ("Report: ... GT-Hub 0.13.38 ..."),
or any issue that says what went wrong - and says what to do with it:

    labels=report,GT-Hub 0.13.38[,crash][,needs report file]
    unlabel=needs report file          (the report's zip came in a comment since)
    ask=1                              ask once for the report's zip (none attached, not asked yet)

Reads the issue from the environment: ISSUE_TITLE, ISSUE_BODY, and COMMENTS - a file with the bodies of the
issue's comments, one after another. Writes its answer to GITHUB_OUTPUT. Only the Python standard library.
The daily look at new reports reads the zips themselves; this only sorts them and asks for what is missing."""
import os
import re

ASKED = "<!-- report-check: zip -->"


def main():
    title = os.environ.get("ISSUE_TITLE", "")
    body = os.environ.get("ISSUE_BODY", "") or ""
    comments = ""
    path = os.environ.get("COMMENTS", "")
    if path and os.path.exists(path):
        with open(path, encoding="utf-8", errors="replace") as f:
            comments = f.read()
    everything = body + "\n" + comments

    # A report: GT-Hub's own (its title and its table), or an issue whose words are about a problem.
    ours = title.startswith("Report:") or "| GT-Hub |" in body or "**Report file:**" in body
    if not ours:
        out(labels="", unlabel="", ask="0")
        return

    labels = ["report"]
    m = re.search(r"\|\s*GT-Hub\s*\|\s*(\d+\.\d+\.\d+)\s*\|", body) or re.search(r"GT-Hub\s+(\d+\.\d+\.\d+)", title)
    if m:
        labels.append("GT-Hub " + m.group(1))
    if "crash" in title.lower() or "**Crashes:**" in body:
        labels.append("crash")

    # The zip: dragged into the issue or a comment (GitHub keeps it at github.com/user-attachments/files/...).
    zipped = re.search(r"https://github\.com/(?:user-attachments/files|[^/\s]+/[^/\s]+/files)/\d+/[^\s)\]]+\.zip", everything, re.I) is not None
    unlabel = ""
    ask = "0"
    if zipped:
        unlabel = "needs report file"
    else:
        labels.append("needs report file")
        if ASKED not in comments:
            ask = "1"
    out(labels=",".join(labels), unlabel=unlabel, ask=ask)


def out(**kv):
    target = os.environ.get("GITHUB_OUTPUT")
    lines = "".join(f"{k}={v}\n" for k, v in kv.items())
    if target:
        with open(target, "a", encoding="utf-8") as f:
            f.write(lines)
    else:
        print(lines, end="")


if __name__ == "__main__":
    main()
