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

import re
import logging
from xpcom import components

try:
    from xpcom.server import UnwrapObject
except Exception:  # pragma: no cover
    def UnwrapObject(obj):
        return obj

from koLintResults import koLintResults

log = logging.getLogger("koCTPP.linter")
log.setLevel(logging.DEBUG)

# Полный CTPP-тег. Допускаем также CT++ whitespace-control форму
# <-TMPL_var foo->, описанную в waaeer/ctpp.
_CTPP_TAG_RE = re.compile(
    r"</?-?TMPL_[A-Za-z0-9_:-]+\b(?:[^\"'>]|\"[^\"]*\"|'[^']*')*-?>",
    re.I
)

# Пока пользователь печатает <TMPL_, <TMPL_va и т.п., HTML linter не должен
# трактовать этот незавершённый фрагмент как HTML-тег. Реальную ошибку CTPP
# на этапе B будет проверять компилятор CTPP, а HTML lint должен оставаться
# прозрачным к шаблонному синтаксису.
_CTPP_PARTIAL_TAG_RE = re.compile(
    r"</?-?TMPL_[^<>\r\n]*",
    re.I
)


def _mask_same_len(s):
    # Сохраняем длину и переносы строк, чтобы координаты HTML/JS ошибок
    # оставались координатами исходного CTPP-файла.
    return u"".join([u"\n" if ch == u"\n" else u" " for ch in s])


class KoCTPPLinter(object):
    _com_interfaces_ = [components.interfaces.koILinter]
    _reg_desc_ = "CTPP: HTML/JS Linter (stage A: HTML only)"
    _reg_clsid_ = "{a98b6bb4-7c90-46a1-bf64-8c09f6ff2af1}"
    _reg_contractid_ = "@activestate.com/koLinter?language=CTPP;1"
    _reg_categories_ = [
        ("category-komodo-linter", "CTPP"),
    ]

    # Underscore-template support passed through the HTML linter.
    _tplPatterns = (
        "CTPP",
        re.compile(r"<%[=-]?", re.U),
        re.compile(r"%>\s*\Z", re.U | re.DOTALL),
    )

    def __init__(self):
        self._koLintService = None
        self._html_linter = None

    def _empty_results(self):
        return koLintResults()

    def _get_html_linter(self):
        if self._html_linter is not None:
            return self._html_linter
        try:
            self._koLintService = components.classes["@activestate.com/koLintService;1"] \
                .getService(components.interfaces.koILintService)

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
        try:
            unicode
            _unicode = unicode
        except NameError:
            _unicode = str

        if not isinstance(text, _unicode):
            try:
                text = text.decode("utf-8", "replace")
            except Exception:
                return u""

        def repl(match):
            return _mask_same_len(match.group(0))

        # Сначала полные теги, затем оставшиеся незавершённые фрагменты.
        text = _CTPP_TAG_RE.sub(repl, text)
        text = _CTPP_PARTIAL_TAG_RE.sub(repl, text)
        return text

    def lint(self, request):
        try:
            html_linter = self._get_html_linter()
            if not html_linter:
                return self._empty_results()

            try:
                text = request.content
            except Exception:
                text = None

            if text is not None:
                return self.lint_with_text(request, text)

            result = html_linter.lint(request)
            return result or self._empty_results()

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
                result = html_linter.lint_with_text(request, sanitized)
                return result or self._empty_results()

            result = html_linter.lint(request)
            return result or self._empty_results()

        except Exception:
            log.exception("CTPP linter crashed in lint_with_text()")
            return self._empty_results()
