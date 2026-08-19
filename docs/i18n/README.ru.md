# Поддержка языка CTPP для Komodo

[English](../../README.md) | **Русский**

Поддержка CTPP2 / CT++ для Komodo IDE/Edit: смешанные HTML5/CSS/JavaScript-шаблоны, линтинг и Code Intelligence.

- Подсветка CTPP, включая HTML-атрибуты и JavaScript-строки.
- Смешанные HTML5/CSS/JavaScript-шаблоны.
- HTML5-линтинг с предварительной обработкой CTPP.
- Code Intelligence 2.0: автодополнение `TMPL_*`.
- Code Intelligence 2.1: выражения CT++, встроенные функции, операторы, `foreach as`, `args(...)` и calltips.
- Идемпотентный менеджер патча autocomplete Komodo 9.

Дорожная карта: [docs/CODEINTEL.ru.md](../CODEINTEL.ru.md).

## Сборка

```bash
./build.sh
```

Версия 2.1 создаёт `ctpp_language-2.1-ko.xpi`. Полная acceptance matrix 2.1 проверена на Komodo IDE 9.3.2 build 88191.

## Лицензия

MIT License. См. [LICENSE](../../LICENSE).
