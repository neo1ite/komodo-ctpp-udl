#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Code Intelligence для шаблонов CTPP."""

import logging
import re

from codeintel2.common import TRG_FORM_CPLN, Trigger
from codeintel2.langintel import LangIntel
from codeintel2.udl import UDLBuffer, UDLCILEDriver, UDLLexer, XMLParsingBufferMixin

from SilverCity.ScintillaConstants import (
    SCE_UDL_TPL_DEFAULT,
    SCE_UDL_TPL_IDENTIFIER,
    SCE_UDL_TPL_OPERATOR,
    SCE_UDL_TPL_WORD,
)

try:
    from xpcom.server import UnwrapObject
    _xpcom_ = True
except ImportError:
    _xpcom_ = False


lang = "CTPP"
log = logging.getLogger("codeintel.ctpp")

# Канонические имена тегов, поддерживаемых текущим UDL-лексером.
CTPP_TAGS = tuple(sorted((
    "TMPL_block",
    "TMPL_call",
    "TMPL_comment",
    "TMPL_else",
    "TMPL_elsif",
    "TMPL_foreach",
    "TMPL_if",
    "TMPL_include",
    "TMPL_loop",
    "TMPL_udf",
    "TMPL_unless",
    "TMPL_var",
)))

# Теги, для которых имеет смысл предлагать закрывающую форму </TMPL_...>.
CTPP_CONTAINER_TAGS = tuple(sorted((
    "TMPL_block",
    "TMPL_comment",
    "TMPL_foreach",
    "TMPL_if",
    "TMPL_loop",
    "TMPL_udf",
    "TMPL_unless",
)))

_TAG_FRAGMENT_RE = re.compile(r"<(/?)(TMPL_[A-Za-z0-9_]*)$", re.I)


class CTPPLexer(UDLLexer):
    lang = lang


class CTPPLangIntel(LangIntel):
    lang = lang

    _all_tag_completions = tuple(("element", name) for name in CTPP_TAGS)
    _container_tag_completions = tuple(
        ("element", name) for name in CTPP_CONTAINER_TAGS
    )

    @staticmethod
    def _tag_fragment_from_pos(buf, pos):
        """Вернуть (fragment, word_start, closing) для незавершённого тега."""
        if pos <= 0:
            return None

        # Ограничиваем окно: имя CTPP-тега заведомо существенно короче.
        start = max(0, pos - 64)
        text = buf.accessor.text_range(start, pos)
        match = _TAG_FRAGMENT_RE.search(text)
        if match is None:
            return None

        fragment = match.group(2)
        return fragment, pos - len(fragment), bool(match.group(1))

    def _tag_trigger(self, buf, pos, implicit):
        info = self._tag_fragment_from_pos(buf, pos)
        if info is None:
            return None

        fragment, word_start, closing = info
        suffix_len = max(0, len(fragment) - len("TMPL_"))

        # Автоматически показываем список сразу после TMPL_ и затем после
        # двух введённых символов имени. Ctrl+J работает на любой длине.
        if implicit and fragment.lower() != "tmpl_" and suffix_len != 2:
            return None

        return Trigger(
            self.lang,
            TRG_FORM_CPLN,
            "tags",
            word_start,
            implicit,
            word_start=word_start,
            word_end=pos,
            fragment=fragment,
            closing=closing,
        )

    def trg_from_pos(self, buf, pos, implicit=True, DEBUG=False, ac=None):
        if pos < 1:
            return None

        style = buf.accessor.style_at_pos(pos - 1)
        if style not in (
            SCE_UDL_TPL_DEFAULT,
            SCE_UDL_TPL_IDENTIFIER,
            SCE_UDL_TPL_OPERATOR,
            SCE_UDL_TPL_WORD,
        ):
            return None

        return self._tag_trigger(buf, pos, implicit)

    def preceding_trg_from_pos(self, buf, pos, curr_pos,
                               preceding_trg_terminators=None, DEBUG=False):
        if curr_pos < 1:
            return None

        style = buf.accessor.style_at_pos(curr_pos - 1)
        if style not in (
            SCE_UDL_TPL_DEFAULT,
            SCE_UDL_TPL_IDENTIFIER,
            SCE_UDL_TPL_OPERATOR,
            SCE_UDL_TPL_WORD,
        ):
            return None

        return self._tag_trigger(buf, curr_pos, implicit=False)

    def async_eval_at_trg(self, buf, trg, ctlr):
        if _xpcom_:
            trg = UnwrapObject(trg)
            ctlr = UnwrapObject(ctlr)

        ctlr.start(buf, trg)

        if trg.id == (self.lang, TRG_FORM_CPLN, "tags"):
            fragment = trg.extra.get("fragment", "")
            closing = bool(trg.extra.get("closing"))
            source = (self._container_tag_completions
                      if closing else self._all_tag_completions)
            prefix = fragment.lower()
            completions = tuple(
                item for item in source if item[1].lower().startswith(prefix)
            )
            ctlr.set_cplns(completions)
            ctlr.done("success")
            return

        ctlr.done("success")


class CTPPBuffer(UDLBuffer, XMLParsingBufferMixin):
    lang = lang

    # Делегируем семейства штатным движкам Komodo.
    m_lang = "HTML5"
    css_lang = "CSS"
    csl_lang = "JavaScript"
    tpl_lang = "CTPP"

    cb_show_if_empty = True

    # Совместимо с XML/HTML, CSS и JavaScript completion в смешанном файле.
    cpln_stop_chars = "'\" (;},~`@#%^&*()=+{}]|\\;,.<>?/"


class CTPPCILEDriver(UDLCILEDriver):
    """На 2.0 индексируем вложенные JavaScript/CSS штатными CILE-драйверами.

    Собственный CTPP CILE запланирован на версию 2.2.
    """

    lang = lang
    csl_lang = "JavaScript"
    css_lang = "CSS"


def register(mgr):
    """Зарегистрировать поддержку CTPP в CodeIntel."""
    mgr.set_lang_info(
        lang,
        silvercity_lexer=CTPPLexer(),
        buf_class=CTPPBuffer,
        langintel_class=CTPPLangIntel,
        import_handler_class=None,
        cile_driver_class=CTPPCILEDriver,
        is_cpln_lang=True,
    )
