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

Используйте штатный скрипт репозитория:

```bash
./build.sh
```

По умолчанию используется `~/Komodo-IDE-9`. При необходимости путь можно переопределить:

```bash
KOMODO_HOME=/opt/Komodo-IDE-9 ./build.sh
```

Скрипт запускает собственный Python 2.7 и SDK Komodo:

```text
mozpython koext build --unjarred
```

Параметр `--unjarred` обязателен намеренно. По умолчанию SDK Komodo перемещает `content/`, `skin/` и `locale/` внутрь `ctpp_language.jar`, тогда как chrome manifest этого расширения адресует эти ресурсы как обычные каталоги расширения. Unjarred-сборка сохраняет корректную доступность chrome registrations и stylesheet иконки языка.

Успешная сборка версии 1.3 создаёт:

```text
ctpp_language-1.3-ko.xpi
```

## Иконка языка

Komodo 9 строит меню Languages динамически и назначает каждому пункту класс `languageicon` и атрибут `language`. Расширение предоставляет `skin/languages.css`, который заменяет иконку для `language="CTPP"` на `skin/ctpp.svg`.

Stylesheet загружается глобально через тот же механизм `agent-style-sheets`, который используется рабочим TypeScript-расширением:

```text
category agent-style-sheets ctpp-language-icons chrome://ctpp/skin/languages.css
```

Поэтому chrome-ресурсы должны реально присутствовать в установленном XPI; именно для этого поддерживаемая сборка использует `--unjarred`.

## Структура проекта

- `udl/` — UDL-описания и переходы между языковыми семействами;
- `components/` — регистрация языка и linter-компоненты;
- `pylib/` — интеграция Code Intelligence/CILE;
- `templates/` — шаблоны новых файлов;
- `skin/` — ресурсы интерфейса, включая `languages.css` и `ctpp.svg`;
- `content/` — прочие chrome-ресурсы при необходимости;
- `build.sh` — поддерживаемый способ сборки под Komodo 9.

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

При проблемах с иконкой проверьте, что XPI содержит `skin/languages.css` и `skin/ctpp.svg` как обычные каталоги верхнего уровня, а не только внутри `ctpp_language.jar`:

```bash
unzip -l ctpp_language-1.3-ko.xpi | grep -E 'skin/(languages\.css|ctpp\.svg)|ctpp_language\.jar'
```

## Лицензия

MIT License. См. [LICENSE](../../LICENSE).
