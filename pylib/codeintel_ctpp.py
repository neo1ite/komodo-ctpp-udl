#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Code Intelligence для шаблонов CTPP."""

import logging
import os
import re

from codeintel2.common import TRG_FORM_CALLTIP, TRG_FORM_CPLN, Trigger
from codeintel2.langintel import LangIntel, ParenStyleCalltipIntelMixin
from codeintel2.udl import UDLBuffer, UDLCILEDriver, UDLLexer, XMLParsingBufferMixin

from SilverCity.ScintillaConstants import (
    SCE_UDL_TPL_COMMENT,
    SCE_UDL_TPL_DEFAULT,
    SCE_UDL_TPL_IDENTIFIER,
    SCE_UDL_TPL_OPERATOR,
    SCE_UDL_TPL_STRING,
    SCE_UDL_TPL_WORD,
)

try:
    from xpcom.server import UnwrapObject
    _xpcom_ = True
except ImportError:
    _xpcom_ = False


lang = "CTPP"
log = logging.getLogger("codeintel.ctpp")

# Канонический синтаксис для этого расширения — fork waaeer/ctpp (CT++ 2.8).
# doc/template_language.rst перечисляет основные теги и отдельно документирует
# TMPL_break. TMPL_loop/TMPL_udf в этой реализации языка не являются тегами.
CTPP_TAGS = tuple(sorted((
    "TMPL_block",
    "TMPL_break",
    "TMPL_call",
    "TMPL_comment",
    "TMPL_else",
    "TMPL_elsif",
    "TMPL_foreach",
    "TMPL_if",
    "TMPL_include",
    "TMPL_unless",
    "TMPL_var",
    "TMPL_verbose",
)))

# Теги, для которых существует закрывающая форма </TMPL_...>.
CTPP_CONTAINER_TAGS = tuple(sorted((
    "TMPL_block",
    "TMPL_comment",
    "TMPL_foreach",
    "TMPL_if",
    "TMPL_unless",
    "TMPL_verbose",
)))

# В этих тегах CT++ 2.8 документирует полноценные expressions/functions.
CTPP_EXPRESSION_TAGS = frozenset((
    "var",
    "if",
    "elsif",
    "unless",
    "foreach",
))

# Текстовые формы операторов из документации CT++ 2.8. mod/div находятся
# непосредственно в таблице приоритетов, остальные перечислены как aliases.
CTPP_OPERATOR_KEYWORDS = tuple(sorted((
    "and", "div", "eq", "ge", "gt", "le", "lt", "mod", "ne", "or",
)))

# Символьные операторы показываются при явном Ctrl+J. Для & | = ! < есть
# также узкий implicit trigger после первого символа.
CTPP_OPERATOR_SYMBOLS = (
    "!", "!=", "&&", "*", "+", "-", "/", "<", "<=", "==", ">", ">=", "||",
)

# Сигнатуры взяты из waaeer/ctpp doc/template_language.rst.
# Имена аргументов намеренно сохраняют написание канонической документации.
CTPP_FUNCTION_SIGNATURES = {
    "_": "_(msgid[, msgid_plural, n][, domain])",
    "AVG": "AVG(flag, a[, b, ...])",
    "BASE64_DECODE": "BASE64_DECODE(x)",
    "BASE64_ENCODE": "BASE64_ENCODE(x)",
    "CAST": "CAST(flag, x)",
    "CONCAT": "CONCAT(a[, b, ...])",
    "CONTEXT": "CONTEXT()",
    "DATE_FORMAT": "DATE_FORMAT(x, format)",
    "DEFAULT": "DEFAULT(x, y)",
    "DEFINED": "DEFINED(a[, b, ...])",
    "ERROR": "ERROR()",
    "FORM_PARAM": "FORM_PARAM(x, y)",
    "GETTEXT": "GETTEXT(msgid[, msgid_plural, n][, domain])",
    "GET_TYPE": "GET_TYPE(x)",
    "HASH_KEYS": "HASH_KEYS(x)",
    "HMAC_MD5": "HMAC_MD5(x, key)",
    "HOSTNAME": "HOSTNAME()",
    "HREF_PARAM": "HREF_PARAM(x, y)",
    "HTMLESCAPE": "HTMLESCAPE(a[, b, ...])",
    "ICONV": "ICONV(x, src, dst[, flags])",
    "IN_ARRAY": "IN_ARRAY(x, array)",
    "IN_SET": "IN_SET(x, a[, b, ...])",
    "JSONESCAPE": "JSONESCAPE(a[, b, ...])",
    "JSON": "JSON(x)",
    "LIST_ELEMENT": "LIST_ELEMENT(a[, b, ...], x)",
    "LIST": "LIST([a, b, ...])",
    "LOG": "LOG(x[, base])",
    "MAX": "MAX(a[, b, ...])",
    "MB_SIZE": "MB_SIZE(x)",
    "MB_SUBSTR": "MB_SUBSTR(x, offset[, bytes[, y]]])",
    "MB_TRUNCATE": "MB_TRUNCATE(x, offest[, addon])",
    "MD5": "MD5(a[, b, ...])",
    "MIN": "MIN(a[, b, ...])",
    "NUM_FORMAT": "NUM_FORMAT(x, y)",
    "OBJ_DUMP": "OBJ_DUMP([a, b, ...])",
    "RANDOM": "RANDOM([[min,] max])",
    "SIZE": "SIZE(x)",
    "SPRINTF": "SPRINTF(format, a[, b, ...])",
    "SUBSTR": "SUBSTR(x, offset[, bytes[, y]]])",
    "TRUNCATE": "TRUNCATE(x, offest[, addon])",
    "URIESCAPE": "URIESCAPE(a[, b, ...])",
    "URLESCAPE": "URLESCAPE(a[, b, ...])",
    "VERSION": "VERSION([x])",
    "WMLESCAPE": "WMLESCAPE(a[, b, ...])",
    "XMLESCAPE": "XMLESCAPE(a[, b, ...])",
}

# args(...) — синтаксис именованных блоков, а не функция из Library reference.
CTPP_SPECIAL_SIGNATURES = {
    "args": "args(a, b, ...)",
}

# CT++ допускает <-TMPL_var ...-> как короткую форму управления пробелами.
_TAG_FRAGMENT_RE = re.compile(r"<(/?)-?(TMPL_[A-Za-z0-9_]*)$", re.I)
_TAG_CONTEXT_RE = re.compile(r"<(-?)TMPL_([A-Za-z_][A-Za-z0-9_]*)\b", re.I)
_IDENTIFIER_FRAGMENT_RE = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)$")
_FUNCTION_OPEN_RE = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)\s*\($")


class CTPPLexer(UDLLexer):
    lang = lang


class CTPPLangIntel(ParenStyleCalltipIntelMixin, LangIntel):
    lang = lang

    # В CTPP конец тега также завершает calltip region.
    calltip_region_terminators = tuple("]});>")

    _all_tag_completions = tuple(("element", name) for name in CTPP_TAGS)
    _container_tag_completions = tuple(
        ("element", name) for name in CTPP_CONTAINER_TAGS
    )
    _function_completions = tuple(
        ("function", name) for name in sorted(CTPP_FUNCTION_SIGNATURES)
    )
    _operator_keyword_completions = tuple(
        ("keyword", name) for name in CTPP_OPERATOR_KEYWORDS
    )
    _operator_symbol_completions = tuple(
        ("keyword", name) for name in CTPP_OPERATOR_SYMBOLS
    )

    @staticmethod
    def _is_tpl_code_style(style):
        return style in (
            SCE_UDL_TPL_DEFAULT,
            SCE_UDL_TPL_IDENTIFIER,
            SCE_UDL_TPL_OPERATOR,
            SCE_UDL_TPL_WORD,
        )

    @staticmethod
    def _tag_fragment_from_pos(buf, pos):
        """Вернуть (fragment, word_start, closing) для незавершённого тега."""
        if pos <= 0:
            return None

        start = max(0, pos - 64)
        text = buf.accessor.text_range(start, pos)
        match = _TAG_FRAGMENT_RE.search(text)
        if match is None:
            return None

        fragment = match.group(2)
        return fragment, pos - len(fragment), bool(match.group(1))

    @staticmethod
    def _tag_context_from_pos(buf, pos):
        """Вернуть имя текущего открывающего TMPL-тега в нижнем регистре.

        Ищем именно последний префикс TMPL_, а не последний символ '<': внутри
        выражения '<' является обычным оператором сравнения.
        """
        if pos <= 0:
            return None

        start = max(0, pos - 4096)
        text = buf.accessor.text_range(start, pos)
        matches = list(_TAG_CONTEXT_RE.finditer(text))
        if not matches:
            return None
        return matches[-1].group(2).lower()

    @staticmethod
    def _inside_args_call(buf, pos):
        """Проверить, находится ли позиция внутри незакрытого args(...)."""
        start = max(0, pos - 2048)
        text = buf.accessor.text_range(start, pos)
        match = None
        for candidate in re.finditer(r"\bargs\s*\(", text, re.I):
            match = candidate
        if match is None:
            return False

        depth = 1
        quote = None
        escaped = False
        i = match.end()
        while i < len(text):
            ch = text[i]
            if quote is not None:
                if escaped:
                    escaped = False
                elif ch == "\\":
                    escaped = True
                elif ch == quote:
                    quote = None
            elif ch in ("'", '"'):
                quote = ch
            elif ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0:
                    return False
            i += 1
        return depth > 0

    def _expressions_allowed_at_pos(self, buf, pos, tag_name=None):
        if tag_name is None:
            tag_name = self._tag_context_from_pos(buf, pos)
        if tag_name in CTPP_EXPRESSION_TAGS:
            return True
        # TMPL_call допускает вычисляемые значения в args(...).
        if tag_name == "call" and self._inside_args_call(buf, pos):
            return True
        return False

    def _tag_trigger(self, buf, pos, implicit):
        info = self._tag_fragment_from_pos(buf, pos)
        if info is None:
            return None

        fragment, word_start, closing = info
        suffix_len = max(0, len(fragment) - len("TMPL_"))

        # Автоматический popup: сразу после TMPL_, затем после двух символов
        # имени. Явный Ctrl+J работает на любой длине фрагмента.
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

    def _expression_candidates(self, buf, pos, tag_name):
        candidates = []

        if self._expressions_allowed_at_pos(buf, pos, tag_name):
            candidates.extend(self._function_completions)
            candidates.extend(self._operator_keyword_completions)
            candidates.extend(self._operator_symbol_completions)
            if tag_name == "foreach":
                candidates.append(("keyword", "as"))

        if tag_name in ("block", "call"):
            candidates.append(("function", "args"))

        # Сохраняем стабильный порядок UI: тип не влияет на сортировку имени.
        candidates.sort(key=lambda item: item[1].lower())
        return tuple(candidates)

    def _identifier_fragment_from_pos(self, buf, pos):
        start = max(0, pos - 128)
        text = buf.accessor.text_range(start, pos)
        match = _IDENTIFIER_FRAGMENT_RE.search(text)
        if match is None:
            return "", pos

        fragment = match.group(1)
        word_start = pos - len(fragment)

        # foo.ba<|> — это member/variable completion этапа 2.4, а не built-ins.
        if word_start > 0 and buf.accessor.char_at_pos(word_start - 1) == ".":
            return None

        return fragment, word_start

    def _expression_trigger(self, buf, pos, implicit):
        tag_name = self._tag_context_from_pos(buf, pos)
        candidates = self._expression_candidates(buf, pos, tag_name)
        if not candidates:
            return None

        info = self._identifier_fragment_from_pos(buf, pos)
        if info is None:
            return None
        fragment, word_start = info

        prefix = fragment.lower()
        matching = tuple(
            item for item in candidates if item[1].lower().startswith(prefix)
        )

        if implicit:
            # Автоматически открываем список только после двух букв и только
            # если префикс действительно совпадает с известным built-in/keyword.
            # Так неизвестные runtime variables не получают ложный popup.
            if len(fragment) != 2 or not matching:
                return None

        return Trigger(
            self.lang,
            TRG_FORM_CPLN,
            "expressions",
            word_start,
            implicit,
            word_start=word_start,
            word_end=pos,
            fragment=fragment,
            tag_name=tag_name or "",
        )

    def _symbol_operator_trigger(self, buf, pos, implicit):
        if not implicit or pos < 1:
            return None

        ch = buf.accessor.char_at_pos(pos - 1)
        if ch not in "&|=!<":
            return None

        tag_name = self._tag_context_from_pos(buf, pos)
        if not self._expressions_allowed_at_pos(buf, pos, tag_name):
            return None

        matches = tuple(
            item for item in self._operator_symbol_completions
            if item[1].startswith(ch) and item[1] != ch
        )
        if not matches:
            return None

        return Trigger(
            self.lang,
            TRG_FORM_CPLN,
            "operators",
            pos - 1,
            implicit,
            word_start=pos - 1,
            word_end=pos,
            fragment=ch,
            tag_name=tag_name or "",
        )

    def _calltip_trigger(self, buf, pos, implicit):
        if pos < 1 or buf.accessor.char_at_pos(pos - 1) != "(":
            return None

        start = max(0, pos - 256)
        text = buf.accessor.text_range(start, pos)
        match = _FUNCTION_OPEN_RE.search(text)
        if match is None:
            return None

        raw_name = match.group(1)
        upper_name = raw_name.upper()
        tag_name = self._tag_context_from_pos(buf, pos)

        if upper_name in CTPP_FUNCTION_SIGNATURES:
            if not self._expressions_allowed_at_pos(buf, pos, tag_name):
                return None
            signature_key = upper_name
        elif raw_name.lower() in CTPP_SPECIAL_SIGNATURES:
            if tag_name not in ("block", "call"):
                return None
            signature_key = raw_name.lower()
        else:
            return None

        return Trigger(
            self.lang,
            TRG_FORM_CALLTIP,
            "function-signature",
            pos,
            implicit,
            function=signature_key,
            tag_name=tag_name or "",
        )

    def trg_from_pos(self, buf, pos, implicit=True, DEBUG=False, ac=None):
        if pos < 1:
            return None

        style = buf.accessor.style_at_pos(pos - 1)
        if not self._is_tpl_code_style(style):
            return None

        trigger = self._calltip_trigger(buf, pos, implicit)
        if trigger is not None:
            return trigger

        trigger = self._tag_trigger(buf, pos, implicit)
        if trigger is not None:
            return trigger

        trigger = self._symbol_operator_trigger(buf, pos, implicit)
        if trigger is not None:
            return trigger

        return self._expression_trigger(buf, pos, implicit)

    def preceding_trg_from_pos(self, buf, pos, curr_pos,
                               preceding_trg_terminators=None, DEBUG=False):
        if curr_pos < 1:
            return None

        style = buf.accessor.style_at_pos(curr_pos - 1)
        if not self._is_tpl_code_style(style):
            return None

        trigger = self._calltip_trigger(buf, curr_pos, implicit=False)
        if trigger is not None:
            return trigger

        trigger = self._tag_trigger(buf, curr_pos, implicit=False)
        if trigger is not None:
            return trigger

        return self._expression_trigger(buf, curr_pos, implicit=False)

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

        if trg.id in (
            (self.lang, TRG_FORM_CPLN, "expressions"),
            (self.lang, TRG_FORM_CPLN, "operators"),
        ):
            fragment = trg.extra.get("fragment", "")
            tag_name = trg.extra.get("tag_name", "")
            source = self._expression_candidates(buf, trg.pos, tag_name)
            prefix = fragment.lower()
            completions = tuple(
                item for item in source if item[1].lower().startswith(prefix)
            )
            ctlr.set_cplns(completions)
            ctlr.done("success")
            return

        if trg.id == (self.lang, TRG_FORM_CALLTIP, "function-signature"):
            name = trg.extra.get("function", "")
            if name in CTPP_FUNCTION_SIGNATURES:
                signature = CTPP_FUNCTION_SIGNATURES[name]
            else:
                signature = CTPP_SPECIAL_SIGNATURES.get(name)
            if signature:
                ctlr.set_calltips((signature,))
            ctlr.done("success")
            return

        ctlr.done("success")


class CTPPBuffer(UDLBuffer, XMLParsingBufferMixin):
    lang = lang

    # Делегируем UDL-семейства штатным движкам Komodo.
    m_lang = "HTML5"
    css_lang = "CSS"
    csl_lang = "JavaScript"
    tpl_lang = "CTPP"

    cb_show_if_empty = True

    # Совместимо с XML/HTML, CSS и JavaScript completion в смешанном файле.
    cpln_stop_chars = "'\" (;},~`@#%^&*()=+{}]|\\;,.<>?/"

    # ParenStyleCalltipIntelMixin должен знать, какие стили пропускать при
    # подсчёте аргументов. Не полагаемся на schemes.StateMap для addon-языка.
    def string_styles(self):
        return (SCE_UDL_TPL_STRING,)

    def comment_styles(self):
        return (SCE_UDL_TPL_COMMENT,)


class CTPPCILEDriver(UDLCILEDriver):
    """На 2.0/2.1 индексируем вложенные JavaScript/CSS штатными драйверами.

    Собственный CTPP CILE запланирован на версию 2.2.
    """

    lang = lang
    csl_lang = "JavaScript"
    css_lang = "CSS"


def _register_extension_langinfo(mgr):
    """Подключить langinfo_*.py из pylib расширения к уже созданной lidb.

    Manager CodeIntel создаёт default LangInfo Database *до* загрузки
    extra_module_dirs. Поэтому наличие pylib/langinfo_ctpp.py само по себе
    недостаточно: его нужно явно догрузить в существующую базу.
    """
    lidb = mgr.lidb

    try:
        lidb.langinfo_from_komodo_lang(lang, tryFallback=False)
        return
    except Exception:
        pass

    module_dir = os.path.dirname(__file__)
    lidb._load_dir(module_dir)
    if module_dir not in lidb.dirs:
        lidb.dirs.append(module_dir)

    # _load_dir() добавляет LangInfo-классы, но derived lookup tables могли
    # быть построены раньше. Сбрасываем только кеши; следующий lookup
    # штатно вызовет Database._build_tables().
    for attr in (
        "_langinfo_from_ext",
        "_langinfo_from_filename",
        "_langinfo_from_filename_re",
        "_magic_table",
        "_li_from_doctype_public_id",
        "_li_from_doctype_system_id",
        "_li_from_emacs_mode",
        "_li_from_vi_filetype",
        "_li_from_norm_komodo_lang",
    ):
        setattr(lidb, attr, None)

    # Fail loudly in the CodeIntel log if extension LangInfo still did not load.
    lidb.langinfo_from_komodo_lang(lang, tryFallback=False)


def register(mgr):
    """Зарегистрировать поддержку CTPP в CodeIntel."""
    _register_extension_langinfo(mgr)

    mgr.set_lang_info(
        lang,
        silvercity_lexer=CTPPLexer(),
        buf_class=CTPPBuffer,
        langintel_class=CTPPLangIntel,
        import_handler_class=None,
        cile_driver_class=CTPPCILEDriver,
        is_cpln_lang=True,
    )
