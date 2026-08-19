# История изменений

Формат ведётся по версиям расширения. Канонический диалект CTPP — `waaeer/ctpp`, CT++ 2.8.

## 2.2 — в разработке

### CILE / CIX

- заменена пустая CILE-заглушка на реальный scanner `pylib/cile_ctpp.py`;
- `TMPL_block 'name' args(...)` индексируется как CIX function scope;
- аргументы блока индексируются как `variable ilk="argument"`;
- `TMPL_call` и `TMPL_include` представлены скрытыми fabricated CIX references;
- static и dynamic `TMPL_call` различаются;
- сохраняются `line`, `lineend` и `signature`;
- `TMPL_comment` исключается из семантического индекса;
- `>` внутри строк и вложенных `()` / `[]` / `{}` не завершает CTPP-тег;
- CTPP blob добавляется в mixed CIX после штатного JavaScript/CSS scan;
- основной runtime для CILE зафиксирован как встроенный Python 2.7 Komodo 9;
- добавлены CILE fixture и smoke-test через `mozpython`.

### Документация

- восстановлена полноценная структура README;
- синхронизирована русская версия README;
- добавлена отдельная документация по CILE;
- добавлен этот CHANGELOG.

## 2.1 — 2026-08-19

### Code Intelligence

- автодополнение встроенных функций CT++ 2.8;
- текстовые и символьные операторы expressions;
- поддержка `TMPL_foreach ... as`;
- `args(...)` для `TMPL_block` и `TMPL_call`;
- штатные calltips Komodo для built-ins и `args(...)`;
- корректная обработка вложенных `()` / `[]` и операторов сравнения внутри CTPP;
- expression completion ограничен документированными CTPP-контекстами;
- runtime variables и member completion сознательно оставлены на 2.4.

Полная acceptance matrix пройдена на Komodo IDE 9.3.2 build 88191.

## 2.0.1 — 2026-08-19

- исправлен идемпотентный `uninstall` в `patch-komodo-codeintel.sh`;
- замена записи `codeintel.js` в JAR больше не зависит от ZIP timestamps;
- `build.sh` и `patch-komodo-codeintel.sh` сделаны исполняемыми;
- семантика CTPP CodeIntel 2.0 не менялась.

## 2.0 — 2026-08-19

### Code Intelligence

- отдельный CTPP `LangInfo`;
- CodeIntel переведён на фактическое UDL-семейство `TPL_*`;
- autocomplete `TMPL_*` тегов;
- completion закрывающих контейнерных тегов;
- автоматическое дополнение и `Ctrl+J`;
- сохранены штатные HTML5/CSS/JavaScript CodeIntel в mixed CTPP-файлах;
- поддержана whitespace-control форма `<-TMPL_var ...->`;
- добавлен патч Komodo 9 для повторного вычисления trigger при уже открытом HTML5 autocomplete.

## До 2.0

Ранние версии проекта обеспечивали регистрацию языка, LexUDL-подсветку, mixed HTML/CSS/JavaScript/Underscore, линтинг, шаблоны файлов и UI-иконки. Детальная история этих релизов сохраняется в Git.
