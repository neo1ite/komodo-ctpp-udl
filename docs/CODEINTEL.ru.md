# Дорожная карта Code Intelligence для CTPP

Канонической реализацией CTPP/CT++ для расширения считается `waaeer/ctpp`, CT++ 2.8.

Основная среда acceptance: Komodo IDE 9.3.2 build 88191, Linux x86_64. CodeIntel работает на встроенном Python 2.7 Komodo.

## 2.0 — базовый CodeIntel

Статус: **выпущено**.

Реализовано:

- явная регистрация `CTPP` в LangInfo/CodeIntel;
- фактическое UDL-семейство `TPL_*`;
- autocomplete `TMPL_*`;
- closing completion для контейнерных тегов;
- automatic completion и `Ctrl+J`;
- HTML5 → CTPP handoff на `<TMPL_`;
- сохранены HTML5/CSS/JavaScript CodeIntel в mixed-файле;
- whitespace-control `<-TMPL_...->`.

Komodo 9 требует core-патч `ko.codeintel.trigger()`. Идемпотентный менеджер находится в `patch-komodo-codeintel.sh`.

## 2.0.1 — release-engineering hotfix

Статус: **выпущено**.

- исправлен быстрый `install → uninstall` patch manager;
- JAR replacement больше не зависит от ZIP timestamps;
- `build.sh` и patch manager исполняемые.

## 2.1 — CTPP expressions

Статус: **выпущено**.

Реализовано:

- встроенные функции CT++ 2.8;
- текстовые операторы `and`, `or`, `lt`, `le`, `gt`, `ge`, `eq`, `ne`, `mod`, `div`;
- символьные операторы;
- `TMPL_foreach ... as`;
- `args(...)` в `TMPL_block` / `TMPL_call`;
- штатные calltips Komodo;
- lexer вложенных `()` / `[]`, включая `>` / `>=` внутри expressions;
- runtime variables/member completion сознательно оставлены на 2.4.

Acceptance matrix полностью пройдена на Komodo IDE 9.3.2 build 88191, включая regression HTML5/JavaScript/CSS и CTPP внутри HTML attributes / JavaScript strings.

## 2.2 — настоящий CILE / CIX

Статус: **в разработке в `codeintel-2.2`**.

Цель — превратить CTPP из языка с lexer/autocomplete в настоящий Citadel/CIX language, сохранив mixed JavaScript/CSS indexing.

### Реализуемые сущности

#### `TMPL_block`

Индексируется как:

```text
CIX scope ilk="function"
attributes="__ctpp_block__"
```

Сохраняются:

- `name`;
- `line`;
- `lineend`;
- `signature`;
- `args(...)` как `variable ilk="argument"`.

#### `TMPL_call`

Создаётся скрытая fabricated reference-variable с custom attributes:

```text
__ctpp_reference__
__ctpp_call__
```

Для `TMPL_call dynamic_var` дополнительно:

```text
__dynamic__
```

#### `TMPL_include`

Создаётся скрытая fabricated reference-variable:

```text
__ctpp_reference__
__ctpp_include__
```

### Mixed CILE

`CTPPCILEDriver.scan_purelang()`:

1. выполняет штатный `UDLCILEDriver.scan_purelang()`;
2. сохраняет JavaScript master CILE;
3. сохраняет CSS slave CILE;
4. добавляет CTPP blob в тот же CIX tree через `cile_ctpp.scan_buf(..., tree=tree)`.

Подробности: [CILE.ru.md](CILE.ru.md).

### Python 2.7

Для 2.2 обязательна проверка именно встроенным runtime Komodo:

```bash
./tests/cile-smoke.sh
```

или:

```bash
~/Komodo-IDE-9/lib/mozilla/mozpython \
    pylib/cile_ctpp.py tests/cile-basic.ctpp
```

Успешный Python 3 standalone test — только дополнительный сигнал.

### Acceptance matrix 2.2

1. `./build.sh` собирает `ctpp_language-2.2-ko.xpi`.
2. `./tests/cile-smoke.sh` проходит под Komodo `mozpython` Python 2.7.
3. В логе нет import/syntax exception `codeintel_ctpp` / `cile_ctpp`.
4. CIX содержит CTPP blob.
5. Block `card` индексируется как function scope.
6. `title` / `body` индексируются как arguments scope `card`.
7. `line` / `lineend` блока корректны.
8. Static call `card` присутствует как hidden reference.
9. Dynamic call `dynamic_block` присутствует и отмечен `__dynamic__`.
10. Include `includes/header.ctpp` присутствует как hidden reference.
11. `ignored` / `ignored.ctpp` внутри `TMPL_comment` отсутствуют.
12. Block `comparison` корректно переживает expression `(x > 1 && y != 0)`.
13. JavaScript blob сохраняется.
14. CSS blob сохраняется.
15. HTML5/JavaScript/CSS/CTPP autocomplete 2.0/2.1 не регрессирует.

## 2.3 — Go to Definition

Цели:

- `TMPL_call` → соответствующий `TMPL_block`;
- `TMPL_include` → target file;
- static references между файлами;
- корректный fallback для dynamic call, который нельзя разрешить статически.

2.3 строится поверх references и block scopes из CILE 2.2.

## 2.4 — переменные

Цели:

- block arguments;
- locals `TMPL_foreach`;
- iterator attributes;
- runtime-переменные, приходящие в шаблон извне;
- member completion `foo.bar`.

## 2.5 — Code Browser / Symbols / project index

Цели:

- полноценные CTPP symbols;
- Code Browser без generic warning noise;
- проектный индекс;
- поиск definitions/references;
- навигация по крупному набору шаблонов.
