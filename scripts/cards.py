"""Draw project cards for the profile README.

Runs daily in .github/workflows/snake.yml and publishes to the `output` branch
together with the snake, so star counts stay current without a third-party
card service (the hosted pin cards clip non-Latin descriptions).
"""
import json
import os
import sys
import urllib.request
from xml.sax.saxutils import escape

USER = "wilgon456"

# repo, title, English line, Korean line
PROJECTS = [
    ("orca-agent-cleanup", "Orca Agent Cleanup",
     "Audit and recoverably quarantine leftover agent skills, hooks and CLI residue.",
     "Orca가 남긴 에이전트 스킬·훅·CLI 찌꺼기를 찾아 되돌릴 수 있게 격리합니다."),
    ("Paseobility", "Paseobility",
     "Reusable Paseo skills for browsers, projects, artifacts and connected computers.",
     "브라우저·프로젝트·산출물·연결된 컴퓨터를 다루는 Paseo 스킬 묶음입니다."),
    ("ai_cli_auto_manager", "AI CLI Auto Manager",
     "Keeps AI coding CLIs updated on a schedule and cleans what they leave behind.",
     "AI 코딩 CLI를 정해진 때 안전하게 업데이트하고 남은 찌꺼기를 치웁니다."),
    ("Hermes_Auto_Update", "Hermes Auto Update",
     "Daily upstream updates for Hermes Agent while keeping local customizations.",
     "Hermes Agent 새 판과 공식 스킬을 매일 반영하고 내 설정은 지킵니다."),
    ("claude_xuck", "Plain Korean Replies",
     "A Claude Code plugin that makes Korean answers short and plain.",
     "Claude Code가 한국어로 답할 때 짧고 평범한 문장으로 쓰게 하는 플러그인입니다."),
    ("xuck_hancom_pdf", "Hancom PDF Fix",
     "Turns off Hancom's 'open after saving PDF' box for good. One double-click.",
     "한글에서 PDF 저장 뒤 열기 체크를 꺼서 고정합니다. 더블클릭 한 번이면 끝."),
]

LANG_COLORS = {"JavaScript": "#f1e05a", "TypeScript": "#3178c6", "Python": "#3572A5",
               "PowerShell": "#4ea1ff", "Rust": "#dea584", "Shell": "#89e051"}

W, H = 400, 132
FONT = "'Segoe UI', 'Apple SD Gothic Neo', 'Noto Sans KR', Ubuntu, sans-serif"


def text_width(s, size):
    """Rough advance width: Hangul and other wide glyphs take a full em."""
    return sum(size * (1.0 if ord(c) > 0x2E80 else 0.56 if c != " " else 0.3) for c in s)


def wrap(s, size, width, max_lines=2):
    lines, cur = [], ""
    for word in s.split(" "):
        trial = (cur + " " + word).strip()
        if text_width(trial, size) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    lines.append(cur)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1].rstrip(".") + "…"
    return lines


def fetch(repo):
    req = urllib.request.Request(f"https://api.github.com/repos/{USER}/{repo}")
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=20) as r:
        d = json.load(r)
    return d.get("stargazers_count", 0), d.get("forks_count", 0), d.get("language") or ""


def card(title, desc, stars, forks, lang):
    lines = wrap(desc, 13, W - 50)
    desc_svg = "".join(
        f'<text x="25" y="{70 + i * 19}" class="d">{escape(l)}</text>' for i, l in enumerate(lines))
    x = 25
    meta = ""
    if lang:
        meta += (f'<circle cx="{x + 6}" cy="110" r="6" fill="{LANG_COLORS.get(lang, "#a9b1d6")}"/>'
                 f'<text x="{x + 18}" y="114" class="m">{escape(lang)}</text>')
        x += 30 + int(text_width(lang, 12))
    meta += f'<text x="{x}" y="114" class="m">★ {stars}</text>'
    x += 30 + int(text_width(str(stars), 12))
    if forks:
        meta += f'<text x="{x}" y="114" class="m">⑂ {forks}</text>'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{escape(title)}">
<style>
.t{{font:600 17px {FONT};fill:#70a5fd}}
.d{{font:400 13px {FONT};fill:#c0caf5}}
.m{{font:400 12px {FONT};fill:#a9b1d6}}
.c{{animation:in .6s ease-out both}}
@keyframes in{{from{{opacity:0;transform:translateY(6px)}}to{{opacity:1;transform:none}}}}
</style>
<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#1d4ed8"/><stop offset="1" stop-color="#38bdf8"/></linearGradient></defs>
<rect width="{W}" height="{H}" rx="12" fill="#1a1b27"/>
<rect width="{W}" height="4" rx="2" fill="url(#g)"/>
<g class="c">
<text x="25" y="40" class="t">{escape(title)}</text>
{desc_svg}
{meta}
</g>
</svg>
'''


def main(out):
    os.makedirs(os.path.join(out, "cards"), exist_ok=True)
    for repo, title, en, ko in PROJECTS:
        stars, forks, lang = fetch(repo)
        for suffix, desc in (("", en), (".ko", ko)):
            path = os.path.join(out, "cards", f"{repo}{suffix}.svg")
            with open(path, "w", encoding="utf-8") as f:
                f.write(card(title, desc, stars, forks, lang))
    print(f"wrote {len(PROJECTS) * 2} cards to {out}/cards")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "dist")
