"""Builds the README header images.

img/avatar.svg              round headshot with a hairline ring, like GitHub's own avatar
img/stats-light.svg / -dark one-line stats strip styled like the profile's "followers" line
"""
import base64, json, os, urllib.request, datetime

USER = "aidanlenahan"
TOKEN = os.environ["GITHUB_TOKEN"]
FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"
HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "..", "img")

ICONS = {
    "commit": "M11.93 8.5a4.002 4.002 0 0 1-7.86 0H.75a.75.75 0 0 1 0-1.5h3.32a4.002 4.002 0 0 1 7.86 0h3.32a.75.75 0 0 1 0 1.5Zm-1.43-.75a2.5 2.5 0 1 0-5 0 2.5 2.5 0 0 0 5 0Z",
    "pr": "M1.5 3.25a2.25 2.25 0 1 1 3 2.122v5.256a2.251 2.251 0 1 1-1.5 0V5.372A2.25 2.25 0 0 1 1.5 3.25Zm5.677-.177L9.573.677A.25.25 0 0 1 10 .854V2.5h1A2.5 2.5 0 0 1 13.5 5v5.628a2.251 2.251 0 1 1-1.5 0V5a1 1 0 0 0-1-1h-1v1.646a.25.25 0 0 1-.427.177L7.177 3.427a.25.25 0 0 1 0-.354ZM3.75 2.5a.75.75 0 1 0 0 1.5.75.75 0 0 0 0-1.5Zm0 9.5a.75.75 0 1 0 0 1.5.75.75 0 0 0 0-1.5Zm8.25.75a.75.75 0 1 0 1.5 0 .75.75 0 0 0-1.5 0Z",
    "repo": "M2 2.5A2.5 2.5 0 0 1 4.5 0h8.75a.75.75 0 0 1 .75.75v12.5a.75.75 0 0 1-.75.75h-2.5a.75.75 0 0 1 0-1.5h1.75v-2h-8a1 1 0 0 0-.714 1.7.75.75 0 1 1-1.072 1.05A2.495 2.495 0 0 1 2 11.5Zm10.5-1h-8a1 1 0 0 0-1 1v6.708A2.486 2.486 0 0 1 4.5 9h8ZM5 12.25a.25.25 0 0 1 .25-.25h3.5a.25.25 0 0 1 .25.25v3.25a.25.25 0 0 1-.4.2l-1.45-1.087a.249.249 0 0 0-.3 0L5.4 15.7a.25.25 0 0 1-.4-.2Z",
    "star": "M8 .25a.75.75 0 0 1 .673.418l1.882 3.815 4.21.612a.75.75 0 0 1 .416 1.279l-3.046 2.97.719 4.192a.751.751 0 0 1-1.088.791L8 12.347l-3.766 1.98a.75.75 0 0 1-1.088-.79l.72-4.194L.818 6.374a.75.75 0 0 1 .416-1.28l4.21-.611L7.327.668A.75.75 0 0 1 8 .25Zm0 2.445L6.615 5.5a.75.75 0 0 1-.564.41l-3.097.45 2.24 2.184a.75.75 0 0 1 .216.664l-.528 3.084 2.769-1.456a.75.75 0 0 1 .698 0l2.77 1.456-.53-3.084a.75.75 0 0 1 .216-.664l2.24-2.183-3.096-.45a.75.75 0 0 1-.564-.41L8 2.694Z",
}

def gql(query, variables):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as r:
        return json.load(r)["data"]

def text_width(s, size, bold=False):
    w = 0.0
    for ch in s:
        if ch in "il.,:;'|!jI ()":
            w += 0.28
        elif ch in "frt-/":
            w += 0.34
        elif ch in "mwMW":
            w += 0.86
        elif ch.isupper():
            w += 0.68
        elif ch.isdigit():
            w += 0.56
        else:
            w += 0.54
    return w * size * (1.07 if bold else 1.0)

year = datetime.date.today().year
d = gql("""query($u:String!,$from:DateTime!){user(login:$u){
  repositories(ownerAffiliations:OWNER,privacy:PUBLIC,first:100){totalCount nodes{stargazerCount}}
  pullRequests{totalCount}
  contributionsCollection(from:$from){totalCommitContributions restrictedContributionsCount}
}}""", {"u": USER, "from": f"{year}-01-01T00:00:00Z"})["user"]
c = d["contributionsCollection"]
stats = [
    ("commit", c["totalCommitContributions"] + c["restrictedContributionsCount"], f"commits in {year}"),
    ("pr", d["pullRequests"]["totalCount"], "pull requests"),
    ("repo", d["repositories"]["totalCount"], "public repos"),
    ("star", sum(n["stargazerCount"] for n in d["repositories"]["nodes"]), "stars"),
]

# Avatar: GitHub draws avatars as circles with a 1px translucent ring.
S = 160
photo = base64.b64encode(open(os.path.join(IMG, "headshot.webp"), "rb").read()).decode()
with open(os.path.join(IMG, "avatar.svg"), "w", encoding="utf-8", newline="\n") as f:
    f.write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{S}" height="{S}" viewBox="0 0 {S} {S}">\n'
            f'<title>Aidan Lenahan</title>\n'
            f'<clipPath id="c"><circle cx="{S/2}" cy="{S/2}" r="{S/2}"/></clipPath>\n'
            f'<image href="data:image/webp;base64,{photo}" width="{S}" height="{S}" clip-path="url(#c)"/>\n'
            f'<circle cx="{S/2}" cy="{S/2}" r="{S/2 - 0.5}" fill="none" stroke="rgba(128,128,128,0.25)"/>\n'
            f'</svg>\n')

# Stats strip: icon, bold number, muted label, separated by middle dots.
SIZE, GAP, H = 14, 6, 20
def strip(fg, muted):
    parts, x = [], 0.0
    for i, (icon, n, label) in enumerate(stats):
        if i:
            parts.append(f'<text x="{x + 6:.1f}" y="15" font-size="{SIZE}" fill="{muted}">&#183;</text>')
            x += 6 + text_width(".", SIZE) + 8
        parts.append(f'<path transform="translate({x:.1f},2)" fill="{muted}" d="{ICONS[icon]}"/>')
        x += 16 + GAP
        num = f"{n:,}"
        # One text run, so the renderer places the label right after the number.
        parts.append(f'<text x="{x:.1f}" y="15" font-size="{SIZE}" fill="{muted}">'
                     f'<tspan font-weight="600" fill="{fg}">{num}</tspan> {label}</text>')
        x += text_width(f"{num} {label}", SIZE)
    w = int(x + 4)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{H}" viewBox="0 0 {w} {H}" font-family="{FONT}">\n'
            f'<title>GitHub stats</title>\n' + "\n".join(parts) + "\n</svg>\n")

for name, colors in {"light": ("#1f2328", "#59636e"), "dark": ("#f0f6fc", "#9198a1")}.items():
    with open(os.path.join(IMG, f"stats-{name}.svg"), "w", encoding="utf-8", newline="\n") as f:
        f.write(strip(*colors))
print("wrote avatar.svg, stats-light.svg, stats-dark.svg")
