#!/usr/bin/env python3
"""Writes RenderToggler/RenderToggler.txt for the newest RenderToggler release of this repository - the list GT-Hub
(0.11.50 and newer) reads to fetch RenderToggler and keep it up to date in every game that has it.

A RenderToggler release: a published release (not a draft, not a pre-release) whose tag starts with "RenderToggler",
such as RenderToggler-1.0.0-EF447, with the files of RenderToggler's build in it - RenderToggler.addon64,
RenderToggler.addon (32-bit), the license texts, and RenderToggler.txt as the build writes it (its Version= line is
taken; without it the version is the tag without "RenderToggler-").

The list names the release (From=) and every file with its SHA-256, worked out here from the files themselves.
GT-Hub takes only files that match it, and only from a release of this repository.

Needs the GitHub CLI (gh, only its REST calls) with GH_TOKEN, and GITHUB_REPOSITORY (owner/name). Only the Python standard library.
Writes to GITHUB_OUTPUT: result=written|same|none, version=, tag=."""
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile

LIST = os.path.join("RenderToggler", "RenderToggler.txt")
REPO = os.environ.get("GITHUB_REPOSITORY", "Gametism/GT-Hub-Data")
# What GT-Hub accepts (src/hdr_mods.h: FromAllowed, SafeFileName).
TAG_OK = re.compile(r"^[A-Za-z0-9._+-]{1,100}$")
NAME_BAD = set('\\/:*?"<>|%')
KINDS = (".addon64", ".addon32", ".addon", ".txt")


def say(**what):
    out = os.environ.get("GITHUB_OUTPUT")
    text = "".join("%s=%s\n" % (k, str(v).replace("\n", " ")) for k, v in what.items())
    if out:
        with open(out, "a", encoding="utf-8") as f:
            f.write(text)
    sys.stdout.write(text)


def gh(*args, binary=False):
    return subprocess.run(["gh", *args], check=True, capture_output=True, text=not binary).stdout


def newest():
    """The newest published RenderToggler release (GitHub's REST answer for it), or None."""
    rows = json.loads(gh("api", "repos/%s/releases?per_page=100" % REPO))
    rows = [r for r in rows if not r.get("draft") and not r.get("prerelease") and r.get("published_at")
            and r["tag_name"].lower().startswith("rendertoggler")]
    rows.sort(key=lambda r: r["published_at"], reverse=True)
    return rows[0] if rows else None


def safe_name(n):
    return 0 < len(n) <= 120 and not n.startswith(".") and all(ord(c) >= 32 and c not in NAME_BAD for c in n)


def main():
    release = newest()
    if not release:
        print("No published RenderToggler release - the list stays as it is.")
        return say(result="none")
    tag = release["tag_name"]
    if not TAG_OK.match(tag) or ".." in tag:
        sys.exit("The tag %r has characters GT-Hub does not take in a link: letters, digits and . - _ + only." % tag)
    with tempfile.TemporaryDirectory() as d:
        for asset in release.get("assets", []):
            if not safe_name(asset["name"]):
                print("Left out (an odd name): %r" % asset["name"])
                continue
            data = gh("api", "-H", "Accept: application/octet-stream", "repos/%s/releases/assets/%d" % (REPO, asset["id"]), binary=True)
            with open(os.path.join(d, asset["name"]), "wb") as f:
                f.write(data)
        names = sorted(os.listdir(d), key=str.lower)
        version = ""
        files = []
        for n in names:
            path = os.path.join(d, n)
            if n.lower() == "rendertoggler.txt":
                with open(path, encoding="utf-8-sig", errors="replace") as f:
                    for line in f:
                        if line.startswith("Version="):
                            version = line[8:].strip()
                continue
            if not n.lower().endswith(KINDS) or not safe_name(n):
                print("Left out (not an add-on or a text): %s" % n)
                continue
            with open(path, "rb") as f:
                files.append((n, hashlib.sha256(f.read()).hexdigest()))
    if not any(n.lower().endswith((".addon64", ".addon32", ".addon")) for n, _ in files):
        sys.exit("The release %s has no RenderToggler.addon64 or RenderToggler.addon." % tag)
    if not version:
        version = tag[len("RenderToggler"):].lstrip("-_ ") or tag
    version = "".join(c for c in version if 32 <= ord(c) < 127)[:80]
    lines = [
        "; RenderToggler for GT-Hub (0.11.50 and newer) - written by .github/workflows/rendertoggler.yml from the",
        "; release %s. Not edited by hand: a new release writes it anew." % tag,
        "Version=%s" % version,
        "From=https://github.com/%s/releases/download/%s/" % (REPO, tag),
    ] + ["%s %s" % (n, h) for n, h in files]
    text = "\n".join(lines) + "\n"
    old = ""
    if os.path.exists(LIST):
        with open(LIST, encoding="utf-8") as f:
            old = f.read()
    if old == text:
        print("RenderToggler %s from %s - the list is that already." % (version, tag))
        return say(result="same", version=version, tag=tag)
    os.makedirs(os.path.dirname(LIST), exist_ok=True)
    with open(LIST, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print(text)
    say(result="written", version=version, tag=tag)


if __name__ == "__main__":
    main()
