# -*- coding: utf-8 -*-
# ***** BEGIN LICENSE BLOCK *****
# Version: MPL 1.1/GPL 2.0/LGPL 2.1
#
# The contents of this file are subject to the Mozilla Public License
# Version 1.1 (the "License"); you may not use this file except in
# compliance with the License. You may obtain a copy of the License at
# http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS IS"
# basis, WITHOUT WARRANTY OF ANY KIND, either express or implied. See the
# License for the specific language governing rights and limitations
# under the License.
#
# The Original Code is Komodo code.
#
# The Initial Developer of the Original Code is ActiveState Software Inc.
#
# ***** END LICENSE BLOCK *****

"""
CTPP linter (stage A): delegate to Komodo's built-in HTML linter so we get:
  - HTML validation
  - JS validation inside <script> blocks (handled by HTML linter)
No ctpp compiler here yet.

IMPORTANT:
  - Always return koILintResults. Returning None makes Komodo think the linter is async
    and the "hourglass" will hang forever.
"""

# components/koCTPP_Linter.py
import re
import logging
from xpcom import components

# Komodo often returns XPCOM-wrapped Python objects; UnwrapObject gives you the real object
# so you can pass extra args (TPLInfo/udlMapping), as Mason does.
try:
    from xpcom.server import UnwrapObject
except Exception:  # pragma: no cover
    def UnwrapObject(obj):
        return obj

# This is the canonical "empty results" object (used in Komodo's own linters)
from koLintResult import KoLintResult
from koLintResults import koLintResults

import scimozindent

log = logging.getLogger("koCTPP.linter")
log.setLevel(logging.DEBUG)

# Надежное распознавание <TMPL_...> с учетом кавычек (чтобы '>' внутри строк не ломал парсинг)
_CTPP_TAG_RE = re.compile(
    r"</?TMPL_[A-Za-z0-9_:-]+\b(?:[^\"'>]|\"[^\"]*\"|'[^']*')*>",
    re.I
)

def _mask_same_len(s):
    # сохраняем длину и переносы строк (на случай если шаблон внезапно многострочный)
    return u"".join([u"\n" if ch == u"\n" else u" " for ch in s])

class KoCTPPLinter(object):
    _com_interfaces_ = [components.interfaces.koILinter]
    _reg_desc_ = "CTPP: HTML/JS Linter (stage A: HTML only)"
    _reg_clsid_ = "{a98b6bb4-7c90-46a1-bf64-8c09f6ff2af1}"  # <-- ВАЖНО: уникальный CLSID линтера

    # Do NOT use "type=" пока у нас один лентер — иначе Komodo может не выбрать его как default.
    _reg_contractid_ = "@activestate.com/koLinter?language=CTPP;1"
    _reg_categories_ = [
        ("category-komodo-linter", "CTPP"),
    ]

    # For HTML linter's "template" support (same trick as Mason).
    # This doesn't make Komodo "understand" CTPP, but helps HTML/JS linting be less noisy.
    _tplPatterns = (
        "CTPP",
        re.compile(r"<%[=-]?", re.U),
        re.compile(r"%>\s*\Z", re.U | re.DOTALL),
    )

    def __init__(self):
        # НИЧЕГО не делаем “тяжёлого” в __init__ — чтобы addRequest не падал.
        self._koLintService = None
        self._html_linter = None

    def _empty_results(self):
        # MUST return an object; never None.
        return koLintResults()

    def _get_html_linter(self):
        if self._html_linter is not None:
            return self._html_linter
        try:
            self._koLintService = components.classes["@activestate.com/koLintService;1"] \
                .getService(components.interfaces.koILintService)

            # На разных версиях Komodo может быть "HTML" или "HTML5"
            for lang in ("HTML5", "HTML"):
                try:
                    linter = UnwrapObject(self._koLintService.getLinterForLanguage(lang))
                    if linter:
                        self._html_linter = linter
                        return linter
                except Exception:
                    pass
        except Exception:
            log.exception("Failed to obtain HTML linter")

        self._html_linter = None
        return None

    def _sanitize_ctpp(self, text):
        # text ожидаем unicode; если пришли bytes — декодим максимально безопасно
        try:
            unicode  # noqa
            _unicode = unicode
        except NameError:
            _unicode = str

        if not isinstance(text, _unicode):
            enc = "utf-8"
            try:
                enc = getattr(text, "encoding", None) or enc
            except Exception:
                pass
            try:
                text = text.decode(enc, "replace")
            except Exception:
                try:
                    text = text.decode("utf-8", "replace")
                except Exception:
                    # в худшем случае — пустой текст, но НЕ None
                    return u""

        # Маскируем только TMPL-теги, остальной HTML оставляем как есть
        def repl(m):
            return _mask_same_len(m.group(0))

        return _CTPP_TAG_RE.sub(repl, text)

    def lint(self, request):
        # Базовая схема lint/lint_with_text по документации Komodo (request.content + request.encoding) :contentReference[oaicite:0]{index=0}
        try:
            html_linter = self._get_html_linter()
            if not html_linter:
                return self._empty_results()

            # Пытаемся взять исходный текст из request.content (часто там именно текст буфера)
            text = None
            try:
                text = request.content
            except Exception:
                text = None

            if text is not None:
                return self.lint_with_text(request, text)

            # Пока stage A: просто делегируем как есть.
            # (Позже добавим санитайз/выделение JS блоков.)
            res = html_linter.lint(request)
            return res or self._empty_results()

        except Exception:
            log.exception("CTPP linter crashed in lint()")
            return self._empty_results()

    def lint_with_text(self, request, text):
        try:
            html_linter = self._get_html_linter()
            if not html_linter:
                return self._empty_results()

            sanitized = self._sanitize_ctpp(text)

            if hasattr(html_linter, "lint_with_text"):
                res = html_linter.lint_with_text(request, sanitized)
                return res or self._empty_results()

            # fallback
            res = html_linter.lint(request)
            return res or self._empty_results()

        except Exception:
            log.exception("CTPP linter crashed in lint_with_text()")
            return self._empty_results()
