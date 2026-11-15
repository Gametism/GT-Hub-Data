#!/usr/bin/env python3
"""Takes the line from a Sidewarden suggestion (an issue that "Suggest For Everyone" opened) into
sidewarden-data.txt - checked by the same rules Sidewarden reads the list with, so that a line that gets in
is one every Sidewarden takes.

Reads the issue from the environment (ISSUE_TITLE, ISSUE_BODY), changes sidewarden-data.txt where the line
belongs, and writes what happened to GITHUB_OUTPUT:
    result=added     the line is in the list now
    result=updated   the game had that argument already; its words are the issue's now
    result=already   the very line was there
    result=invalid   the line breaks a rule; `reason` says which
    result=none      not a suggestion this script knows (nothing is done)
Only the Python standard library."""
import os
import re
import sys

LIST = "sidewarden-data.txt"


def plain(text, most):
    """Plain words only: no control characters, no < or >, `most` characters at most."""
    return len(text) <= most and all(ord(c) >= 0x20 and c not in "<>" for c in text)


def match_ok(key):
    """steam:<number>, exe:<file name> or engine:<ue3, ue4, unity, source>."""
    kind, colon, rest = key.partition(":")
    if not colon or not rest or len(key) > 120:
        return False
    if any(ord(c) < 0x21 or c in "|\\/" for c in rest):
        return False
    if kind == "steam":
        return rest.isdigit() and len(rest) <= 10
    if kind == "engine":
        return rest in ("ue3", "ue4", "unity", "source")
    return kind == "exe"


def pattern_ok(name):
    """A file name to look for next to a game's exe: a name, no path."""
    if not name or len(name) > 80 or name == "." or ".." in name:
        return False
    return all(0x20 <= ord(c) <= 0x7E and c not in '\\/:"<>|,' for c in name)


def check_arguments(fields):
    if len(fields) != 3:
        return "it needs three parts: which game | the argument(s) | what it does"
    key, args, title = fields
    if not match_ok(key.lower()):
        return "the game is given as steam:<its Steam number>, exe:<its exe's file name> or engine:<ue3, ue4, unity, source>"
    if not args or len(args) > 200 or any(not 0x20 <= ord(c) <= 0x7E for c in args):
        return "the arguments have to be plain characters, 200 at most"
    if args.count('"') % 2:
        return "a quotation mark in the arguments is not closed"
    if not title or title.startswith("("):
        return 'the third part says what the arguments do, in a few words (instead of "(what it does)")'
    if not plain(title, 80):
        return "what it does is %d characters long; 80 at most, and no < or >" % len(title)
    return ""


def check_affinity(fields):
    if len(fields) > 5 or len(fields) < 3:
        return "it needs these parts: which game | cores | why | fixed by | only beside"
    fields = fields + [""] * (5 - len(fields))
    key = fields[0]
    cores, why, fixed, beside = [("" if f == "-" else f) for f in fields[1:5]]
    if not match_ok(key.lower()) or key.lower().startswith("engine:"):
        return "the game is given as steam:<its Steam number> or exe:<its exe's file name>"
    if not cores.isdigit() or len(cores) > 2 or not 1 <= int(cores) <= 64:
        return "the cores are a number from 1 to 64"
    if not why or why.startswith("("):
        return 'the third part says what happens with all cores (instead of "(what happens without it)")'
    if not plain(why, 120) or any(ord(c) > 0x7E for c in why):
        return "why is %d characters long; 120 at most, plain letters" % len(why)
    if fixed and not all(n == "steam" or pattern_ok(n) for n in fixed.split(",")):
        return "fixed by is steam, or file names with commas between them"
    if beside and not pattern_ok(beside):
        return "only beside is one file name"
    return ""


def the_line(body):
    """The first line with text after "Line for the list:"."""
    lines = body.replace("\r", "").split("\n")
    for i, line in enumerate(lines):
        if line.strip().lower().rstrip(":") == "line for the list":
            for after in lines[i + 1:]:
                after = after.strip().strip("`").strip()
                if after:
                    return after
    return ""


def fields_of(line):
    return [f.strip() for f in line.split("|")]


def answer_to(body, question):
    """What was written after "<question>" ("What they do (a few words, ...):") - on its line, or on the next
    line with text before the next question. Empty: nothing."""
    lines = body.replace("\r", "").split("\n")
    for i, line in enumerate(lines):
        if line.strip().lower().startswith(question.lower()):
            rest = line.split(":", 1)[1].strip() if ":" in line else ""
            if rest:
                return rest
            for after in lines[i + 1:]:
                after = after.strip()
                if not after:
                    continue
                if ":" in after and after.split(":", 1)[0].strip().lower() in ("tried and working", "tried and working with fewer", "line for the list"):
                    return ""
                return after
    return ""


def put_in(text, section, line, same):
    """`line` into `section`: in place of a line that `same` says is the same one, else at the section's end
    (before the empty lines that close it). Returns (text, what happened)."""
    lines = text.replace("\r\n", "\n").split("\n")
    start = None
    for i, l in enumerate(lines):
        if l.strip().lower() == "[%s]" % section:
            start = i
            break
    if start is None:
        lines += ["", "[%s]" % section, line]
        return "\n".join(lines), "added"
    end = len(lines)
    for i in range(start + 1, len(lines)):
        if lines[i].strip().startswith("["):
            end = i
            break
    for i in range(start + 1, end):
        l = lines[i].strip()
        if not l or l.startswith(";") or l.startswith("#"):
            continue
        if l == line:
            return text, "already"
        if same(fields_of(l)):
            lines[i] = line
            return "\n".join(lines), "updated"
    at = end
    while at - 1 > start and not lines[at - 1].strip():
        at -= 1
    lines.insert(at, line)
    return "\n".join(lines), "added"


def say(**what):
    out = os.environ.get("GITHUB_OUTPUT")
    text = "".join("%s=%s\n" % (k, str(v).replace("\n", " ")) for k, v in what.items())
    if out:
        with open(out, "a", encoding="utf-8") as f:
            f.write(text)
    sys.stdout.write(text)


def main():
    title = os.environ.get("ISSUE_TITLE", "")
    body = os.environ.get("ISSUE_BODY", "")
    if title.lower().startswith("launch arguments for"):
        section, check = "arguments", check_arguments
    elif title.lower().startswith("cpu cores for"):
        section, check = "affinity", check_affinity
    else:
        return say(result="none")
    line = the_line(body)
    if not line:
        return say(result="invalid", reason='there is no line under "Line for the list:"')
    fields = fields_of(line)
    # (A line that still says "(what it does)": the answer written above it takes its place.)
    if len(fields) >= 3 and fields[2].startswith("("):
        said = answer_to(body, "What they do" if section == "arguments" else "What happens with all cores")
        if said:
            fields[2] = said
    reason = check(fields)
    if reason:
        return say(result="invalid", reason=reason, line=line)
    fields[0] = fields[0].lower()
    line = " | ".join(fields)
    if section == "arguments":
        same = lambda f: len(f) >= 2 and f[0].lower() == fields[0] and f[1].lower() == fields[1].lower()
    else:
        same = lambda f: len(f) >= 1 and f[0].lower() == fields[0]
    with open(LIST, encoding="utf-8") as f:
        text = f.read()
    new, what = put_in(text, section, line, same)
    if what != "already":
        with open(LIST, "w", encoding="utf-8", newline="\n") as f:
            f.write(new if new.endswith("\n") else new + "\n")
    say(result=what, line=line, section=section)


if __name__ == "__main__":
    main()
