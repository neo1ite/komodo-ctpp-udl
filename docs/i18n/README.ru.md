# Поддержка языка CTPP для Komodo

[English](../../README.md) | **Русский**

Это расширение добавляет поддержку шаблонов **CTPP2 / CT++** в Komodo IDE и Komodo Edit.

Оно регистрирует язык `CTPP` для файлов `*.ctpp`, обеспечивает подсветку смешанных CTPP/HTML5/CSS/JavaScript-шаблонов и содержит UDL-поддержку для Underscore templates.

## Возможности

- отдельный язык `CTPP` в Komodo;
- подсветка синтаксиса `*.ctpp`;
- HTML5, CSS и JavaScript как вложенные языки внутри шаблонов;
- шаблоны новых CTPP-файлов;
- компоненты linter и Code Intelligence/CILE;
- отдельная иконка CTPP для файлов и элементов интерфейса языка;
- совместимость с Komodo IDE и Komodo Edit версий 6–9.

Полноценный современный Code Intelligence для CTPP пока не реализован.

## Установка

Установите XPI через менеджер дополнений Komodo.

После обновления промежуточной сборки полностью закройте Komodo и удалите startup cache:

```bash
rm -rf ~/.komodoide/9.3/XRE/startupCache
```

## Сборка

Komodo 9 поставляется со своим Python 2.7 — `mozpython`. На современных Linux-системах SDK следует запускать через runtime Komodo.

**Важно:** используйте `--unjarred`. По умолчанию SDK Komodo упаковывает `content/`, `skin/` и `locale/` внутрь `ctpp_language.jar`, а `chrome.manifest` данного расширения обращается к `chrome://ctpp/skin/languages.css` и `ctpp.svg` как к обычным chrome-каталогам. Поэтому для иконки языка требуется unjarred-сборка.

```bash
KOMODO_HOME="${KOMODO_HOME:-$HOME/Komodo-IDE-9}"

"$KOMODO_HOME/lib/mozilla/mozpython" \
    "$KOMODO_HOME/lib/sdk/bin/koext" build --unjarred
```

Успешная сборка версии 1.3 создаёт:

```text
ctpp_language-1.3-ko.xpi
```

В выводе сборки должны присутствовать отдельные каталоги `skin/` и `content/`, а файла `ctpp_language.jar` быть не должно.

## Иконка языка

Иконки файлов/вкладок CTPP разрешаются через файловый механизм Komodo. Список языков использует другой путь интерфейса: Komodo создаёт пункты с классом `languageicon` и атрибутом `language="CTPP"`.

Версия 1.3 подключает CTPP stylesheet непосредственно к основному chrome Komodo:

```text
style chrome://komodo/content/komodo.xul chrome://ctpp/skin/languages.css
```

`skin/languages.css` переопределяет изображение для `language="CTPP"`, а SVG расположен в `skin/ctpp.svg`.

XPI должен собираться через `koext build --unjarred`; иначе SDK помещает skin в JAR, и chrome URL выше не разрешается в упакованный stylesheet ожидаемым способом.

## Структура проекта

- `udl/` — UDL-описания и переходы между языковыми семействами;
- `components/` — регистрация языка и linter-компоненты;
- `pylib/` — интеграция Code Intelligence/CILE;
- `templates/` — шаблоны новых файлов;
- `skin/` — ресурсы интерфейса, включая `languages.css` и `ctpp.svg`;
- `content/` — прочие chrome-ресурсы при необходимости.

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

Если Code Intelligence выдаёт исключение при разборе постороннего JavaScript-файла, это отдельная проблема и не связано непосредственно с регистрацией языка CTPP.

## Лицензия

MIT License. См. [LICENSE](../../LICENSE).
