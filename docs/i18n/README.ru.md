# Поддержка языка CTPP для Komodo

[English](../../README.md) | **Русский**

Это расширение добавляет поддержку шаблонов **CTPP2 / CT++** в Komodo IDE и Komodo Edit.

Оно регистрирует язык `CTPP` для файлов `*.ctpp`, обеспечивает подсветку синтаксиса смешанных CTPP/HTML5/CSS/JavaScript-шаблонов и содержит UDL-поддержку, используемую проектом для Underscore templates.

## Возможности

- отдельный язык `CTPP` в Komodo;
- подсветка синтаксиса `*.ctpp`;
- HTML5, CSS и JavaScript как вложенные языки внутри шаблонов;
- шаблоны новых CTPP-файлов;
- компоненты linter и Code Intelligence/CILE;
- отдельная иконка CTPP для файлов и элементов интерфейса языка;
- совместимость с Komodo IDE и Komodo Edit 6–9.

Полноценный современный Code Intelligence для CTPP пока не реализован.

## Установка

Установите XPI-пакет через менеджер дополнений Komodo.

После обновления расширения полностью закройте Komodo и удалите startup cache, а затем запустите Komodo снова:

```bash
rm -rf ~/.komodoide/9.3/XRE/startupCache
```

Для Komodo Edit используйте соответствующий каталог профиля, если он отличается в вашей системе.

## Сборка

Komodo 9 поставляется со своим Python 2.7 — `mozpython`. На современных Linux-системах команда `python` может отсутствовать, поэтому надёжный способ сборки выглядит так:

```bash
KOMODO_HOME="${KOMODO_HOME:-$HOME/Komodo-IDE-9}"

"$KOMODO_HOME/lib/mozilla/mozpython" \
    "$KOMODO_HOME/lib/sdk/bin/koext" build
```

Успешная сборка создаёт XPI примерно такого вида:

```text
ctpp_language-1.3-ko.xpi
```

## Иконка языка

В версии 1.3 `skin/languages.css` загружается в основной интерфейс Komodo через небольшой корректный XUL overlay. Одновременно stylesheet регистрируется через `agent-style-sheets` как резервный механизм.

```text
overlay chrome://komodo/content/komodo.xul chrome://ctpp/content/overlay.xul
category agent-style-sheets ctpp-language-icons chrome://ctpp/skin/languages.css
```

В overlay находится только объявление stylesheet и пустой корректный XUL-элемент `overlay`. Это принципиально отличается от одной из предыдущих неудачных ревизий, где `overlay.xul` был пустым и Komodo выдавал:

```text
no element found in chrome://ctpp/content/overlay.xul
Failed to load overlay from chrome://ctpp/content/overlay.xul
```

Сам SVG расположен в `skin/ctpp.svg`.

## Структура проекта

- `udl/` — UDL-описания и переходы между языковыми семействами;
- `components/` — регистрация языка и linter-компоненты;
- `pylib/` — интеграция Code Intelligence/CILE;
- `templates/` — шаблоны новых файлов;
- `skin/` — ресурсы интерфейса, включая `languages.css` и `ctpp.svg`;
- `content/` — chrome-ресурсы, включая overlay для иконки языка.

## Совместимость

Основная проверенная конфигурация:

- Komodo IDE 9.3.2;
- Linux x86_64.

`install.rdf` допускает Komodo IDE и Komodo Edit версий 6–9.

## Диагностика

Если после установки новой версии изменения не появились в интерфейсе, полностью закройте Komodo и удалите:

```text
~/.komodoide/9.3/XRE/startupCache
```

После этого запустите Komodo снова.

Если Code Intelligence выдаёт исключение при разборе постороннего JavaScript-файла, это отдельная проблема и не связано непосредственно с регистрацией языка CTPP; её следует разбирать по журналу Komodo отдельно.

## Лицензия

MIT License. См. [LICENSE](../../LICENSE).
