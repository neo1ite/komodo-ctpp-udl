# -*- coding: utf-8 -*-

"""LangInfo для CTPP."""

from langinfo import LangInfo


class CTPPLangInfo(LangInfo):
    name = "CTPP"
    komodo_name = "CTPP"
    conforms_to_bases = ["Text"]
    exts = [".ctpp"]
