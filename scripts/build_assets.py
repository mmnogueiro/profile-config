#!/usr/bin/env python3
"""Generate the SVG assets (stack, certs, journey, divider).

Edit the data lists below, then run:
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
        "Java", "Python", "C", "JavaScript", "PHP", "TypeScript",
        "HTML & CSS", "Bootstrap", "Node.js", "Express", "React",
        "Flask", "Pandas", "Selenium", "BeautifulSoup",
        "SQL", "MySQL", "PostgreSQL", "SQLite", "Supabase",
        "Docker", "Git", "Bash",
    ]),
    ("// break", ACCENT, [
        "Nmap", "Wireshark", "Burp Suite", "Metasploit", "Gobuster", "Hydra",
        "John the Ripper", "Hashcat", "Netcat", "CyberChef", "Linux", "Windows",
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

# (name, issuer, score, max) — use None, None when there is no score
CERTS = [
    ("SEC0", "TryHackMe", 540, 600),
    ("SEC1", "TryHackMe", 550, 700),
    ("Full-Stack Web Dev Bootcamp", "Udemy", None, None),
    ("100 Days of Code: Python", "Udemy", None, None),
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
def scramble(text, seed):
    """Deterministic gibberish of the same length (spaces kept)."""
    glyphs = "01#$%&@!?<>/\\*+=~^"
    out, n = [], seed
    for ch in text:
        n = (n * 1103515245 + 12345) & 0x7FFFFFFF
        out.append(" " if ch == " " else glyphs[n % len(glyphs)])
    return "".join(out)


def build_stack():
    """Static grid; a scanner beam sweeps across on a loop and every chip it hits 'decrypts'."""
    pad, label_w, size, chip_h, gap = 28, 104, 13, 32, 8
    T, sweep, start = 8.0, 2.6, 1.0           # loop period, beam travel time, first pass
    x0, x1 = pad + label_w, W - pad
    y = 26
    chips, labels, k = [], [], 0
    for c, (label, color, items) in enumerate(STACK):
        labels.append(f'<text class="in" style="animation-delay:{0.1 + c * 0.15:.2f}s" x="{pad}" y="{y+21}" '
                      f'font-size="13" fill="{color}" fill-opacity=".9">{escape(label)}</text>')
        x = x0
        for item in items:
            tl = tw(item, size)
            w = tl + 40
            if x + w > x1:
                x, y = x0, y + chip_h + gap
            hit = start + (x + w / 2 - x0) / (x1 - x0) * sweep
            dl = f"animation-delay:{hit:.2f}s"
            txt = lambda s, cls, extra="": (f'<text class="{cls}" style="{dl}" x="25" y="20.5" font-size="{size}" '
                                            f'fill="{extra or "#e5e7eb"}" textLength="{tl}">{escape(s)}</text>')
            chips.append(
                f'<g transform="translate({x:.1f} {y})"><g class="in" style="animation-delay:{0.15 + k * 0.02:.2f}s">'
                f'<rect width="{w:.1f}" height="{chip_h}" rx="7" fill="#ffffff" fill-opacity=".03" stroke="#ffffff" stroke-opacity=".12"/>'
                f'<rect class="hl" style="{dl}" width="{w:.1f}" height="{chip_h}" rx="7" fill="{color}" fill-opacity=".08" stroke="{color}"/>'
                f'<circle cx="14" cy="16" r="3" fill="{color}"/>'
                f'<circle class="ping" style="{dl}" cx="14" cy="16" r="3" fill="none" stroke="{color}"/>'
                + txt(item, "rt")
                + txt(scramble(item, k * 3 + 1), "s1", color)
                + txt(scramble(item, k * 3 + 2), "s2", color)
                + txt(scramble(item, k * 3 + 3), "s3", color)
                + '</g></g>'
            )
            x += w + gap
            k += 1
        y += chip_h + 18
    h = y + 8
    top, bot = 14, h - 14
    beam = (f'<g class="beam" style="animation-delay:{start:.2f}s">'
            f'<rect x="-70" y="{top}" width="70" height="{bot - top}" fill="url(#trail)"/>'
            f'<rect x="-1" y="{top}" width="2" height="{bot - top}" rx="1" fill="{ACCENT}" filter="url(#glow)"/></g>')
    defs = ('<defs><linearGradient id="trail" x1="0" x2="1">'
            f'<stop offset="0" stop-color="{ACCENT}" stop-opacity="0"/><stop offset="1" stop-color="{ACCENT}" stop-opacity=".14"/></linearGradient>'
            '<filter id="glow" x="-400%" y="-5%" width="900%" height="110%"><feGaussianBlur stdDeviation="2.5" result="b"/>'
            '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
            f'<clipPath id="area"><rect x="{x0 - 8}" y="0" width="{x1 - x0 + 16}" height="{h}"/></clipPath></defs>')
    p = lambda sec: f"{sec / T * 100:.2f}%"   # seconds -> keyframe percent
    s_end = p(sweep)
    style = (
        f".beam{{opacity:0;animation:beam {T}s linear infinite}}"
        f"@keyframes beam{{0%{{opacity:1;transform:translateX({x0 - 8}px)}}{s_end}{{opacity:1;transform:translateX({x1 + 8}px)}}"
        f"{p(sweep + .01)},100%{{opacity:0;transform:translateX({x1 + 8}px)}}}}"
        f".hl{{opacity:0;animation:hl {T}s ease-out infinite}}@keyframes hl{{0%{{opacity:1}}{p(1.2)},100%{{opacity:0}}}}"
        f".ping{{opacity:0;transform-box:fill-box;transform-origin:center;animation:ping {T}s ease-out infinite}}"
        f"@keyframes ping{{0%{{opacity:1;transform:scale(1)}}{p(.7)},100%{{opacity:0;transform:scale(3.2)}}}}"
        f".rt{{animation:rt {T}s steps(1) infinite}}@keyframes rt{{0%{{opacity:0}}{p(.36)},100%{{opacity:1}}}}"
        f".s1,.s2,.s3{{opacity:0;animation:{T}s steps(1) infinite}}"
        f".s1{{animation-name:s1}}@keyframes s1{{0%{{opacity:1}}{p(.12)},100%{{opacity:0}}}}"
        f".s2{{animation-name:s2}}@keyframes s2{{0%{{opacity:0}}{p(.12)}{{opacity:1}}{p(.24)},100%{{opacity:0}}}}"
        f".s3{{animation-name:s3}}@keyframes s3{{0%{{opacity:0}}{p(.24)}{{opacity:1}}{p(.36)},100%{{opacity:0}}}}"
        "@media (prefers-reduced-motion:reduce){.beam,.hl,.ping,.s1,.s2,.s3{opacity:0!important}.rt{opacity:1!important}}"
    )
    body = defs + "\n" + "\n".join(labels) + "\n" + "\n".join(chips) + f'\n<g clip-path="url(#area)">{beam}</g>'
    label = "Tech stack. " + ". ".join(f"{l.strip('/ ').capitalize()}: " + ", ".join(i) for l, _, i in STACK) + "."
    (OUT / "stack.svg").write_text(frame(h, body, label, style), encoding="utf-8")


# ---------------------------------------------------------------- certs
ISSUER_COLOR = {"TryHackMe": ACCENT, "Udemy": "#a78bfa"}


def build_certs():
    pad, gap, card_h, cols = 24, 16, 104, 2
    card_w = (W - 2 * pad - gap * (cols - 1)) / cols
    parts = []
    rows = -(-len(CERTS) // cols)
    for i, (name, issuer, score, top) in enumerate(CERTS):
        r, c = divmod(i, cols)
        last_alone = i == len(CERTS) - 1 and len(CERTS) % cols
        w = W - 2 * pad if last_alone else card_w
        x, y = pad + c * (card_w + gap), pad + r * (card_h + gap)
        d = 0.15 + i * 0.15
        color = ISSUER_COLOR.get(issuer, ACCENT)
        bar_w = w - 48
        pct = score / top if score is not None else 1
        shield = ('<path d="M0-11L9-7.5V-1C9 5 5 9.5 0 11C-5 9.5-9 5-9-1V-7.5Z" '
                  f'fill="{color}" fill-opacity=".12" stroke="{color}" stroke-width="1.4"/>'
                  f'<path d="M-3.6 0L-1 2.6L4 -2.6" fill="none" stroke="{color}" stroke-width="1.6" '
                  'stroke-linecap="round" stroke-linejoin="round"/>')
        if score is not None:
            right = (f'<text x="{w-24:.1f}" y="36" font-size="15" font-weight="700" text-anchor="end" fill="{color}">{score}'
                     f'<tspan fill="#6b7280" font-weight="400">/{top}</tspan></text>'
                     f'<text x="{w-24:.1f}" y="54" font-size="12" text-anchor="end" fill="#6b7280">{pct:.0%}</text>')
        else:
            right = f'<text x="{w-24:.1f}" y="36" font-size="12" text-anchor="end" fill="{color}">completed</text>'
        parts.append(
            f'<g transform="translate({x:.1f} {y})"><g class="in" style="animation-delay:{d:.2f}s">'
            f'<rect width="{w:.1f}" height="{card_h}" rx="10" fill="#ffffff" fill-opacity=".03" stroke="#ffffff" stroke-opacity=".12"/>'
            f'<g transform="translate(36 38)">{shield}</g>'
            f'<text x="60" y="36" font-size="16" font-weight="700" fill="#f3f4f6">{escape(name)}</text>'
            f'<text x="60" y="54" font-size="12" fill="#9ca3af">{escape(issuer)}</text>{right}'
            f'<rect x="24" y="74" width="{bar_w:.1f}" height="6" rx="3" fill="#ffffff" fill-opacity=".08"/>'
            f'<rect class="bar" x="24" y="74" width="{bar_w * pct:.1f}" height="6" rx="3" fill="{color}" '
            f'style="animation-delay:{d + 0.3:.2f}s"/></g></g>'
        )
    h = pad * 2 + rows * card_h + (rows - 1) * gap
    style = (".bar{transform-box:fill-box;transform:scaleX(0);animation:bar 1.2s cubic-bezier(.2,.8,.2,1) forwards}"
             "@keyframes bar{to{transform:scaleX(1)}}"
             "@media (prefers-reduced-motion:reduce){.bar{transform:none}}")
    label = "Certifications: " + "; ".join(
        f"{n} by {iss}" + (f", {s}/{t}" if s is not None else ", completed") for n, iss, s, t in CERTS)
    (OUT / "certs.svg").write_text(frame(h, "\n".join(parts), label, style), encoding="utf-8")


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
    (OUT / "journey.svg").write_text(frame(h, "\n".join(parts), label, style), encoding="utf-8")


# ---------------------------------------------------------------- divider
def build_divider():
    """Man-in-the-middle: packets leave clean (blue) and come out of the attacker tampered (red)."""
    blue, light, red = "#367bf0", "#a9c9ff", "#ef4444"
    clean = (f'<g><rect x="-11" y="-6" width="22" height="12" rx="3.5" fill="#1d3a6b" stroke="#6aa8ff"/>'
             f'<path d="M-2.2 0V-1.6a2.2 2.2 0 0 1 4.4 0V0" fill="none" stroke="{light}" stroke-width="1.1"/>'
             f'<rect x="-3.2" y="0" width="6.4" height="3.6" rx=".8" fill="{light}"/></g>')
    tampered = (f'<g><rect x="-11" y="-6" width="22" height="12" rx="3.5" fill="#4a1218" stroke="{red}" filter="url(#neon)"/>'
                f'<path d="M-2.2 -.6V-2.8a2.2 2.2 0 0 1 4.4 0" fill="none" stroke="#fca5a5" stroke-width="1.1"/>'
                f'<rect x="-3.2" y="0" width="6.4" height="3.6" rx=".8" fill="#fca5a5"/></g>')
    skull = (f'<path d="M0-6.2C-3.6-6.2-5.4-3.6-5.4-.8C-5.4 1.2-4.4 2.4-3.2 3V5H3.2V3C4.4 2.4 5.4 1.2 5.4-.8C5.4-3.6 3.6-6.2 0-6.2Z" fill="{red}"/>'
             '<ellipse cx="-2.1" cy="-.6" rx="1.45" ry="1.6" fill="#0d1017"/><ellipse cx="2.1" cy="-.6" rx="1.45" ry="1.6" fill="#0d1017"/>'
             '<path d="M0 1.1L-.8 2.5H.8Z" fill="#0d1017"/><path d="M-1.6 3.4V5M0 3.4V5M1.6 3.4V5" stroke="#0d1017" stroke-width=".55"/>')
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="44" viewBox="0 0 {W} 44" role="presentation">
<defs><clipPath id="L"><rect width="450" height="44"/></clipPath><clipPath id="R"><rect x="450" width="450" height="44"/></clipPath>
<filter id="neon" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="1.4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
<style>
  .fw{{animation:fw 4s linear infinite}}@keyframes fw{{from{{transform:translateX(100px)}}to{{transform:translateX(800px)}}}}
  .bw{{animation:bw 4s linear 2s infinite;transform:translateX(800px)}}@keyframes bw{{from{{transform:translateX(800px)}}to{{transform:translateX(100px)}}}}
  .tap{{transform-origin:450px 22px;animation:tap 2s ease-out infinite}}@keyframes tap{{0%{{transform:scale(.6);opacity:.9}}60%,100%{{transform:scale(1.8);opacity:0}}}}
  @media (prefers-reduced-motion:reduce){{*{{animation:none!important}}.bw{{display:none}}.fw{{transform:translateX(250px)}}}}
</style>
<!-- wire -->
<line x1="84" y1="22" x2="816" y2="22" stroke="#808080" stroke-opacity=".35" stroke-dasharray="2 6" stroke-linecap="round"/>
<!-- client (laptop) -->
<g fill="none" stroke="{light}" stroke-width="1.4" stroke-linejoin="round">
  <rect x="56" y="12" width="22" height="15" rx="2" fill="{blue}" fill-opacity=".15"/>
  <path d="M52 30H82L80 32.5H54Z" fill="{light}" fill-opacity=".3"/>
</g>
<!-- server -->
<g fill="none" stroke="{light}" stroke-width="1.4">
  <rect x="822" y="10" width="22" height="11" rx="2" fill="{blue}" fill-opacity=".15"/>
  <rect x="822" y="23" width="22" height="11" rx="2" fill="{blue}" fill-opacity=".15"/>
</g>
<circle cx="828" cy="15.5" r="1.4" fill="#4ade80"/><circle cx="828" cy="28.5" r="1.4" fill="#4ade80"/>
<path d="M833 15.5H840M833 28.5H840" stroke="{light}" stroke-opacity=".5" stroke-linecap="round"/>
<!-- packets: clean until the attacker, tampered after -->
<g clip-path="url(#L)">
  <g class="fw"><g transform="translate(0 22)">{clean}</g></g>
  <g class="bw"><g transform="translate(0 22)">{tampered}</g></g>
</g>
<g clip-path="url(#R)">
  <g class="fw"><g transform="translate(0 22)">{tampered}</g></g>
  <g class="bw"><g transform="translate(0 22)">{clean}</g></g>
</g>
<!-- attacker in the middle -->
<circle class="tap" cx="450" cy="22" r="11" fill="none" stroke="{red}" stroke-width="1.2"/>
<circle cx="450" cy="22" r="11" fill="#0d1017" stroke="{red}" stroke-opacity=".7" stroke-width="1.2"/>
<g filter="url(#neon)" transform="translate(450 22.5) scale(.95)">{skull}</g>
</svg>
"""
    (OUT / "divider.svg").write_text(svg, encoding="utf-8")


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    build_stack()
    build_certs()
    build_journey()
    build_divider()
    print("assets written to", OUT)
