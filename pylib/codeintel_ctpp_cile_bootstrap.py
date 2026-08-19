#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Загрузить CTPP CILE, пока активен extension import hook CodeIntel.

Manager Komodo временно устанавливает import hook только на время загрузки
``codeintel_*.py`` из extension pylib. Сам ``cile_ctpp.py`` по шаблону имени
автоматически не загружается. Этот маленький bootstrap импортирует его как
``codeintel2.cile_ctpp`` именно в тот момент, когда extension directory ещё
доступен import hook-у.

После этого ``CTPPCILEDriver.scan_purelang()`` может безопасно получить уже
загруженный модуль из ``codeintel2`` / ``sys.modules`` во встроенном Python 2.7.
"""

from codeintel2 import cile_ctpp  # noqa: F401
