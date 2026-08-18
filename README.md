# CTPP language support for Komodo

Расширение добавляет поддержку шаблонов **CTPP2 / CT++** в Komodo IDE и Komodo Edit.

Поддерживаются файлы `*.ctpp`, смешанная разметка HTML5, CSS и JavaScript, а также шаблонные конструкции CTPP. В проект также входят UDL-описания для интеграции с Underscore templates.

## Возможности

- отдельный язык `CTPP` в Komodo;
- подсветка синтаксиса CTPP в `*.ctpp`;
- поддержка HTML5/CSS/JavaScript внутри шаблонов;
- шаблоны новых CTPP-файлов;
- компоненты для lint/code intelligence;
- отдельная иконка языка CTPP в интерфейсе Komodo;
- поддержка Komodo IDE и Komodo Edit версий 6–9.

Полноценный современный Code Intelligence для CTPP пока не реализован.

## Установка

Соберите XPI или используйте готовый пакет релиза, после чего установите его через менеджер дополнений Komodo.

После обновления расширения рекомендуется полностью закрыть Komodo и удалить startup cache:

```bash
rm -rf ~/.komodoide/9.3/XRE/startupCache
```

Затем запустите Komodo снова.

## Сборка

Komodo 9 поставляется со своим Python 2.7 (`mozpython`). На современных Linux-системах команда `python` часто отсутствует, поэтому надёжный способ сборки выглядит так:

```bash
/home/neolite/Komodo-IDE-9/lib/mozilla/mozpython \
    /home/neolite/Komodo-IDE-9/lib/sdk/bin/koext build
```

Если Komodo установлен в другом каталоге, замените `/home/neolite/Komodo-IDE-9` на свой путь.

Успешная сборка создаёт файл примерно такого вида:

```text
ctpp_language-1.3-ko.xpi
```

## Иконка языка

Начиная с версии 1.3 иконка CTPP подключается через штатную категорию `agent-style-sheets`, без XUL overlay.

Это важно для Komodo 9: старый вариант с пустым `overlay.xul` мог приводить к ошибкам загрузки вида:

```text
no element found in chrome://ctpp/content/overlay.xul
Failed to load overlay from chrome://ctpp/content/overlay.xul
```

CSS для иконки расположен в `content/languages.css`, а сам SVG — в `skin/ctpp.svg`.

## Структура проекта

- `udl/` — UDL-описания и переходы между языковыми семействами;
- `components/` — регистрация языка и linter-компоненты;
- `pylib/` — Code Intelligence/CILE-интеграция;
- `templates/` — шаблоны новых файлов;
- `content/` — ресурсы, загружаемые через chrome package;
- `skin/` — визуальные ресурсы, включая `ctpp.svg`.

## Совместимость

Основная проверенная конфигурация:

- Komodo IDE 9.3.2;
- Linux x86_64.

Расширение по `install.rdf` также допускает Komodo IDE/Edit 6–9.

## Лицензия

MIT License. См. `LICENSE`.
