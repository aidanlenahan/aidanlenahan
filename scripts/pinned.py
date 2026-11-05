"""Builds img/pins/<repo>-light.svg and -dark.svg: cards styled like GitHub's pinned repositories.

Stars, forks, language and archive status come from the GitHub API on each run.
Descriptions come from DESCRIPTIONS below when set, otherwise from the repo itself.
"""
import json, os, urllib.request
from xml.sax.saxutils import escape

USER = "aidanlenahan"
TOKEN = os.environ["GITHUB_TOKEN"]

# Order matters: the README shows these two per row.
REPOS = ["gem", "pharmreach", "bucit", "secdiagdrop", "iogame", "cyberpatriot", "emmystrong", "rbrgymnastics"]

DESCRIPTIONS = {
    "gem": "PWA that gets friend group plans out of the group chat: private groups, events, RSVPs, and live updates.",
    "pharmreach": "HackRU 2026, built in 24 hours. Find which nearby pharmacies stock a medication, with price and location.",
    "bucit": "Ticketing and inventory for my high school's student Chromebook repair team. It replaced their paper tickets.",
    "secdiagdrop": "PowerShell upkeep for a nonprofit's shared PCs. Diagnostic uploads wait for my email approval.",
    "iogame": "Multiplayer territory game in the style of OpenFront: claim tiles, fight a bot, build cities and ports.",
    "cyberpatriot": "Windows and Linux hardening guides and scripts from my years as a CyberPatriot competitor.",
    "emmystrong": "Site for a nonprofit that helps people who need a bone marrow transplant find a donor match.",
    "rbrgymnastics": "Site and SEO for the nonprofit that funds Red Bank Regional's gymnastics team. Raised $2,400+ in a year.",
}

W, H, PAD = 400, 120, 16
FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"

THEMES = {
    "light": dict(bg="#ffffff", border="#d1d9e0", link="#0969da", muted="#59636e",
                  arch_fg="#9a6700", arch_border="#d4a72c"),
    "dark": dict(bg="#0d1117", border="#3d444d", link="#4493f8", muted="#9198a1",
                 arch_fg="#d29922", arch_border="#9e6a03"),
}

ICON_REPO = ("M2 2.5A2.5 2.5 0 0 1 4.5 0h8.75a.75.75 0 0 1 .75.75v12.5a.75.75 0 0 1-.75.75h-2.5a.75.75 0 0 1 0-1.5h1.75v-2h-8a1 1 0 0 0-.714 1.7.75.75 0 1 1-1.072 1.05A2.495 2.495 0 0 1 2 11.5Zm10.5-1h-8a1 1 0 0 0-1 1v6.708A2.486 2.486 0 0 1 4.5 9h8ZM5 12.25a.25.25 0 0 1 .25-.25h3.5a.25.25 0 0 1 .25.25v3.25a.25.25 0 0 1-.4.2l-1.45-1.087a.249.249 0 0 0-.3 0L5.4 15.7a.25.25 0 0 1-.4-.2Z")
ICON_STAR = ("M8 .25a.75.75 0 0 1 .673.418l1.882 3.815 4.21.612a.75.75 0 0 1 .416 1.279l-3.046 2.97.719 4.192a.751.751 0 0 1-1.088.791L8 12.347l-3.766 1.98a.75.75 0 0 1-1.088-.79l.72-4.194L.818 6.374a.75.75 0 0 1 .416-1.28l4.21-.611L7.327.668A.75.75 0 0 1 8 .25Zm0 2.445L6.615 5.5a.75.75 0 0 1-.564.41l-3.097.45 2.24 2.184a.75.75 0 0 1 .216.664l-.528 3.084 2.769-1.456a.75.75 0 0 1 .698 0l2.77 1.456-.53-3.084a.75.75 0 0 1 .216-.664l2.24-2.183-3.096-.45a.75.75 0 0 1-.564-.41L8 2.694Z")
ICON_FORK = ("M5 5.372v.878c0 .414.336.75.75.75h4.5a.75.75 0 0 0 .75-.75v-.878a2.25 2.25 0 1 1 1.5 0v.878a2.25 2.25 0 0 1-2.25 2.25h-1.5v2.128a2.251 2.251 0 1 1-1.5 0V8.5h-1.5A2.25 2.25 0 0 1 3.5 6.25v-.878a2.25 2.25 0 1 1 1.5 0ZM5 3.25a.75.75 0 1 0-1.5 0 .75.75 0 0 0 1.5 0Zm6.75.75a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5Zm-3 8.75a.75.75 0 1 0-1.5 0 .75.75 0 0 0 1.5 0Z")

# Rough Helvetica advance widths (fraction of font size), enough to wrap and place labels.
def text_width(s, size, bold=False):
    w = 0.0
    for ch in s:
        if ch in "il.,:;'|!jI ":
            w += 0.28
        elif ch in "frt()-/\"":
            w += 0.34
        elif ch in "mwMW":
            w += 0.86
        elif ch.isupper() or ch in "%&@":
            w += 0.68
        elif ch.isdigit() or ch in "$+":
            w += 0.56
        else:
            w += 0.54
    return w * size * (1.07 if bold else 1.0)

def wrap(text, size, width, max_lines=2):
    words, lines, cur = text.split(), [], ""
    for word in words:
        trial = f"{cur} {word}".strip()
        if text_width(trial, size) <= width:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    lines.append(cur)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        while text_width(lines[-1] + "...", size) > width:
            lines[-1] = lines[-1].rsplit(" ", 1)[0]
        lines[-1] += "..."
    return lines

def gql(query, variables):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as r:
        return json.load(r)["data"]

def card(repo, t):
    name = repo["name"]
    archived = repo["isArchived"]
    desc = DESCRIPTIONS.get(name) or repo["description"] or ""
    lang = repo["primaryLanguage"]
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT}">',
         f'<title>{escape(name)}</title>',
         f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="6" fill="{t["bg"]}" stroke="{t["border"]}"/>']
    # header: repo icon, name, visibility label
    o.append(f'<path transform="translate({PAD},{PAD + 2})" fill="{t["muted"]}" d="{ICON_REPO}"/>')
    nx = PAD + 16 + 8
    o.append(f'<text x="{nx}" y="{PAD + 14}" font-size="14" font-weight="600" fill="{t["link"]}">{escape(name)}</text>')
    label = "Public archive" if archived else "Public"
    lx = nx + text_width(name, 14, bold=True) + 8
    lw = text_width(label, 12) + 14
    lfg, lbd = (t["arch_fg"], t["arch_border"]) if archived else (t["muted"], t["border"])
    o.append(f'<rect x="{lx:.1f}" y="{PAD + 0.5}" width="{lw:.1f}" height="19" rx="9.5" fill="none" stroke="{lbd}"/>')
    o.append(f'<text x="{lx + 7:.1f}" y="{PAD + 14}" font-size="12" font-weight="500" fill="{lfg}">{label}</text>')
    # description
    for i, line in enumerate(wrap(desc, 12, W - 2 * PAD)):
        o.append(f'<text x="{PAD}" y="{PAD + 44 + i * 18}" font-size="12" fill="{t["muted"]}">{escape(line)}</text>')
    # footer: language, stars, forks (GitHub hides zero counts)
    fy, x = H - PAD - 2, PAD
    if lang:
        o.append(f'<circle cx="{x + 6}" cy="{fy - 4}" r="6" fill="{lang["color"] or "#8c959f"}" stroke="rgba(31,35,40,0.15)"/>')
        o.append(f'<text x="{x + 16}" y="{fy}" font-size="12" fill="{t["muted"]}">{escape(lang["name"])}</text>')
        x += 16 + text_width(lang["name"], 12) + 16
    for icon, count in ((ICON_STAR, repo["stargazerCount"]), (ICON_FORK, repo["forkCount"])):
        if count:
            o.append(f'<path transform="translate({x:.1f},{fy - 12})" fill="{t["muted"]}" d="{icon}"/>')
            o.append(f'<text x="{x + 20:.1f}" y="{fy}" font-size="12" fill="{t["muted"]}">{count:,}</text>')
            x += 20 + text_width(f"{count:,}", 12) + 16
    o.append("</svg>")
    return "\n".join(o)

fields = "name description isArchived stargazerCount forkCount primaryLanguage { name color }"
query = "query($u:String!){user(login:$u){" + " ".join(
    f'r{i}: repository(name:"{n}"){{ {fields} }}' for i, n in enumerate(REPOS)) + "}}"
data = gql(query, {"u": USER})["user"]

out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "img", "pins")
os.makedirs(out_dir, exist_ok=True)
for i, n in enumerate(REPOS):
    repo = data[f"r{i}"]
    for theme, colors in THEMES.items():
        with open(os.path.join(out_dir, f"{n}-{theme}.svg"), "w", encoding="utf-8", newline="\n") as f:
            f.write(card(repo, colors))
print(f"wrote {len(REPOS) * 2} cards")
