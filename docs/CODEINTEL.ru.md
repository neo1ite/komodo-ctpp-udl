# Дорожная карта Code Intelligence для CTPP

Канонической реализацией CTPP/CT++ считается `waaeer/ctpp`, CT++ 2.8.

## 2.0 — базовый CodeIntel
Статус: выпущено.

## 2.1 — CTPP expressions
Статус: выпущено. Acceptance matrix пройдена на Komodo IDE 9.3.2 build 88191.

## 2.2 — настоящий CILE
Статус: реализуется в ветке `codeintel-2.2`.

Первый слой scanner реализован в `pylib/cile_ctpp.py`:

- реальный разбор CT++-тегов вместо пустого CIX stub;
- `TMPL_block 'name' args(...)` → CIX `scope ilk="function"`;
- аргументы блока → `variable ilk="argument"`;
- `TMPL_call` → скрытая CIX reference-запись;
- `TMPL_include` → скрытая CIX reference-запись;
- статические и dynamic `TMPL_call some_var` различаются;
- корректные 1-based `line`/`lineend`;
- `>` внутри строк, `()`, `[]`, `{}` не завершает CTPP-тег;
- содержимое `TMPL_comment` не индексируется;
- scanner умеет добавлять CTPP blob в уже существующий multi-lang CIX, не уничтожая JavaScript/CSS blobs;
- есть автономный smoke-test режим и fixture `tests/cile-basic.ctpp`.

Следующий шаг 2.2 — подключить scanner к `CTPPCILEDriver.scan_purelang()` после штатного JavaScript/CSS multi-lang scan.

Проверка первого слоя:

1. `python3 pylib/cile_ctpp.py tests/cile-basic.ctpp` выдаёт валидный CIX.
2. В CIX есть blocks `card` и `comparison`, но нет закомментированного `ignored`.
3. У `card` есть arguments `title`, `body` и корректный `lineend`.
4. Есть static call reference `card` и dynamic call reference `dynamic_block`.
5. Есть include reference `includes/header.ctpp`.
6. Выражение `(x > 1 && y != 0)` не ломает scanner.

После интеграции с CTPPCILEDriver отдельно проверяем сохранность JavaScript/CSS CILE и загрузку CTPP blob в CodeIntel database.

## 2.3 — Go to Definition
`TMPL_call` → `TMPL_block`, `TMPL_include` → файл.

## 2.4 — переменные
Локальные и runtime-переменные, аргументы блоков, `TMPL_foreach`.

## 2.5 — Code Browser / Symbols / project index
Проектный индекс, символы, определения/ссылки и навигация.
