#!/usr/bin/env python3
"""Writes the [supporters] section of gt-hub-data.txt from Gametism's Patreon: everyone who supports it now, by tier.
GT-Hub (0.11.58 and newer) thanks them by name in About GT-Hub.

Who is in it: the members whose patron_status is "active_patron". Their tier is the highest one they are entitled to
now (by its price); the tiers in the order of their price, the highest first, and in a tier the longest supporters
first. A supporter without a tier stands last, without one.

How they are named: as supporters-names.txt in this repository says. Its first setting is how a name is written when
nothing else is said for it:
    names: none               not named at all - the default: a name is only shown where the supporter agreed to it
    names: first-initial      Jane D. (the first name and the first letter of the last one)
    names: first              Jane
    names: full               Jane Doe (as Patreon has it)
and a line for one supporter changes that for them alone (their name as Patreon has it, any letter case):
    Jane Doe = JaneD          shown as JaneD
    John Smith = -            not shown
A name in About GT-Hub is public (this list is read by every GT-Hub), so it needs the supporter's yes: with "names: none"
only the supporters with a line of their own are named.
What GT-Hub takes: up to 48 characters, no | < > (those are left out here), a tier name up to 24.

The Patreon access: a Creator's Access Token with its Refresh Token and the client's id and secret (the Patreon
developer portal, "Clients & API Keys"), in the repository's secrets PATREON_ACCESS_TOKEN, PATREON_REFRESH_TOKEN,
PATREON_CLIENT_ID and PATREON_CLIENT_SECRET. Patreon's tokens run out after some weeks; where the access token is
refused, a new pair is asked for with the refresh token and kept in the secrets at once (the refresh token can be used
only once), with the GitHub CLI and SECRETS_TOKEN - a token of the repository's owner that may write its secrets.
No token is ever written to the log. Without the secrets nothing happens: Patreon is not connected yet.

Only the Python standard library (and gh for the secrets). Writes to GITHUB_OUTPUT: result=written|same|none, count=.
python3 patreon_supporters.py --test  checks the parts that do not need Patreon."""
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

LIST = "gt-hub-data.txt"
NAMES = "supporters-names.txt"
API = "https://www.patreon.com/api/oauth2/v2"
TOKEN_URL = "https://www.patreon.com/api/oauth2/token"
AGENT = "GT-Hub-Data supporters (+https://github.com/Gametism/GT-Hub-Data)"
STYLES = ("none", "first-initial", "first", "full")
HEADER = """[supporters]
; The supporters on Patreon, thanked by name in About GT-Hub (GT-Hub 0.11.58 and newer).
; Written by itself once a day from Patreon (.github/workflows/patreon-supporters.yml) - a name is changed or left
; out in supporters-names.txt, not here.
;   name | tier       the highest tier first, in a tier the longest supporters first
"""


def say(**what):
    out = os.environ.get("GITHUB_OUTPUT")
    text = "".join("%s=%s\n" % (k, str(v).replace("\n", " ")) for k, v in what.items())
    if out:
        with open(out, "a", encoding="utf-8") as f:
            f.write(text)
    else:
        sys.stdout.write(text)


def mask(value):
    if value and os.environ.get("GITHUB_ACTIONS"):
        print("::add-mask::" + value)


# ---- what GT-Hub takes (src/shared_list.h: [supporters], PlainText) ----

def clean(text, most):
    text = re.sub(r"\s", " ", text or "")
    text = "".join(c for c in text if c >= " " and c not in "|<>\x7f")
    text = re.sub(r"\s+", " ", text).strip()
    while len(text.encode("utf-8")) > most:   # (GT-Hub counts bytes: cut letters, never half of one)
        text = text[:-1].rstrip()
    return text


def shown_name(full, style):
    if style == "none":
        return ""
    words = clean(full, 200).split(" ")
    words = [w for w in words if w]
    if not words:
        return ""
    if style == "full" or len(words) == 1:
        return clean(" ".join(words), 48) if style == "full" else clean(words[0], 48)
    if style == "first":
        return clean(words[0], 48)
    return clean(words[0] + " " + words[-1][0].upper() + ".", 48)


def read_names(text):
    """supporters-names.txt: the style, and a name for a supporter (lower-case Patreon name -> shown name, "" not shown)."""
    style, names = "none", {}
    for raw in (text or "").splitlines():
        line = raw.strip()
        if not line or line.startswith(";") or line.startswith("#"):
            continue
        m = re.match(r"(?i)^names\s*:\s*(\S+)$", line)
        if m:
            if m.group(1).lower() in STYLES:
                style = m.group(1).lower()
            continue
        if "=" in line:
            who, shown = line.split("=", 1)
            who = re.sub(r"\s+", " ", who).strip().lower()
            shown = shown.strip()
            if who:
                names[who] = "" if shown == "-" else clean(shown, 48)
    return style, names


def supporters(pages, style="first-initial", names=None):
    """The members of all pages of /campaigns/{id}/members (with their tiers included), as (name, tier) in order."""
    names = names or {}
    tiers, members = {}, []
    for page in pages:
        for inc in page.get("included", []) or []:
            if inc.get("type") == "tier":
                a = inc.get("attributes") or {}
                tiers[inc.get("id")] = (clean(a.get("title"), 24), int(a.get("amount_cents") or 0))
        members.extend(page.get("data", []) or [])
    out = []
    for m in members:
        a = m.get("attributes") or {}
        if a.get("patron_status") != "active_patron":
            continue
        full = re.sub(r"\s+", " ", (a.get("full_name") or "").strip())
        key = full.lower()
        shown = names[key] if key in names else shown_name(full, style)
        if not shown:
            continue
        rel = ((m.get("relationships") or {}).get("currently_entitled_tiers") or {}).get("data") or []
        best = None
        for t in rel:
            tier = tiers.get(t.get("id"))
            if tier and (best is None or tier[1] > best[1]):
                best = tier
        title, amount = best if best else ("", -1)
        since = a.get("pledge_relationship_start") or "9999"
        out.append((-amount, since, shown.lower(), shown, title))
    out.sort()
    return [(shown, title) for _, _, _, shown, title in out]


def section(people):
    lines = [HEADER.rstrip("\n")]
    for name, tier in people:
        lines.append("%s | %s" % (name, tier) if tier else name)
    return "\n".join(lines) + "\n"


def with_section(listing, new):
    """gt-hub-data.txt with its [supporters] section replaced by `new` (added at the end where it has none)."""
    lines = listing.splitlines(keepends=True)
    start = next((i for i, l in enumerate(lines) if l.strip().lower() == "[supporters]"), None)
    if start is None:
        body = listing if listing.endswith("\n") or not listing else listing + "\n"
        return body + ("\n" if body and not body.endswith("\n\n") else "") + new
    end = next((i for i in range(start + 1, len(lines)) if lines[i].lstrip().startswith("[")), len(lines))
    tail = "".join(lines[end:])
    return "".join(lines[:start]) + new + ("\n" + tail if tail else "")


# ---- Patreon ----

class Refused(Exception):
    pass


def get(url, token):
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + token, "User-Agent": AGENT})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 401:
            raise Refused()
        raise SystemExit("Patreon answered %d for %s" % (e.code, url.split("?")[0]))


def fetch(token, campaign=None):
    if not campaign:
        found = get(API + "/campaigns?" + urllib.parse.urlencode({"fields[campaign]": "creation_name"}), token).get("data") or []
        if not found:
            raise SystemExit("This Patreon account has no campaign.")
        campaign = found[0]["id"]
    query = urllib.parse.urlencode({
        "include": "currently_entitled_tiers",
        "fields[member]": "full_name,patron_status,pledge_relationship_start",
        "fields[tier]": "title,amount_cents",
        "page[count]": "500",
    })
    url, pages = API + "/campaigns/%s/members?%s" % (campaign, query), []
    while url and len(pages) < 200:
        page = get(url, token)
        pages.append(page)
        url = ((page.get("links") or {}).get("next")) or None
    return pages


def refresh():
    body = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "refresh_token": os.environ["PATREON_REFRESH_TOKEN"],
        "client_id": os.environ["PATREON_CLIENT_ID"],
        "client_secret": os.environ["PATREON_CLIENT_SECRET"],
    }).encode()
    req = urllib.request.Request(TOKEN_URL, data=body, headers={"User-Agent": AGENT, "Content-Type": "application/x-www-form-urlencoded"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            got = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise SystemExit("Patreon did not give new tokens (%d). Make a new Creator's Access Token and Refresh Token in the Patreon "
                         "developer portal and put them into the secrets PATREON_ACCESS_TOKEN and PATREON_REFRESH_TOKEN." % e.code)
    access, again = got.get("access_token"), got.get("refresh_token")
    if not access or not again:
        raise SystemExit("Patreon's answer had no tokens.")
    mask(access)
    mask(again)
    # (Kept at once: the refresh token that was used is gone now.)
    env = dict(os.environ, GH_TOKEN=os.environ.get("SECRETS_TOKEN", ""))
    for name, value in (("PATREON_ACCESS_TOKEN", access), ("PATREON_REFRESH_TOKEN", again)):
        done = subprocess.run(["gh", "secret", "set", name, "--repo", os.environ.get("GITHUB_REPOSITORY", "Gametism/GT-Hub-Data")],
                              input=value.encode(), env=env, capture_output=True)
        if done.returncode:
            raise SystemExit("New Patreon tokens came, but %s could not be kept in the secrets (SECRETS_TOKEN missing or not allowed to "
                             "write them). Make a new token pair in the Patreon developer portal and check SECRETS_TOKEN." % name)
    print("Patreon's tokens were renewed and kept in the secrets.")
    return access


def main():
    token = os.environ.get("PATREON_ACCESS_TOKEN", "")
    if not token:
        print("Patreon is not connected yet (no PATREON_ACCESS_TOKEN secret) - nothing to do.")
        say(result="none", count=0)
        return
    mask(token)
    mask(os.environ.get("PATREON_REFRESH_TOKEN", ""))
    try:
        pages = fetch(token, os.environ.get("PATREON_CAMPAIGN_ID"))
    except Refused:
        if not all(os.environ.get(k) for k in ("PATREON_REFRESH_TOKEN", "PATREON_CLIENT_ID", "PATREON_CLIENT_SECRET")):
            raise SystemExit("Patreon refused the access token, and the secrets to renew it are missing.")
        try:
            pages = fetch(refresh(), os.environ.get("PATREON_CAMPAIGN_ID"))
        except Refused:
            raise SystemExit("Patreon refused the renewed token too.")
    style, names = read_names(open(NAMES, encoding="utf-8").read() if os.path.exists(NAMES) else "")
    people = supporters(pages, style, names)
    with open(LIST, encoding="utf-8") as f:
        before = f.read()
    after = with_section(before, section(people))
    print("%d supporter(s) on Patreon now (names: %s)." % (len(people), style))
    if after == before:
        say(result="same", count=len(people))
        return
    with open(LIST, "w", encoding="utf-8", newline="\n") as f:
        f.write(after)
    say(result="written", count=len(people))


def test():
    def page(members, tiers, nxt=None):
        return {"data": [{"type": "member", "id": str(i), "attributes": a, "relationships": {"currently_entitled_tiers": {"data": [{"type": "tier", "id": t} for t in ts]}}}
                         for i, (a, ts) in enumerate(members)],
                "included": [{"type": "tier", "id": k, "attributes": {"title": v[0], "amount_cents": v[1]}} for k, v in tiers.items()],
                "links": {"next": nxt} if nxt else {}}
    tiers = {"1": ("Supporter", 300), "2": ("Legend", 1500), "3": ("Hero", 700)}
    p1 = page([({"full_name": "Jane  Doe", "patron_status": "active_patron", "pledge_relationship_start": "2026-02-01"}, ["1"]),
               ({"full_name": "Max Mustermann", "patron_status": "active_patron", "pledge_relationship_start": "2026-01-01"}, ["1", "2"]),
               ({"full_name": "Former Fan", "patron_status": "former_patron"}, ["2"]),
               ({"full_name": "Declined Dan", "patron_status": "declined_patron"}, ["3"])], tiers)
    p2 = page([({"full_name": "Zoe <b>Bold</b> | Q", "patron_status": "active_patron", "pledge_relationship_start": "2025-12-01"}, ["1"]),
               ({"full_name": "Private Person", "patron_status": "active_patron"}, ["3"]),
               ({"full_name": "Free Follower", "patron_status": None}, []),
               ({"full_name": "Custom Amount", "patron_status": "active_patron"}, [])], tiers)
    style, names = read_names("; how names are written\nnames: first-initial\nprivate person = -\nJane Doe = JaneD\nnames: bogus\n")
    got = supporters([p1, p2], style, names)
    assert style == "first-initial", style
    assert got == [("Max M.", "Legend"), ("Zoe Q.", "Supporter"), ("JaneD", "Supporter"), ("Custom A.", "")], got
    assert supporters([p1, p2], "full")[:2] == [("Max Mustermann", "Legend"), ("Private Person", "Hero")]
    assert supporters([p1], "first") == [("Max", "Legend"), ("Jane", "Supporter")]
    # (with "names: none" only the supporters with a line of their own are named)
    style, names = read_names("names: none\nJane Doe = JaneD\n")
    assert style == "none" and supporters([p1, p2], style, names) == [("JaneD", "Supporter")]
    assert read_names("")[0] == "none" and shown_name("Max Mustermann", "none") == ""
    assert shown_name("Cher", "first-initial") == "Cher" and shown_name("  ", "full") == "" and len(clean("ä" * 40, 48).encode()) <= 48
    assert clean("A\tB|C<D>E\x01", 48) == "A BCDE"
    sec = section(got)
    assert sec.startswith("[supporters]\n;") and sec.endswith("Custom A.\n") and "Max M. | Legend\n" in sec
    base = "; list\n[hotfix]\nnvidia | 1 | - | - | https://www.nvidia.com/\n\n[supporters]\nOld | Gone\n\n[affinity]\nexe:a.exe | 8 | x\n"
    out = with_section(base, sec)
    assert "Old | Gone" not in out and "[affinity]\nexe:a.exe | 8 | x\n" in out and out.count("[supporters]") == 1 and out.startswith("; list\n[hotfix]")
    assert with_section(out, sec) == out
    added = with_section("[hotfix]\nnvidia | 1 | - | - | https://www.nvidia.com/\n", sec)
    assert added.endswith(sec) and "\n\n[supporters]" in added
    print("ok: supporters, names, the section and its place in the list")


if __name__ == "__main__":
    test() if "--test" in sys.argv else main()
