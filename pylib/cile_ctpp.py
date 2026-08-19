#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""CILE scanner для CTPP / CT++ 2.8.

Основная среда выполнения — встроенный Python 2.7 Komodo IDE 9.3.2.
Код намеренно остаётся совместимым и с Python 3 для standalone smoke-test.

На этапе CodeIntel 2.2 scanner индексирует:

* определения ``TMPL_block`` и их ``args(...)``;
* ссылки ``TMPL_call``;
* ссылки ``TMPL_include``.

Go to Definition здесь намеренно не реализуется: это задача 2.3.
Runtime-переменные и ``TMPL_foreach`` locals относятся к 2.4.
"""

from __future__ import print_function

import io
import os
import re
import sys
import time

try:
    import ciElementTree as ET
except ImportError:
    # Только для автономного smoke-test вне Komodo.
    from xml.etree import ElementTree as ET

try:
    from codeintel2.common import CILEError
except ImportError:
    class CILEError(Exception):
        pass


__version__ = "2.2.0"


class CTPPCILEError(CILEError):
    pass


try:
    text_type = unicode
except NameError:
    text_type = str

try:
    binary_type = bytes
except NameError:
    binary_type = str


_TAG_START_RE = re.compile(
    r"<(?P<closing>/)?(?P<leading_dash>-)?TMPL_"
    r"(?P<name>[A-Za-z_][A-Za-z0-9_]*)\b",
    re.I,
)
_ARGS_RE = re.compile(r"\bargs\s*\(", re.I)
_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_DYNAMIC_TARGET_RE = re.compile(
    r"^[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*"
)


def _as_text(value):
    if isinstance(value, text_type):
        return value
    if isinstance(value, binary_type):
        return value.decode("utf-8", "replace")
    return text_type(value)


def _normalise_path(path):
    path = path or "<Unsaved>/CTPP.ctpp"
    if sys.platform.startswith("win"):
        path = path.replace("\\", "/")
    return path


def _line_from_offset(text, offset):
    """Вернуть 1-based номер строки без зависимости от byte/char offsets."""
    return text.count("\n", 0, offset) + 1


def _quote_signature_value(value):
    """Стабильно заключить значение в single quotes для CIX signature.

    Нельзя использовать ``%r``: Python 2 сериализует unicode как ``u'card'``,
    из-за чего один и тот же CTPP-файл получает разные signature в Py2/Py3.
    """
    value = _as_text(value)
    value = value.replace(u"\\", u"\\\\").replace(u"'", u"\\'")
    return u"'%s'" % value


def _find_tag_end(text, pos):
    """Найти закрывающий ``>`` CTPP-тега.

    ``>`` внутри строк, ``()``, ``[]`` и ``{}`` является частью expression и
    не завершает тег.
    """
    quote = None
    escaped = False
    paren = 0
    bracket = 0
    brace = 0

    while pos < len(text):
        ch = text[pos]

        if quote is not None:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == quote:
                quote = None
            pos += 1
            continue

        if ch in ("'", '"'):
            quote = ch
        elif ch == "(":
            paren += 1
        elif ch == ")":
            if paren:
                paren -= 1
        elif ch == "[":
            bracket += 1
        elif ch == "]":
            if bracket:
                bracket -= 1
        elif ch == "{":
            brace += 1
        elif ch == "}":
            if brace:
                brace -= 1
        elif ch == ">" and not (paren or bracket or brace):
            return pos

        pos += 1

    return None


def _iter_tags(text):
    pos = 0
    while True:
        match = _TAG_START_RE.search(text, pos)
        if match is None:
            return

        end = _find_tag_end(text, match.end())
        if end is None:
            # Незавершённый тег во время редактирования не должен ломать CILE.
            return

        body = text[match.end():end].rstrip()
        if body.endswith("-"):
            # trailing whitespace-control: <TMPL_var foo->
            body = body[:-1].rstrip()

        yield {
            "start": match.start(),
            "end": end + 1,
            "line": _line_from_offset(text, match.start()),
            "closing": bool(match.group("closing")),
            "name": match.group("name").lower(),
            "body": body,
            "raw": text[match.start():end + 1],
        }
        pos = end + 1


def _read_quoted_head(text):
    """Прочитать первый quoted value; вернуть ``(value, rest)`` или None."""
    text = text.lstrip()
    if not text or text[0] not in ("'", '"'):
        return None

    quote = text[0]
    out = []
    escaped = False
    pos = 1

    while pos < len(text):
        ch = text[pos]
        if escaped:
            out.append(ch)
            escaped = False
        elif ch == "\\":
            escaped = True
        elif ch == quote:
            return u"".join(out), text[pos + 1:]
        else:
            out.append(ch)
        pos += 1

    return None


def _find_matching_paren(text, open_pos):
    depth = 1
    quote = None
    escaped = False
    pos = open_pos + 1

    while pos < len(text):
        ch = text[pos]
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
                return pos
        pos += 1

    return None


def _split_top_level_commas(text):
    parts = []
    start = 0
    paren = 0
    bracket = 0
    brace = 0
    quote = None
    escaped = False

    for pos, ch in enumerate(text):
        if quote is not None:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == quote:
                quote = None
            continue

        if ch in ("'", '"'):
            quote = ch
        elif ch == "(":
            paren += 1
        elif ch == ")" and paren:
            paren -= 1
        elif ch == "[":
            bracket += 1
        elif ch == "]" and bracket:
            bracket -= 1
        elif ch == "{":
            brace += 1
        elif ch == "}" and brace:
            brace -= 1
        elif ch == "," and not (paren or bracket or brace):
            parts.append(text[start:pos].strip())
            start = pos + 1

    parts.append(text[start:].strip())
    return parts


def _extract_args(text, identifiers_only=False):
    match = _ARGS_RE.search(text)
    if match is None:
        return []

    open_pos = text.find("(", match.start())
    close_pos = _find_matching_paren(text, open_pos)
    if close_pos is None:
        return []

    values = [
        item for item in _split_top_level_commas(text[open_pos + 1:close_pos])
        if item
    ]

    if identifiers_only:
        return [item for item in values if _IDENTIFIER_RE.match(item)]
    return values


def _parse_block(tag):
    parsed = _read_quoted_head(tag["body"])
    if parsed is None:
        # Каноническая документация определяет block name quoted-строкой.
        return None

    name, rest = parsed
    if not name:
        return None
    args = _extract_args(rest, identifiers_only=True)
    return name, args


def _parse_call(tag):
    body = tag["body"].strip()
    parsed = _read_quoted_head(body)
    if parsed is not None:
        name, rest = parsed
        if not name:
            return None
        return name, False, _extract_args(rest)

    # Канонический CT++ допускает <TMPL_call some_var>.
    match = _DYNAMIC_TARGET_RE.match(body)
    if match is None:
        return None
    target = match.group(0)
    rest = body[match.end():]

    # После dynamic target допускаем только пустой хвост или args(...).
    if rest.strip() and _ARGS_RE.search(rest) is None:
        return None
    return target, True, _extract_args(rest)


def _parse_include(tag):
    # CT++ 2.8: include имеет ровно один quoted filename и не принимает var.
    parsed = _read_quoted_head(tag["body"])
    if parsed is None:
        return None
    filename, rest = parsed
    if not filename or rest.strip():
        return None
    return filename


def _local_name(tag):
    if "}" in tag:
        return tag.rsplit("}", 1)[-1]
    return tag


def _find_file_element(tree):
    for child in list(tree):
        if _local_name(child.tag) == "file":
            return child
    return None


def _remove_existing_ctpp_blob(file_elem, lang):
    for child in list(file_elem):
        if (_local_name(child.tag) == "scope"
                and child.get("ilk") == "blob"
                and child.get("lang") == lang):
            file_elem.remove(child)


def _prepare_tree(path, mtime, lang, tree=None):
    if tree is None:
        tree = ET.Element(
            "codeintel", version="2.0", xmlns="urn:activestate:cix:2.0")
        file_elem = ET.SubElement(
            tree,
            "file",
            lang=lang,
            path=path,
            mtime=str(mtime),
        )
    else:
        file_elem = _find_file_element(tree)
        if file_elem is None:
            file_elem = ET.SubElement(
                tree,
                "file",
                lang=lang,
                path=path,
                mtime=str(mtime),
            )
        else:
            # Multi-lang tree должен оставаться описанием исходного CTPP-файла.
            file_elem.set("lang", lang)
            file_elem.set("path", path)
            file_elem.set("mtime", str(mtime))

    _remove_existing_ctpp_blob(file_elem, lang)
    blob = ET.SubElement(
        file_elem,
        "scope",
        ilk="blob",
        lang=lang,
        name=os.path.basename(path),
        src=path,
    )
    return tree, file_elem, blob


def _add_reference(blob, kind, name, line, raw, dynamic=False):
    # CIX не имеет отдельного reference element. Используем скрытую fabricated
    # variable без нестандартного ilk: generic Citadel/Code Browser не обязаны
    # понимать новый ilk, а 2.3 сможет распознать ссылку по attributes.
    attributes = [
        "__hidden__",
        "__fabricated__",
        "__ctpp_reference__",
        "__ctpp_%s__" % kind,
    ]
    if dynamic:
        attributes.append("__dynamic__")

    ET.SubElement(
        blob,
        "variable",
        name=name,
        line=str(line),
        attributes=" ".join(attributes),
        doc=raw.strip(),
    )


def _scan_symbols(text, blob):
    block_stack = []
    comment_depth = 0
    last_line = text.count("\n") + 1

    for tag in _iter_tags(text):
        name = tag["name"]

        # TMPL_comment suppresses semantics of everything inside it.
        if name == "comment":
            if tag["closing"]:
                if comment_depth:
                    comment_depth -= 1
            else:
                comment_depth += 1
            continue
        if comment_depth:
            continue

        if tag["closing"]:
            if name == "block" and block_stack:
                scope = block_stack.pop()
                scope.set("lineend", str(tag["line"]))
            continue

        if name == "block":
            parsed = _parse_block(tag)
            if parsed is None:
                continue
            block_name, args = parsed

            signature = u"TMPL_block %s" % _quote_signature_value(block_name)
            if args:
                signature += u" args(%s)" % u", ".join(args)

            scope = ET.SubElement(
                blob,
                "scope",
                ilk="function",
                name=block_name,
                line=str(tag["line"]),
                signature=signature,
                attributes="__ctpp_block__",
            )
            for arg in args:
                ET.SubElement(scope, "variable", ilk="argument", name=arg)
            block_stack.append(scope)

        elif name == "call":
            parsed = _parse_call(tag)
            if parsed is None:
                continue
            target, dynamic, unused_args = parsed
            _add_reference(
                blob,
                "call",
                target,
                tag["line"],
                tag["raw"],
                dynamic=dynamic,
            )

        elif name == "include":
            filename = _parse_include(tag)
            if filename is not None:
                _add_reference(
                    blob,
                    "include",
                    filename,
                    tag["line"],
                    tag["raw"],
                )

    # Во время редактирования незакрытый блок индексируется до EOF.
    for scope in block_stack:
        scope.set("lineend", str(last_line))
        old = scope.get("attributes", "")
        scope.set("attributes", (old + " __ctpp_unclosed__").strip())


def scan_text(text, path, mtime=None, lang="CTPP", tree=None):
    """Просканировать raw CTPP text и вернуть CIX tree.

    Если ``tree`` передан, CTPP blob добавляется в уже построенный multi-lang
    CIX. Это сохраняет JavaScript/CSS CILE штатного UDL driver.
    """
    text = _as_text(text)
    path = _normalise_path(path)
    if mtime is None:
        mtime = int(time.time())

    tree, unused_file, blob = _prepare_tree(path, mtime, lang, tree=tree)
    _scan_symbols(text, blob)
    return tree


def scan_buf(buf, mtime=None, lang="CTPP", tree=None):
    """CILE entry point для ``CTPPBuffer`` Komodo."""
    path = _normalise_path(getattr(buf, "path", None))
    text = buf.accessor.text
    return scan_text(text, path, mtime=mtime, lang=lang, tree=tree)


def _write_stdout(data):
    """Записать UTF-8 XML одинаково в Python 2.7 и Python 3."""
    if isinstance(data, text_type):
        data = data.encode("utf-8")

    stream = getattr(sys.stdout, "buffer", None)
    if stream is None:
        # Python 2: sys.stdout принимает byte str.
        sys.stdout.write(data)
        sys.stdout.write("\n")
    else:
        stream.write(data)
        stream.write(b"\n")


def _main(argv):
    if len(argv) != 2:
        sys.stderr.write("usage: %s FILE.ctpp\n" % argv[0])
        return 2

    path = argv[1]
    with io.open(path, "r", encoding="utf-8", errors="replace") as stream:
        text = stream.read()
    tree = scan_text(text, path)
    _write_stdout(ET.tostring(tree, encoding="utf-8"))
    return 0


if __name__ == "__main__":
    sys.exit(_main(sys.argv))
