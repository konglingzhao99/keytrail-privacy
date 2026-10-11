#!/usr/bin/env python3
"""Write the static privacy pages from the language modules."""

import html
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from pages import de, en, fr, hi, ja, ko, mn, ru, th, zh_cn

LANGS = [
    ("en", "en", "en", en.PAGE),
    ("zh-cn", "zh-Hans", "zh-Hans", zh_cn.PAGE),
    ("ja", "ja", "ja", ja.PAGE),
    ("ru", "ru", "ru", ru.PAGE),
    ("fr", "fr", "fr", fr.PAGE),
    ("ko", "ko", "ko", ko.PAGE),
    ("de", "de", "de", de.PAGE),
    ("hi", "hi", "hi", hi.PAGE),
    ("th", "th", "th", th.PAGE),
    ("mn", "mn", "mn", mn.PAGE),
]

NAMES = {code: page["name"] for code, _, _, page in LANGS}


def render(page, depth, current):
    prefix = "../" if depth else ""
    links = []
    alternates = []
    for code, lang, hreflang, _ in LANGS:
        href = f"{prefix}{code}/"
        current_attr = ' aria-current="page"' if code == current else ""
        links.append(
            f'<a href="{href}" hreflang="{hreflang}" lang="{lang}"{current_attr}>{html.escape(NAMES[code])}</a>'
        )
        alternates.append(
            f'<link rel="alternate" hreflang="{hreflang}" href="{href}">'
        )
    alternates.append(
        f'<link rel="alternate" hreflang="x-default" href="{prefix}en/">'
    )
    parts = []
    for kind, value in page["blocks"]:
        if kind == "p":
            parts.append(f"<p>{html.escape(value)}</p>")
        elif kind == "h2":
            parts.append(f"<h2>{html.escape(value)}</h2>")
        elif kind == "ul":
            items = "".join(f"<li>{html.escape(item)}</li>" for item in value)
            parts.append(f"<ul>{items}</ul>")
        elif kind == "contact":
            parts.append(f"<p>{html.escape(value)}</p>")
            parts.append(
                '<p><a href="mailto:konglingzhao989@gmail.com">konglingzhao989@gmail.com</a></p>'
            )
            parts.append(
                f'<p><a href="{prefix}support/">{html.escape(page["support_link"])}</a></p>'
            )
        else:
            raise SystemExit(f"unknown block {kind}")
    brand = "#top" if depth == 0 else f"{prefix}"
    return f"""<!DOCTYPE html>
<html lang="{page["html_lang"]}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<title>{html.escape(page["title"])}</title>
<link rel="stylesheet" href="{prefix}assets/style.css">
<link rel="icon" href="{prefix}assets/icon.png">
{chr(10).join(alternates)}
</head>
<body id="top">
<a class="skip" href="#content">{html.escape(page["skip"])}</a>
<div class="shell">
<header class="mast">
<a class="brand" href="{brand}">
<img src="{prefix}assets/icon.png" width="28" height="28" alt="">
<span>KeyTrail</span>
</a>
</header>
<nav class="languages" aria-label="{html.escape(page["nav"])}">
{chr(10).join(links)}
</nav>
<main id="content">
<p class="updated">{html.escape(page["updated"])}</p>
<h1>{html.escape(page["h1"])}</h1>
{chr(10).join(parts)}
</main>
<footer>
<p>© 2026 KeyTrail</p>
</footer>
</div>
</body>
</html>
"""


SUPPORT = [
    ("en", "English", "Questions about KeyTrail can be sent to the address below. This is the public contact for the app. A reply within a set time is not promised."),
    ("zh-Hans", "简体中文", "关于 KeyTrail 的问题可以写到下面的地址。这是本应用的公开联系地址，不承诺在固定时间内回复。"),
    ("ja", "日本語", "KeyTrail についての質問は、下のアドレスへ送ってください。これはアプリの公開連絡先です。一定時間内の返信は約束しません。"),
    ("ru", "Русский", "Вопросы о KeyTrail можно отправить на адрес ниже. Это публичный контакт приложения. Ответ в определённый срок не обещается."),
    ("fr", "Français", "Les questions sur KeyTrail peuvent être envoyées à l’adresse ci-dessous. C’est le contact public de l’app. Une réponse dans un délai fixé n’est pas promise."),
    ("ko", "한국어", "KeyTrail에 대한 질문은 아래 주소로 보낼 수 있습니다. 이 주소는 앱의 공개 연락처입니다. 정해진 시간 안의 답장은 약속하지 않습니다."),
    ("de", "Deutsch", "Fragen zu KeyTrail kannst du an die Adresse unten schicken. Das ist die öffentliche Kontaktadresse der App. Eine Antwort innerhalb einer festen Zeit wird nicht zugesagt."),
    ("hi", "हिन्दी", "KeyTrail के बारे में प्रश्न नीचे दिए पते पर भेजे जा सकते हैं। यह ऐप का सार्वजनिक संपर्क है। किसी निश्चित समय में उत्तर का वादा नहीं है।"),
    ("th", "ไทย", "คำถามเกี่ยวกับ KeyTrail ส่งไปที่อยู่ด้านล่างได้ นี่คือที่อยู่ติดต่อสาธารณะของแอป ไม่ได้สัญญาว่าจะตอบภายในเวลาที่กำหนด"),
    ("mn", "Монгол", "KeyTrail-ийн талаарх асуултыг доорх хаяг руу илгээж болно. Энэ нь аппын нийтийн холбоо барих хаяг юм. Тогтсон хугацаанд хариулахыг амлахгүй."),
]


def render_support():
    sections = []
    links = []
    for code, _, hreflang, page in LANGS:
        links.append(
            f'<a href="../{code}/" hreflang="{hreflang}" lang="{page["html_lang"]}">{html.escape(NAMES[code])}</a>'
        )
    for lang, name, text in SUPPORT:
        sections.append(
            f'<section lang="{lang}"><h2>{html.escape(name)}</h2><p>{html.escape(text)}</p></section>'
        )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<title>Support — KeyTrail</title>
<link rel="stylesheet" href="../assets/style.css">
<link rel="icon" href="../assets/icon.png">
</head>
<body id="top">
<a class="skip" href="#content">Skip to content</a>
<div class="shell">
<header class="mast">
<a class="brand" href="../">
<img src="../assets/icon.png" width="28" height="28" alt="">
<span>KeyTrail</span>
</a>
</header>
<nav class="languages" aria-label="Language">
{chr(10).join(links)}
</nav>
<main id="content">
<h1>Support</h1>
<p>KeyTrail is a Mac menu bar app. Write to the address below about the app or its privacy policy.</p>
<p><a href="mailto:konglingzhao989@gmail.com">konglingzhao989@gmail.com</a></p>
{chr(10).join(sections)}
</main>
<footer>
<p>© 2026 KeyTrail</p>
</footer>
</div>
</body>
</html>
"""


def main():
    home = next(page for code, _, _, page in LANGS if code == "en")
    (ROOT / "index.html").write_text(render(home, 0, "en"), encoding="utf-8")
    for code, _, _, page in LANGS:
        folder = ROOT / code
        folder.mkdir(exist_ok=True)
        (folder / "index.html").write_text(render(page, 1, code), encoding="utf-8")
    support = ROOT / "support"
    support.mkdir(exist_ok=True)
    (support / "index.html").write_text(render_support(), encoding="utf-8")
    print(f"wrote {len(LANGS) + 2} pages")


if __name__ == "__main__":
    main()
