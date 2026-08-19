# Поддержка языка CTPP для Komodo

[English](../../README.md) | **Русский**

Это расширение добавляет поддержку шаблонов **CTPP2 / CT++** в Komodo IDE и Komodo Edit.

Оно регистрирует язык `CTPP` для файлов `*.ctpp`, обеспечивает подсветку смешанных CTPP/HTML5/CSS/JavaScript-шаблонов, поддержку Underscore templates, линтинг и интеграцию с Code Intelligence.

## Возможности

- отдельный язык `CTPP` в Komodo;
- подсветка синтаксиса `*.ctpp`;
- HTML5, CSS и JavaScript как вложенные языки внутри шаблонов;
- подсветка CTPP внутри HTML-атрибутов, атрибутов `<script>` и JavaScript-строк;
- подсветка Underscore templates в HTML- и JavaScript-контекстах;
- HTML5-линтинг с предварительной обработкой CTPP;
- **Code Intelligence 2.0:** регистрация CTPP в CodeIntel и автодополнение тегов `TMPL_*`;
- автоматическая передача уже открытого HTML5 autocomplete CTPP CodeIntel после распознавания `<TMPL_`/`</TMPL_`;
- штатный HTML5/CSS/JavaScript CodeIntel внутри смешанного CTPP-документа;
- шаблоны новых CTPP-файлов;
- отдельная иконка CTPP для файлов и элементов интерфейса языка;
- совместимость с Komodo IDE и Komodo Edit версий 6–9.

Следующие этапы CodeIntel — expressions, CILE, Go to Definition, переменные и Code Browser/project index — зафиксированы в [дорожной карте](../CODEINTEL.ru.md).

## Установка

Установите XPI через менеджер дополнений Komodo.

После обновления промежуточной сборки полностью закройте Komodo и удалите startup cache:

```bash
rm -rf ~/.komodoide/9.3/XRE/startupCache
```

После изменений CodeIntel важно полностью завершить Komodo, чтобы при следующем запуске был создан новый backend-процесс CodeIntel и заново загружены модули расширения из `pylib/`.

## Сборка

Komodo 9 поставляется со своим Python 2.7 — `mozpython`. На современных Linux-системах SDK следует запускать через runtime Komodo.

**Важно:** используйте `--unjarred`. Расширение использует chrome URL для `content/` и `skin/`; в версии 2.0 из `content/` также загружается небольшой UI-мост, который закрывает уже открытый HTML5 autocomplete и повторно запускает CodeIntel как CTPP после распознавания префикса `TMPL_`.

```bash
KOMODO_HOME="${KOMODO_HOME:-$HOME/Komodo-IDE-9}"

"$KOMODO_HOME/lib/mozilla/mozpython" \
    "$KOMODO_HOME/lib/sdk/bin/koext" build --unjarred
```

Успешная сборка версии 2.0 создаёт:

```text
ctpp_language-2.0-ko.xpi
```

В выводе сборки должны присутствовать отдельные каталоги `skin/` и `content/`, а файла `ctpp_language.jar` быть не должно.

## Code Intelligence 2.0

Версия 2.0 реализует первый рабочий слой CodeIntel для CTPP:

- отдельный `LangInfo` для `CTPP`;
- использование семейства `TPL_*` вместо оставшегося от генератора заглушечного `SSL_*`;
- автоматическое дополнение тегов после `<TMPL_` и после двух введённых символов имени;
- явное дополнение по `Ctrl+J` для частично введённого `TMPL_*`;
- дополнение контейнерных тегов в закрывающей форме `</TMPL_...>`;
- штатное HTML5/XML-дополнение в HTML-частях шаблона;
- делегирование JavaScript и CSS штатным CodeIntel/CILE-драйверам Komodo;
- передача активного HTML5 popup в CTPP popup, когда ввод превращается в незавершённый CTPP-тег.

Дополнение выражений внутри CTPP сознательно оставлено на версию 2.1.

## Иконка языка

Иконки файлов/вкладок CTPP разрешаются через файловый механизм Komodo. Список языков использует другой путь интерфейса: Komodo создаёт пункты с классом `languageicon` и атрибутом `language="CTPP"`.

Расширение подключает CTPP stylesheet непосредственно к основному chrome Komodo.

## Структура проекта

- `udl/` — UDL-описания и переходы между языковыми семействами;
- `components/` — регистрация языка и linter-компоненты;
- `pylib/` — Code Intelligence, LangInfo и будущая CILE-интеграция;
- `content/` — интеграция с UI Komodo, включая мост автодополнения CTPP;
- `templates/` — шаблоны новых файлов;
- `skin/` — ресурсы интерфейса, включая `languages.css` и `ctpp.svg`.

## Совместимость

Основная проверенная конфигурация:

- Komodo IDE 9.3.2 build 88191;
- Linux x86_64.

`install.rdf` допускает Komodo IDE и Komodo Edit версий 6–9.

## Диагностика

Если после установки промежуточной сборки изменения не появились в интерфейсе, полностью закройте Komodo и удалите:

```text
~/.komodoide/9.3/XRE/startupCache
```

После этого запустите Komodo снова.

Если после установки 2.0 остаётся старое состояние CodeIntel, убедитесь, что завершены все процессы Komodo: CodeIntel работает в отдельном backend-процессе и должен заново загрузить `pylib/` расширения.

## Лицензия

MIT License. См. [LICENSE](../../LICENSE).
