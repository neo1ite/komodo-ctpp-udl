# CILE / CIX для CTPP

Документ описывает архитектуру этапа Code Intelligence 2.2 для Komodo IDE 9.3.2.

## Зачем нужен CILE

Lexer и autocomplete знают, **как выглядит** CTPP-код и что можно предложить в текущей позиции. CILE решает другую задачу: строит семантическое представление файла в формате CIX, которое затем хранится в CodeIntel database.

Это основа для:

- списка структурных символов;
- определения областей и аргументов;
- последующего Go to Definition;
- межфайлового разрешения `TMPL_call` / `TMPL_include`;
- проектного индекса.

## Runtime

Komodo IDE 9.3.2 использует встроенный Python 2.7:

```text
$KOMODO_HOME/lib/mozilla/mozpython
```

Поэтому Python 2.7 является **обязательной** средой совместимости для:

- `pylib/codeintel_ctpp.py`;
- `pylib/cile_ctpp.py`;
- `pylib/langinfo_ctpp.py`.

Python 3 можно использовать только как дополнительный standalone smoke-test.

## CIX-модель 2.2

### `TMPL_block`

CTPP block отображается на стандартный CIX `scope ilk="function"`, потому что эта сущность CIX:

- имеет имя;
- имеет `line` / `lineend`;
- поддерживает `signature`;
- может содержать arguments.

Пример CTPP:

```ctpp
<TMPL_block 'card' args(title, body)>
    ...
</TMPL_block>
```

Концептуальный CIX:

```xml
<scope
    ilk="function"
    name="card"
    line="3"
    lineend="14"
    signature="TMPL_block 'card' args(title, body)"
    attributes="__ctpp_block__">

    <variable ilk="argument" name="title" />
    <variable ilk="argument" name="body" />
</scope>
```

Custom attribute `__ctpp_block__` позволяет отличить CTPP block от настоящей функции другого языка.

### `TMPL_call`

CIX 2.0 не имеет отдельной сущности reference. До реализации Go to Definition в 2.3 ссылка представляется как скрытая fabricated variable:

```xml
<variable
    name="card"
    line="16"
    attributes="__hidden__ __fabricated__ __ctpp_reference__ __ctpp_call__"
    doc="&lt;TMPL_call 'card' ...&gt;" />
```

Для dynamic call добавляется:

```text
__dynamic__
```

Пример:

```ctpp
<TMPL_call dynamic_block>
```

### `TMPL_include`

Аналогично хранится скрытая reference-запись с:

```text
__ctpp_include__
```

В 2.3 она станет входной точкой для перехода к включаемому файлу.

## Почему references не используют `ilk="reference"`

CIX разрешает произвольное значение optional `ilk` у variable, но generic Citadel/Code Browser не обязаны понимать новое значение. Поэтому 2.2 не вводит нестандартный ilk.

Reference определяется по custom attributes:

```text
__ctpp_reference__
__ctpp_call__
__ctpp_include__
__dynamic__
```

Такой вариант меньше вмешивается в generic CodeIntel и удобнее для 2.3.

## Mixed-language CIX

CTPP-файл является UDL-документом:

```text
M    -> HTML5
CSS  -> CSS
CSL  -> JavaScript
TPL  -> CTPP
```

В Komodo `UDLCILEDriver` при отсутствии SSL использует JavaScript CILE как master и CSS как slave.

`CTPPCILEDriver.scan_purelang()` в 2.2 делает два этапа:

```text
1. штатный UDLCILEDriver.scan_purelang(buf)
   -> JavaScript blob
   -> CSS blob

2. cile_ctpp.scan_buf(buf, tree=tree)
   -> добавляет CTPP blob в тот же CIX tree
```

Итоговая структура:

```xml
<codeintel version="2.0">
  <file lang="CTPP" path="...">
    <scope ilk="blob" lang="JavaScript" ... />
    <scope ilk="blob" lang="CSS" ... />
    <scope ilk="blob" lang="CTPP" ... />
  </file>
</codeintel>
```

## Scanner rules

`cile_ctpp.py`:

- распознаёт canonical `TMPL_*` case-insensitively;
- поддерживает `<-TMPL_...->` whitespace control;
- не считает `>` концом тега внутри строк, `()`, `[]`, `{}`;
- не индексирует содержимое `TMPL_comment`;
- не падает на незакрытом `TMPL_block` во время редактирования: `lineend` временно становится EOF, а block получает `__ctpp_unclosed__`;
- статический `TMPL_include` принимает только quoted filename;
- `TMPL_call 'name'` и `TMPL_call variable` различаются.

## Fixture

Основной fixture:

```text
tests/cile-basic.ctpp
```

Он содержит:

- static include;
- block `card` с arguments;
- JavaScript;
- CSS;
- static call;
- dynamic call;
- `TMPL_comment` с ложными сущностями, которые не должны попасть в индекс;
- второй block с expression `(x > 1 && y != 0)`.

## Обязательный smoke-test через Python 2.7 Komodo

```bash
./tests/cile-smoke.sh
```

Эквивалентный прямой запуск:

```bash
KOMODO_HOME="${KOMODO_HOME:-$HOME/Komodo-IDE-9}"

"$KOMODO_HOME/lib/mozilla/mozpython" \
    pylib/cile_ctpp.py tests/cile-basic.ctpp
```

Важно: успешный

```bash
python3 pylib/cile_ctpp.py tests/cile-basic.ctpp
```

не считается достаточной проверкой совместимости с Komodo.

## Проверка интеграции 2.2

После установки development XPI и полного перезапуска Komodo нужно проверить:

1. в логе нет Python 2 syntax/import exception для `cile_ctpp`;
2. обычный CTPP autocomplete 2.0/2.1 не регрессировал;
3. JavaScript CodeIntel внутри `<script>` работает;
4. CSS CodeIntel внутри `<style>` работает;
5. CTPP scan создаёт block `card` и `comparison`;
6. `title` и `body` находятся внутри scope `card` как arguments;
7. references `card`, `dynamic_block` и `includes/header.ctpp` присутствуют в CIX/database;
8. `ignored` / `ignored.ctpp` из `TMPL_comment` отсутствуют;
9. JavaScript/CSS blobs сохраняются вместе с CTPP blob.

## Граница 2.2 / 2.3

2.2 отвечает только за **построение и загрузку семантической модели**.

2.3 будет использовать эту модель для:

- `TMPL_call` → `TMPL_block`;
- `TMPL_include` → target file;
- межфайлового разрешения ссылок.
