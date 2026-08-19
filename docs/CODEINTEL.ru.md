# Дорожная карта Code Intelligence для CTPP

Code Intelligence развивается поэтапно, чтобы каждый релиз давал законченную и проверяемую функциональность, не смешивая автодополнение, семантический анализ и проектный индекс.

Канонической реализацией CTPP/CT++ для расширения считается `waaeer/ctpp` и описанный в `doc/template_language.rst` синтаксис CT++ 2.8. В частности, поддерживаются `TMPL_var`, `TMPL_if`, `TMPL_elsif`, `TMPL_else`, `TMPL_unless`, `TMPL_foreach`, `TMPL_include`, `TMPL_comment`, `TMPL_block`, `TMPL_call`, `TMPL_verbose` и `TMPL_break`; `TMPL_loop` и `TMPL_udf` в этот диалект не входят.

## 2.0 — базовый CodeIntel

Статус: реализуется в ветке `codeintel-2.0`.

Цели:

- зарегистрировать `CTPP` в LangInfo/CodeIntel без предупреждений;
- перевести CTPP CodeIntel с ошибочного `SSL_*` на фактическое семейство `TPL_*`;
- добавить автодополнение `TMPL_*`;
- поддержать автоматическое дополнение и `Ctrl+J`;
- корректно передавать открытый HTML5 autocomplete CTPP CodeIntel после распознавания префикса `<TMPL_`/`</TMPL_`;
- не сломать штатный HTML5/CSS/JavaScript CodeIntel в смешанных шаблонах;
- оставить собственный CILE CTPP за рамками этого релиза.

Проверка в Komodo 9.3.2:

1. В логе нет `Unable to retrieve langinfo for 'CTPP'`.
2. При вводе `<` работает штатный HTML5 autocomplete, а после полного префикса `<TMPL_` он автоматически заменяется списком CTPP-тегов без ложной HTML-lint ошибки.
3. После `<TMPL_va` список фильтруется до `TMPL_var`.
4. `Ctrl+J` работает на частично введённом `<TMPL_...`.
5. После `</TMPL_` предлагаются только контейнерные теги.
6. HTML5 autocomplete продолжает работать в HTML-разметке.
7. JavaScript autocomplete продолжает работать внутри `<script>`.
8. CSS autocomplete продолжает работать внутри `<style>`.
9. Поддерживается CT++ whitespace-control форма `<-TMPL_var ...->`.

## 2.1 — CTPP expressions

Автодополнение операторов, встроенных функций и выражений внутри параметров `TMPL_if`, `TMPL_var`, `TMPL_call`, `TMPL_foreach` и других CTPP-конструкций; calltips там, где сигнатура известна.

## 2.2 — настоящий CILE

Разбор CTPP в CIX: определения именованных `TMPL_block`, их аргументы, а также ссылки из `TMPL_call` и `TMPL_include`. Остальные индексируемые сущности будут добавляться только если они существуют в каноническом диалекте `waaeer/ctpp`.

## 2.3 — Go to Definition

Переходы от `TMPL_call` к `TMPL_block`, от `TMPL_include` к файлам и дальнейшее межфайловое разрешение ссылок.

## 2.4 — переменные

Локальные переменные, аргументы блоков, контекст `TMPL_foreach` и данные, выводимые из шаблона; отдельная стратегия для runtime-переменных, приходящих в CTPP извне.

## 2.5 — Code Browser / Symbols / project index

Полноценный проектный индекс CTPP, символы в Code Browser, поиск определений/ссылок и навигация по крупному набору шаблонов.
