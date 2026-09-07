# 文本与 HTML 处理工具。


from __future__ import annotations

import html
import re
from html.parser import HTMLParser

class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        if data.strip():
            self.parts.append(data.strip())

def normalize_whitespace(text: str | None) -> str:
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()

def html_to_text(content: str | None) -> str:
    if not content:
        return ""
    parser = _TextExtractor()
    parser.feed(content)
    return normalize_whitespace(html.unescape(" ".join(parser.parts)))

def truncate_text(text: str, limit: int = 4000) -> str:
    text = text or ""
    return text if len(text) <= limit else text[: limit - 3] + "..."
