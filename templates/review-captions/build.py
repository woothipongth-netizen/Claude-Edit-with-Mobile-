"""สร้างโปรเจกต์ HyperFrames จาก content.json: หัวข้อค้างบนจอทุกช่วง + ซับตามเสียงพากย์ + ชื่อร้านตอนจบ

ใช้: python3 -I templates/review-captions/build.py <content.json> <โฟลเดอร์โปรเจกต์>
แล้ว: cd <โฟลเดอร์โปรเจกต์> && npx hyperframes lint && npx hyperframes render -o out.mp4 --quiet

ต้องรัน scripts/setup.sh ก่อน (คัดลอก GSAP และฟอนต์ Kanit มาไว้ที่ templates/vendor/)
ดูตัวอย่าง content.json ได้ที่ content.example.json
"""
import html
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
VENDOR = HERE.parent / "vendor"
BRAND = json.loads((HERE.parent.parent / "brand.json").read_text())


def rich(text):
    """*คำ* = สีทอง, | = ขึ้นบรรทัดใหม่ ข้อความอื่นถูก escape"""
    out, gold = [], False
    for part in html.escape(text).split("*"):
        out.append(f"<em>{part}</em>" if gold else part)
        gold = not gold
    return "".join(out).replace("|", "<br />")


def main():
    content = json.loads(Path(sys.argv[1]).read_text())
    proj = Path(sys.argv[2])
    proj.mkdir(parents=True, exist_ok=True)
    (proj / "fonts").mkdir(exist_ok=True)
    shutil.copy(VENDOR / "gsap.min.js", proj)
    for f in (VENDOR / "fonts").glob("*.woff2"):
        shutil.copy(f, proj / "fonts")
    for key in ("footage", "audio"):
        src = Path(content[key])
        shutil.copy(src, proj / src.name)
        content[key] = src.name

    total = content["duration"]
    end = {"brand": BRAND["shop_name"], "cta": BRAND["cta"], **content["end_card"]}
    els, anim = [], []

    for i, t in enumerate(content["titles"]):
        a, b = t["start"], t["end"]
        els.append(f'<div id="t{i}" class="title clip" data-start="{a}" data-duration="{b - a:.2f}" '
                   f'data-track-index="3"><span>{rich(t["text"])}</span></div>')
        anim.append(f'["#t{i}", {a}, {b - a:.2f}, "title"]')

    for i, c in enumerate(content["captions"]):
        a, b = c["start"], c["end"]
        els.append(f'<div id="c{i}" class="line clip" data-start="{a}" data-duration="{b - a:.2f}" '
                   f'data-track-index="{5 + i % 2}"><span>{rich(c["text"])}</span></div>')
        anim.append(f'["#c{i}", {a}, {b - a:.2f}, "line"]')

    hook = content.get("hook")
    if hook:
        els.append(f'<div id="hook" class="hook clip" data-start="{hook["start"]}" '
                   f'data-duration="{hook["end"] - hook["start"]:.2f}" data-track-index="7">'
                   f'<div>{rich(hook["text"])}</div></div>')

    page = (HERE / "index.template.html").read_text()
    page = (page.replace("{{TOTAL}}", str(total))
                .replace("{{ACCENT}}", BRAND["colors"]["accent"])
                .replace("{{FOOTAGE}}", content["footage"])
                .replace("{{AUDIO}}", content["audio"])
                .replace("{{END_START}}", str(end["start"]))
                .replace("{{END_DUR}}", f'{total - end["start"]:.2f}')
                .replace("{{BRAND}}", html.escape(end["brand"]))
                .replace("{{CTA}}", html.escape(end["cta"]))
                .replace("{{ELEMENTS}}", "\n      ".join(els))
                .replace("{{ANIM}}", ",\n        ".join(anim))
                .replace("{{HOOK}}", json.dumps(hook)))
    (proj / "index.html").write_text(page)
    print(f"สร้างแล้ว: {proj / 'index.html'} ({len(content['titles'])} หัวข้อ, {len(content['captions'])} ซับ)")


if __name__ == "__main__":
    main()
