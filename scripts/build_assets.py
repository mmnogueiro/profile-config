#!/usr/bin/env python3
"""Generate assets/stack.svg, assets/journey.svg and assets/divider.svg.

Edit the STACK and JOURNEY lists below, then run:
    python scripts/build_assets.py
Only the Python standard library is needed.
"""
from pathlib import Path
from html import escape

OUT = Path(__file__).resolve().parent.parent / "assets"

ACCENT = "#4ade80"
BG = "#0a0d0b"
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"

# ---------------------------------------------------------------- data
STACK = [
    ("// build", "#60a5fa", [
        "Java", "Python", "C", "JavaScript", "PHP", "HTML & CSS",
        "SQL", "MySQL", "Supabase", "Docker", "Git", "Linux",
    ]),
    ("// break", ACCENT, [
        "Nmap", "Wireshark", "Burp Suite", "Metasploit", "Kali Linux", "TryHackMe",
    ]),
]

# (year, title, line 1, line 2, done?)
JOURNEY = [
    ("2023", "ViaTecla", "web dev internship", "CMS & portals", True),
    ("2024", "NOVA FCT", "CSE degree", "joins n.inf", True),
    ("2025", "Clip a Room", "Fraqtory · PHP/MySQL", "n.inf projects lead", True),
    ("2026", "TryHackMe", "SEC0 · 540/600", "SEC1 · 550/700", True),
    ("next", "CTFs", "HackTheBox", "picoCTF", False),
]

# ---------------------------------------------------------------- helpers
W = 900
CHAR = 0.6  # monospace advance, in em


def tw(text, size):
    return round(len(text) * CHAR * size, 1)


def frame(h, body, label, extra_style=""):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img" aria-label="{escape(label)}">
<style>
  text{{font-family:{MONO}}}
  .in{{opacity:0;animation:in .6s cubic-bezier(.2,.8,.2,1) forwards}}
  @keyframes in{{from{{opacity:0;transform:translateY(6px)}}to{{opacity:1;transform:none}}}}
  {extra_style}
  @media (prefers-reduced-motion:reduce){{*{{animation:none!important}}.in{{opacity:1}}}}
</style>
<rect x=".5" y=".5" width="{W-1}" height="{h-1}" rx="13.5" fill="{BG}" stroke="#ffffff" stroke-opacity=".1"/>
{body}
</svg>
"""


# ---------------------------------------------------------------- stack
def build_stack():
    pad, label_w, size, chip_h, gap = 28, 104, 13, 32, 8
    y = 26
    parts, delay = [], 0.15
    for label, color, items in STACK:
        parts.append(f'<text x="{pad}" y="{y+21}" font-size="13" fill="{color}" fill-opacity=".9">{escape(label)}</text>')
        x = pad + label_w
        for item in items:
            w = tw(item, size) + 40
            if x + w > W - pad:
                x = pad + label_w
                y += chip_h + gap
            parts.append(
                f'<g transform="translate({x:.1f} {y})"><g class="in" style="animation-delay:{delay:.2f}s">'
                f'<rect width="{w:.1f}" height="{chip_h}" rx="7" fill="#ffffff" fill-opacity=".03" stroke="#ffffff" stroke-opacity=".12"/>'
                f'<circle cx="14" cy="16" r="3" fill="{color}"/>'
                f'<text x="25" y="20.5" font-size="{size}" fill="#e5e7eb" textLength="{tw(item, size)}">{escape(item)}</text></g></g>'
            )
            x += w + gap
            delay += 0.04
        y += chip_h + 18
    h = y + 8
    label = "Tech stack. Build: " + ", ".join(STACK[0][2]) + ". Break: " + ", ".join(STACK[1][2]) + "."
    (OUT / "stack.svg").write_text(frame(h, "\n".join(parts), label))


# ---------------------------------------------------------------- journey
def build_journey():
    h, line_y, pad = 190, 74, 90
    n = len(JOURNEY)
    step = (W - 2 * pad) / (n - 1)
    xs = [pad + i * step for i in range(n)]
    last_done = max(i for i, j in enumerate(JOURNEY) if j[4])
    solid_len = xs[last_done] - xs[0]
    parts = [
        f'<line x1="{xs[0]}" y1="{line_y}" x2="{xs[-1]}" y2="{line_y}" stroke="#ffffff" stroke-opacity=".12" stroke-dasharray="4 6"/>',
        f'<line class="draw" x1="{xs[0]}" y1="{line_y}" x2="{xs[last_done]}" y2="{line_y}" stroke="{ACCENT}" stroke-width="2" '
        f'stroke-dasharray="{solid_len:.0f}" stroke-dashoffset="{solid_len:.0f}"/>',
    ]
    for i, (year, title, l1, l2, done) in enumerate(JOURNEY):
        x, d = xs[i], 0.3 + i * 0.35
        node = (f'<circle cx="{x}" cy="{line_y}" r="7" fill="{BG}" stroke="{ACCENT}" stroke-width="2"/>'
                f'<circle cx="{x}" cy="{line_y}" r="3" fill="{ACCENT}"/>') if done else (
                f'<circle class="pulse" cx="{x}" cy="{line_y}" r="7" fill="{BG}" stroke="#9ca3af" stroke-width="1.5" stroke-dasharray="3 3"/>')
        parts.append(
            f'<g class="in" style="animation-delay:{d:.2f}s">'
            f'<text x="{x}" y="42" font-size="12" text-anchor="middle" fill="{ACCENT if done else "#9ca3af"}">{escape(year)}</text>'
            f'{node}'
            f'<text x="{x}" y="112" font-size="15" font-weight="700" text-anchor="middle" fill="{"#f3f4f6" if done else "#9ca3af"}">{escape(title)}</text>'
            f'<text x="{x}" y="136" font-size="12" text-anchor="middle" fill="#9ca3af">{escape(l1)}</text>'
            f'<text x="{x}" y="156" font-size="12" text-anchor="middle" fill="#6b7280">{escape(l2)}</text></g>'
        )
    style = (".draw{animation:draw 1.8s ease-out .3s forwards}@keyframes draw{to{stroke-dashoffset:0}}"
             ".pulse{animation:pulse 2.4s ease-in-out infinite}@keyframes pulse{50%{stroke-opacity:.3}}")
    label = "Journey: " + "; ".join(f"{y} {t} — {a}, {b}" for y, t, a, b, _ in JOURNEY)
    (OUT / "journey.svg").write_text(frame(h, "\n".join(parts), label, style))


# ---------------------------------------------------------------- divider
def build_divider():
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="24" viewBox="0 0 {W} 24" role="presentation">
<style>.p{{animation:p 5s ease-in-out infinite alternate}}@keyframes p{{to{{transform:translateX(744px)}}}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}</style>
<line x1="72" y1="12" x2="828" y2="12" stroke="#808080" stroke-opacity=".35" stroke-dasharray="2 6" stroke-linecap="round"/>
<rect x="66" y="9" width="6" height="6" rx="1" fill="#808080" fill-opacity=".6"/>
<rect x="828" y="9" width="6" height="6" rx="1" fill="#808080" fill-opacity=".6"/>
<g class="p"><rect x="74" y="10" width="34" height="4" rx="2" fill="{ACCENT}" fill-opacity=".85"/></g>
</svg>
"""
    (OUT / "divider.svg").write_text(svg)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    build_stack()
    build_journey()
    build_divider()
    print("assets written to", OUT)
