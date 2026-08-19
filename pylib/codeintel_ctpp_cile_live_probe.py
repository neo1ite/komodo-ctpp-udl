#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Временный live-probe CTPP CILE для acceptance версии 2.2.

Модуль загружается CodeIntel Manager как ``codeintel_*.py`` и заменяет только
CILE driver для языка CTPP на диагностический subclass. Probe активируется
только для файла с basename ``cile-basic.ctpp`` и пишет результат фактического
scan, выполненного внутри работающего Komodo/CodeIntel backend, в /tmp.

После завершения acceptance 2.2 этот файл должен быть удалён перед релизом.
"""

from __future__ import print_function

import logging
import os

from codeintel2 import codeintel_ctpp

try:
    import ciElementTree as ET
except ImportError:
    from xml.etree import ElementTree as ET


log = logging.getLogger("codeintel.ctpp.liveprobe")
_TARGET_BASENAME = "cile-basic.ctpp"
_SUMMARY_PATH = "/tmp/komodo-ctpp-cile-live.txt"
_CIX_PATH = "/tmp/komodo-ctpp-cile-live.xml"


def _local_name(tag):
    if "}" in tag:
        return tag.rsplit("}", 1)[-1]
    return tag


def _collect(tree):
    blobs = {}
    file_elem = None

    for elem in list(tree):
        if _local_name(elem.tag) == "file":
            file_elem = elem
            break

    if file_elem is None:
        return blobs, [], []

    for elem in list(file_elem):
        if (_local_name(elem.tag) == "scope"
                and elem.get("ilk") == "blob"
                and elem.get("lang")):
            blobs[elem.get("lang")] = elem

    blocks = []
    refs = []
    ctpp = blobs.get("CTPP")
    if ctpp is not None:
        for elem in list(ctpp):
            name = elem.get("name")
            attrs = set((elem.get("attributes") or "").split())
            if (_local_name(elem.tag) == "scope"
                    and elem.get("ilk") == "function"):
                blocks.append(name)
            elif (_local_name(elem.tag) == "variable"
                    and "__ctpp_reference__" in attrs):
                refs.append(name)

    return blobs, sorted(blocks), sorted(refs)


def _write_probe(tree, path):
    blobs, blocks, refs = _collect(tree)
    blob_names = sorted(blobs)

    summary = (
        "CTPP CILE LIVE PROBE: OK\n"
        "path: %s\n"
        "blobs: %s\n"
        "blocks: %s\n"
        "refs: %s\n"
        % (
            path,
            ", ".join(blob_names),
            ", ".join(blocks),
            ", ".join(refs),
        )
    )

    with open(_SUMMARY_PATH, "wb") as stream:
        stream.write(summary.encode("utf-8"))

    xml = ET.tostring(tree, encoding="utf-8")
    if isinstance(xml, unicode):
        xml = xml.encode("utf-8")
    with open(_CIX_PATH, "wb") as stream:
        stream.write(xml)
        stream.write("\n")

    log.info(
        "CTPP CILE LIVE PROBE path=%r blobs=%r blocks=%r refs=%r",
        path, blob_names, blocks, refs)


class CTPPLiveProbeCILEDriver(codeintel_ctpp.CTPPCILEDriver):

    def scan_purelang(self, buf):
        tree = codeintel_ctpp.CTPPCILEDriver.scan_purelang(self, buf)
        path = getattr(buf, "path", None) or ""
        if os.path.basename(path) == _TARGET_BASENAME:
            try:
                _write_probe(tree, path)
            except Exception:
                log.exception("failed to write CTPP CILE live probe")
        return tree


def register(mgr):
    """Подменить только CILE driver; lexer/buffer/langintel остаются прежними."""
    mgr.set_lang_info(
        "CTPP",
        cile_driver_class=CTPPLiveProbeCILEDriver,
        is_cpln_lang=True,
    )
