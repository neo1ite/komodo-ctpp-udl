#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Проверить настоящий mixed CILE pipeline без SDK XPCOM bootstrap.

Komodo 9 SDK `codeintel` на некоторых Linux-сборках не запускается из-за
несовместимого `ciElementTree.so` (PyUnicodeUCS2_Decode). Этот тест проверяет
нужный нам pipeline Manager -> UDLBuffer -> CTPPCILEDriver отдельно от этой
проблемы SDK.

Важно: тест выполняется встроенным mozpython (Python 2.7), вручную подключает
Komodo Python library roots, отключает PyXPCOM и подставляет стандартный
ElementTree вместо бинарного ciElementTree.
"""

from __future__ import print_function

import os
import sys
import tempfile

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PYLIB_DIR = os.path.join(ROOT_DIR, "pylib")
LEXER_DIR = os.path.join(ROOT_DIR, "build", "lexers")
FIXTURE = os.path.join(ROOT_DIR, "tests", "cile-basic.ctpp")
KOMODO_HOME = os.environ.get(
    "KOMODO_HOME", os.path.expanduser("~/Komodo-IDE-9"))
KOMODO_PYTHON = os.path.join(KOMODO_HOME, "lib", "mozilla", "python")
KOMODO_PYTHON_KOMODO = os.path.join(KOMODO_PYTHON, "komodo")

if not os.path.exists(os.path.join(LEXER_DIR, "CTPP.lexres")):
    raise SystemExit("build/lexers/CTPP.lexres not found; run ./build.sh first")

manager_path = os.path.join(KOMODO_PYTHON_KOMODO, "codeintel2", "manager.py")
if not os.path.exists(manager_path):
    raise SystemExit("Komodo codeintel2/manager.py not found: %s" % manager_path)

# Standalone mozpython starts with a much smaller sys.path than the running
# Komodo application. The SDK helper normally prepares these paths itself,
# but that helper crashes on ciElementTree.so before CodeIntel starts.
for path in (KOMODO_PYTHON, KOMODO_PYTHON_KOMODO):
    if path not in sys.path:
        sys.path.insert(0, path)

# Не даём standalone Manager подхватить PyXPCOM: SDK helper ломается раньше
# запуска CodeIntel на данной Komodo 9 Linux installation.
os.environ["CODEINTEL_NO_PYXPCOM"] = "1"

# Встроенный ciElementTree.so этой SDK installation ABI-несовместим с
# standalone mozpython. Код CodeIntel импортирует модуль по имени напрямую,
# поэтому для smoke-test заранее предоставляем совместимый ElementTree API.
from xml.etree import ElementTree as StdET
sys.modules["ciElementTree"] = StdET

from codeintel2.manager import Manager
from codeintel2.udl import UDLLexer


def local_name(tag):
    if "}" in tag:
        return tag.rsplit("}", 1)[-1]
    return tag


def find_file(tree):
    for elem in list(tree):
        if local_name(elem.tag) == "file":
            return elem
    return None


def blob_map(tree):
    file_elem = find_file(tree)
    if file_elem is None:
        raise AssertionError("CIX file element not found")
    result = {}
    for elem in list(file_elem):
        if (local_name(elem.tag) == "scope"
                and elem.get("ilk") == "blob"
                and elem.get("lang")):
            result[elem.get("lang")] = elem
    return result


def attrs(elem):
    return set((elem.get("attributes") or "").split())


def main():
    with open(FIXTURE, "rb") as stream:
        content = stream.read()

    # В standalone-режиме UDL не знает extension lexer directory автоматически.
    UDLLexer.add_extra_lexer_dirs([LEXER_DIR])

    db_dir = tempfile.mkdtemp(prefix="ctpp-codeintel-")
    mgr = Manager(db_base_dir=db_dir, extra_module_dirs=[PYLIB_DIR])
    try:
        buf = mgr.buf_from_content(
            content,
            "CTPP",
            path=FIXTURE,
            encoding="utf-8",
        )
        driver = mgr.citadel.cile_driver_from_lang("CTPP")
        tree = driver.scan_purelang(buf)

        blobs = blob_map(tree)
        required = set(("CTPP", "JavaScript", "CSS"))
        missing = required.difference(blobs)
        if missing:
            raise AssertionError(
                "mixed CIX blobs missing: %r; got: %r" %
                (sorted(missing), sorted(blobs)))

        ctpp = blobs["CTPP"]
        scopes = dict(
            (elem.get("name"), elem)
            for elem in list(ctpp)
            if local_name(elem.tag) == "scope"
            and elem.get("ilk") == "function"
        )
        if set(scopes) != set(("card", "comparison")):
            raise AssertionError("unexpected CTPP scopes: %r" % sorted(scopes))

        card = scopes["card"]
        if card.get("signature") != "TMPL_block 'card' args(title, body)":
            raise AssertionError("wrong card signature: %r" % card.get("signature"))

        refs = [
            elem for elem in list(ctpp)
            if local_name(elem.tag) == "variable"
            and "__ctpp_reference__" in attrs(elem)
        ]
        ref_names = set(elem.get("name") for elem in refs)
        expected_refs = set(("includes/header.ctpp", "card", "dynamic_block"))
        if ref_names != expected_refs:
            raise AssertionError("unexpected CTPP references: %r" % sorted(ref_names))

        xml = StdET.tostring(tree, encoding="utf-8")
        if b"ignored.ctpp" in xml or b'name="ignored"' in xml:
            raise AssertionError("TMPL_comment content leaked into mixed CIX")

        print("Mixed CILE smoke test: OK")
        print("runtime: %s" % sys.executable)
        print("python: %s" % sys.version.split()[0])
        print("codeintel2: %s" % manager_path)
        print("blobs: %s" % ", ".join(sorted(blobs)))
        print("fixture: %s" % FIXTURE)
        return 0
    finally:
        try:
            mgr.finalize()
        except Exception:
            pass


if __name__ == "__main__":
    sys.exit(main())
