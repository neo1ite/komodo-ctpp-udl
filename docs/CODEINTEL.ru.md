# Дорожная карта Code Intelligence для CTPP

Канонической реализацией CTPP/CT++ считается `waaeer/ctpp`, CT++ 2.8.

## 2.0 — базовый CodeIntel
Статус: выпущено.

## 2.1 — CTPP expressions
Статус: выпущено. Acceptance matrix пройдена на Komodo IDE 9.3.2 build 88191.

## 2.2 — настоящий CILE
Статус: следующий этап.

Цели: реальный `cile_ctpp.py`, CIX для `TMPL_block`, аргументы `args(...)`, ссылки `TMPL_call`/`TMPL_include`, mixed JavaScript/CSS CILE, позиции и сигнатуры. Go to Definition остаётся на 2.3.

## 2.3 — Go to Definition
`TMPL_call` → `TMPL_block`, `TMPL_include` → файл.

## 2.4 — переменные
Локальные и runtime-переменные, аргументы блоков, `TMPL_foreach`.

## 2.5 — Code Browser / Symbols / project index
Проектный индекс, символы, определения/ссылки и навигация.
