"""Builds img/sidebar-light.svg and img/sidebar-dark.svg: headshot with GitHub stats below it."""
import base64, json, os, urllib.request, datetime

USER = "aidanlenahan"
TOKEN = os.environ["GITHUB_TOKEN"]
W = 150

def gql(query, variables):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as r:
        return json.load(r)["data"]

year = datetime.date.today().year
d = gql("""query($u:String!,$from:DateTime!){user(login:$u){
  repositories(ownerAffiliations:OWNER,privacy:PUBLIC,first:100){totalCount nodes{stargazerCount}}
  pullRequests{totalCount}
  contributionsCollection(from:$from){totalCommitContributions restrictedContributionsCount}
}}""", {"u": USER, "from": f"{year}-01-01T00:00:00Z"})["user"]

c = d["contributionsCollection"]
rows = [
    (f"Commits ({year})", c["totalCommitContributions"] + c["restrictedContributionsCount"]),
    ("Pull requests", d["pullRequests"]["totalCount"]),
    ("Public repos", d["repositories"]["totalCount"]),
    ("Stars", sum(n["stargazerCount"] for n in d["repositories"]["nodes"])),
]

here = os.path.dirname(os.path.abspath(__file__))
photo = base64.b64encode(open(os.path.join(here, "..", "img", "headshot.webp"), "rb").read()).decode()

def svg(fg, muted, line):
    top = W + 14
    h = top + len(rows) * 22
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" font-family="-apple-system,Segoe UI,Helvetica,Arial,sans-serif">',
           f'<clipPath id="c"><rect width="{W}" height="{W}" rx="10"/></clipPath>',
           f'<image href="data:image/webp;base64,{photo}" width="{W}" height="{W}" clip-path="url(#c)"/>']
    for i, (label, val) in enumerate(rows):
        y = top + i * 22 + 12
        out.append(f'<text x="0" y="{y}" font-size="12" fill="{muted}">{label}</text>')
        out.append(f'<text x="{W}" y="{y}" font-size="12" font-weight="600" fill="{fg}" text-anchor="end">{val:,}</text>')
        if i < len(rows) - 1:
            out.append(f'<line x1="0" x2="{W}" y1="{y + 7}" y2="{y + 7}" stroke="{line}"/>')
    out.append("</svg>")
    return "\n".join(out)

for name, colors in {"light": ("#1f2328", "#59636e", "#d1d9e0"), "dark": ("#f0f6fc", "#9198a1", "#3d444d")}.items():
    with open(os.path.join(here, "..", "img", f"sidebar-{name}.svg"), "w", encoding="utf-8", newline="\n") as f:
        f.write(svg(*colors))
