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

Komodo 9 поставляется со своим Python 2.7 — `mozpython`. На современных Linux-системах SDK следует запускать через runtime Komodo:

```bash
KOMODO_HOME="${KOMODO_HOME:-$HOME/Komodo-IDE-9}"

"$KOMODO_HOME/lib/mozilla/mozpython" \
    "$KOMODO_HOME/lib/sdk/bin/koext" build
```

Для версии 1.3 успешная сборка создаёт:

```text
ctpp_language-1.3-ko.xpi
```

## Иконка языка

Иконки файлов/вкладок CTPP разрешаются через файловый механизм `koicon://` Komodo. Список языков — другой путь интерфейса: Komodo создаёт language menu внутри `chrome://komodo/content/komodo.xul` и назначает сгенерированную `koicon://ko-language/CTPP` как inline style.

Поэтому версия 1.3 подключает CTPP stylesheet непосредственно к основному chrome Komodo через директиву `style` в chrome manifest:

```text
style chrome://komodo/content/komodo.xul chrome://ctpp/skin/languages.css
```

`skin/languages.css` переопределяет изображение для `language="CTPP"`, а сам SVG находится в `skin/ctpp.svg`.

Предыдущие промежуточные варианты с `agent-style-sheets` и XUL overlay для language-menu icon удалены.

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
