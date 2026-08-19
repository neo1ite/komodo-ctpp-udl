#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Структурный smoke-test CTPP CILE.

Запускается встроенным mozpython Komodo 9 (Python 2.7). Проверяет дерево CIX,
а не сериализованную строку XML, поэтому не зависит от порядка атрибутов,
который различается между ciElementTree/Python 2 и ElementTree/Python 3.
"""

from __future__ import print_function

import io
import os
import sys


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PYLIB_DIR = os.path.join(ROOT_DIR, "pylib")
FIXTURE = os.path.join(ROOT_DIR, "tests", "cile-basic.ctpp")

sys.path.insert(0, PYLIB_DIR)
try:
    import cile_ctpp
finally:
    del sys.path[0]


def fail(message):
    raise AssertionError(message)


def attrs(elem):
    return set((elem.get("attributes") or "").split())


def find_blob(tree, lang):
    for file_elem in list(tree):
        if cile_ctpp._local_name(file_elem.tag) != "file":
            continue
        for child in list(file_elem):
            if (cile_ctpp._local_name(child.tag) == "scope"
                    and child.get("ilk") == "blob"
                    and child.get("lang") == lang):
                return child
    return None


def function_scopes(blob):
    return dict(
        (child.get("name"), child)
        for child in list(blob)
        if (cile_ctpp._local_name(child.tag) == "scope"
            and child.get("ilk") == "function")
    )


def reference_vars(blob):
    result = []
    for child in list(blob):
        if cile_ctpp._local_name(child.tag) != "variable":
            continue
        if "__ctpp_reference__" in attrs(child):
            result.append(child)
    return result


def main():
    with io.open(FIXTURE, "r", encoding="utf-8", errors="replace") as stream:
        text = stream.read()

    tree = cile_ctpp.scan_text(text, FIXTURE, mtime=1)
    blob = find_blob(tree, "CTPP")
    if blob is None:
        fail("CTPP blob not found")

    scopes = function_scopes(blob)
    if set(scopes) != set(("card", "comparison")):
        fail("unexpected block scopes: %r" % sorted(scopes))

    card = scopes["card"]
    if card.get("line") != "3" or card.get("lineend") != "14":
        fail("card line range is wrong: %r..%r" % (
            card.get("line"), card.get("lineend")))
    if card.get("signature") != "TMPL_block 'card' args(title, body)":
        fail("card signature is wrong: %r" % card.get("signature"))
    if "__ctpp_block__" not in attrs(card):
        fail("card has no __ctpp_block__ marker")

    arguments = [
        child.get("name")
        for child in list(card)
        if (cile_ctpp._local_name(child.tag) == "variable"
            and child.get("ilk") == "argument")
    ]
    if arguments != ["title", "body"]:
        fail("card arguments are wrong: %r" % arguments)

    comparison = scopes["comparison"]
    if comparison.get("line") != "26" or comparison.get("lineend") != "30":
        fail("comparison line range is wrong: %r..%r" % (
            comparison.get("line"), comparison.get("lineend")))
    if comparison.get("signature") != "TMPL_block 'comparison'":
        fail("comparison signature is wrong: %r" % comparison.get("signature"))

    references = reference_vars(blob)
    by_name = dict((ref.get("name"), ref) for ref in references)
    expected = set(("includes/header.ctpp", "card", "dynamic_block"))
    if set(by_name) != expected:
        fail("unexpected references: %r" % sorted(by_name))

    include = by_name["includes/header.ctpp"]
    if "__ctpp_include__" not in attrs(include):
        fail("include reference marker is missing")

    static_call = by_name["card"]
    if "__ctpp_call__" not in attrs(static_call):
        fail("static call marker is missing")
    if "__dynamic__" in attrs(static_call):
        fail("static call marked as dynamic")

    dynamic_call = by_name["dynamic_block"]
    if not set(("__ctpp_call__", "__dynamic__")).issubset(attrs(dynamic_call)):
        fail("dynamic call markers are missing")

    for ref in references:
        if ref.get("ilk") is not None:
            fail("reference uses non-generic CIX ilk: %r" % ref.get("ilk"))
        if "__fabricated__" not in attrs(ref) or "__hidden__" not in attrs(ref):
            fail("reference is not hidden/fabricated: %r" % ref.get("name"))

    serialized = cile_ctpp.ET.tostring(tree, encoding="utf-8")
    if b"ignored.ctpp" in serialized or b'name="ignored"' in serialized:
        fail("TMPL_comment content leaked into CIX")

    print("CILE smoke test: OK")
    print("runtime: %s" % sys.executable)
    print("python: %s" % sys.version.split()[0])
    print("fixture: %s" % FIXTURE)
    return 0


if __name__ == "__main__":
    sys.exit(main())
