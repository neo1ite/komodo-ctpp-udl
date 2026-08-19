# Поддержка CTPP в Komodo

[English](../../README.md) | **Русский**

Расширение добавляет поддержку CTPP2 / CT++ в Komodo IDE и Komodo Edit.

Оно регистрирует язык `CTPP` для `*.ctpp`, поддерживает смешанные CTPP / HTML5 / CSS / JavaScript-шаблоны, Underscore templates, линтинг и Code Intelligence.

Каноническая реализация CTPP для проекта: **`waaeer/ctpp`, CT++ 2.8**.

## Состояние

- **Стабильный релиз:** 2.1 — expressions, встроенные функции, операторы и calltips.
- **Разработка:** 2.2 — настоящий CILE/CIX scanner для блоков, аргументов, вызовов и include.
- Основная проверенная среда: **Komodo IDE 9.3.2 build 88191, Linux x86_64**.
- CodeIntel Komodo 9 работает на встроенном **Python 2.7**; весь код в `pylib/` обязан оставаться совместимым с Python 2.7.

Документация:

- [дорожная карта Code Intelligence](../CODEINTEL.ru.md);
- [архитектура и тестирование CILE](../CILE.ru.md);
- [CHANGELOG](../../CHANGELOG.md).

## Возможности

### Поддержка языка

- отдельный язык `CTPP` для `*.ctpp`;
- подсветка канонических тегов `TMPL_*`;
- whitespace-control формы вроде `<-TMPL_var ...->`;
- CTPP внутри HTML-атрибутов, атрибутов `<script>` и JavaScript-строк;
- Underscore templates в HTML- и JavaScript-контекстах;
- HTML5-линтинг с предварительной маскировкой CTPP.

### Смешанный документ

Внутри одного CTPP-файла сохраняются штатные языковые сервисы Komodo:

- разметка → HTML5;
- `<style>` → CSS;
- `<script>` → JavaScript;
- CTPP-теги и expressions → CTPP.

### Code Intelligence 2.0

- явная регистрация CTPP в `LangInfo`;
- autocomplete тегов `TMPL_*`;
- autocomplete закрывающих контейнерных тегов;
- автоматическое дополнение и `Ctrl+J`;
- переключение HTML5 → CTPP при вводе `<TMPL_`.

### Code Intelligence 2.1

- встроенные функции CT++ 2.8;
- текстовые операторы `and`, `or`, `lt`, `le`, `gt`, `ge`, `eq`, `ne`, `mod`, `div`;
- символьные операторы;
- `TMPL_foreach ... as`;
- `args(...)` для `TMPL_block` / `TMPL_call`;
- штатные calltips Komodo;
- корректный lexer вложенных `()` / `[]`, включая `>` внутри expressions.

### Code Intelligence 2.2 — в разработке

- настоящий `cile_ctpp.py` вместо старой пустой CIX-заглушки;
- `TMPL_block` как CIX function scope;
- `args(...)` как CIX arguments;
- скрытые fabricated CIX references для `TMPL_call` и `TMPL_include`;
- единый mixed CIX с сохранением JavaScript/CSS blobs;
- позиции строк и сигнатуры для последующей навигации.

Go to Definition сознательно оставлен на 2.3.

## Установка

Установите XPI через менеджер дополнений Komodo.

После замены development-сборки полностью завершите Komodo и удалите startup cache:

```bash
rm -rf ~/.komodoide/9.3/XRE/startupCache
```

CodeIntel работает в отдельном backend-процессе, поэтому после изменений в `pylib/` нужен полный перезапуск Komodo.

## Патч autocomplete для Komodo 9

В Komodo 9 `ko.codeintel.trigger()` преждевременно завершает работу, если popup autocomplete уже открыт. HTML5 открывает список после `<`, и без патча Komodo не вычисляет новый CTPP trigger при переходе LexUDL на `<TMPL_`.

В репозитории есть идемпотентный менеджер патча:

```bash
./patch-komodo-codeintel.sh status
./patch-komodo-codeintel.sh install
./patch-komodo-codeintel.sh status

# Повторные операции безопасны:
./patch-komodo-codeintel.sh install
./patch-komodo-codeintel.sh uninstall
./patch-komodo-codeintel.sh uninstall
```

Перед `install` / `uninstall` Komodo должен быть полностью закрыт.

Эталонный raw patch:

```text
patches/komodo-9-codeintel-autocomplete-retrigger.patch
```

## Сборка

Используйте проектный wrapper:

```bash
./build.sh
```

Эквивалентная команда:

```bash
KOMODO_HOME="${KOMODO_HOME:-$HOME/Komodo-IDE-9}"

"$KOMODO_HOME/lib/mozilla/mozpython" \
    "$KOMODO_HOME/lib/sdk/bin/koext" build --unjarred
```

`--unjarred` обязателен: расширение регистрирует `content/`, `skin/` и связанные chrome-ресурсы как реальные каталоги расширения.

Development-версия 2.2 создаёт:

```text
ctpp_language-2.2-ko.xpi
```

## Smoke-test CILE

Авторитетная среда для проверки CILE — **встроенный Python 2.7 Komodo**, а не системный Python 3.

Основная команда:

```bash
./tests/cile-smoke.sh
```

Или напрямую:

```bash
KOMODO_HOME="${KOMODO_HOME:-$HOME/Komodo-IDE-9}"

"$KOMODO_HOME/lib/mozilla/mozpython" \
    pylib/cile_ctpp.py tests/cile-basic.ctpp
```

Запуск под Python 3 полезен как дополнительная проверка переносимости, но **не заменяет** тест через `mozpython`.

## Структура проекта

```text
components/        компоненты языка и линтера Komodo
pylib/             CodeIntel, LangInfo и CILE
udl/               исходники LexUDL
lexers/            скомпилированные lexer resources в build output
templates/         шаблоны новых CTPP-файлов
skin/              UI-ресурсы языка
patches/           проверяемые патчи ядра Komodo 9
tests/             fixtures и smoke-tests CILE
docs/              архитектура, roadmap и локализованная документация
```

Ключевые файлы:

- `pylib/codeintel_ctpp.py` — triggers, completions, calltips и CILE driver;
- `pylib/cile_ctpp.py` — scanner CTPP → CIX;
- `pylib/langinfo_ctpp.py` — статический LangInfo CTPP;
- `udl/ctpplex.udl` — состояния CTPP lexer;
- `patch-komodo-codeintel.sh` — идемпотентный менеджер патча Komodo 9.

## Совместимость

Основная цель:

- Komodo IDE 9.3.2 build 88191;
- Linux x86_64;
- встроенный Python 2.7 Komodo.

`install.rdf` допускает Komodo IDE / Edit 6–9, но разработка и acceptance выполняются на Komodo IDE 9.3.2.

## Диагностика

Состояние core-патча:

```bash
./patch-komodo-codeintel.sh status
```

После изменения CodeIntel убедитесь, что старых процессов Komodo не осталось, затем удалите:

```text
~/.komodoide/9.3/XRE/startupCache
```

Критичный regression marker в логах:

```text
Unable to retrieve langinfo for 'CTPP'
```

Текущие предупреждения Code Browser для generic HTML/CIX элементов отслеживаются отдельно и не смешиваются с milestone CTPP completion/CILE.

## Лицензия

MIT License. См. [LICENSE](../../LICENSE).
