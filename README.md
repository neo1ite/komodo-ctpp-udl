# Komodo CTPP UDL

[Русский](docs/i18n/README.ru.md) | **English**

CTPP2 / CT++ language support for Komodo IDE and Komodo Edit.

The extension registers `CTPP` for `*.ctpp` files and supports mixed CTPP / HTML5 / CSS / JavaScript templates, Underscore templates, linting and Code Intelligence.

Canonical CTPP implementation for this project: **`waaeer/ctpp`, CT++ 2.8**.

## Status

- **Stable release:** 2.1 — CTPP expressions, built-ins, operators and calltips.
- **Development:** 2.2 — real CILE/CIX scanner for blocks, block arguments, calls and includes.
- Primary tested environment: **Komodo IDE 9.3.2 build 88191, Linux x86_64**.
- Komodo 9 uses its embedded **Python 2.7** runtime for CodeIntel; all `pylib/` code must remain Python 2.7 compatible.

See:

- [Code Intelligence roadmap](docs/CODEINTEL.ru.md)
- [CILE architecture and testing](docs/CILE.ru.md)
- [CHANGELOG](CHANGELOG.md)

## Features

### Language support

- dedicated `CTPP` language for `*.ctpp`;
- syntax highlighting for canonical `TMPL_*` tags;
- whitespace-control forms such as `<-TMPL_var ...->`;
- CTPP inside HTML attributes, `<script>` attributes and JavaScript strings;
- Underscore templates in HTML and JavaScript contexts;
- HTML5-based linting with CTPP sanitizing.

### Mixed-language support

A CTPP file keeps native Komodo language services for embedded regions:

- markup → HTML5;
- `<style>` → CSS;
- `<script>` → JavaScript;
- CTPP tags/expressions → CTPP.

### Code Intelligence 2.0

- explicit CTPP `LangInfo` registration;
- `TMPL_*` tag completion;
- closing-container completion;
- automatic completion and `Ctrl+J`;
- HTML5 → CTPP autocomplete handoff at `<TMPL_`.

### Code Intelligence 2.1

- built-in CT++ 2.8 functions;
- textual operators: `and`, `or`, `lt`, `le`, `gt`, `ge`, `eq`, `ne`, `mod`, `div`;
- symbolic operators;
- `TMPL_foreach ... as`;
- `args(...)` for `TMPL_block` / `TMPL_call`;
- native Komodo calltips;
- correct nested `()` / `[]` expression lexing, including `>` inside expressions.

### Code Intelligence 2.2 — in development

- real `cile_ctpp.py` instead of the old empty CIX stub;
- `TMPL_block` definitions as CIX function scopes;
- `args(...)` as CIX arguments;
- hidden/fabricated CIX references for `TMPL_call` and `TMPL_include`;
- mixed CIX preserving JavaScript and CSS blobs;
- line/signature metadata for later navigation.

Go to Definition is intentionally deferred to 2.3.

## Installation

Install the XPI through Komodo's Add-ons manager.

For development builds, fully close Komodo after replacing the extension and clear the startup cache:

```bash
rm -rf ~/.komodoide/9.3/XRE/startupCache
```

CodeIntel runs in a separate backend process, so a full Komodo restart is required after changes under `pylib/`.

## Komodo 9 autocomplete patch

Komodo 9 contains an early return in `ko.codeintel.trigger()` while an autocomplete popup is already open. HTML5 opens its popup after `<`; without a core fix, Komodo refuses to recalculate the trigger when LexUDL later switches to CTPP at `<TMPL_`.

The repository contains an idempotent patch manager:

```bash
./patch-komodo-codeintel.sh status
./patch-komodo-codeintel.sh install
./patch-komodo-codeintel.sh status

# Safe repeated operations:
./patch-komodo-codeintel.sh install
./patch-komodo-codeintel.sh uninstall
./patch-komodo-codeintel.sh uninstall
```

Komodo must be fully closed for `install` / `uninstall`.

The raw core diff is available at:

```text
patches/komodo-9-codeintel-autocomplete-retrigger.patch
```

## Building

Komodo 9 ships its own Python runtime and SDK. Use the project build wrapper:

```bash
./build.sh
```

Equivalent command:

```bash
KOMODO_HOME="${KOMODO_HOME:-$HOME/Komodo-IDE-9}"

"$KOMODO_HOME/lib/mozilla/mozpython" \
    "$KOMODO_HOME/lib/sdk/bin/koext" build --unjarred
```

`--unjarred` is required because the extension registers `content/`, `skin/` and related chrome resources as real extension directories.

Development version 2.2 builds:

```text
ctpp_language-2.2-ko.xpi
```

## CILE smoke test

The authoritative runtime for CILE compatibility is Komodo's embedded Python 2.7, not the system Python 3.

Run:

```bash
./tests/cile-smoke.sh
```

or directly:

```bash
KOMODO_HOME="${KOMODO_HOME:-$HOME/Komodo-IDE-9}"

"$KOMODO_HOME/lib/mozilla/mozpython" \
    pylib/cile_ctpp.py tests/cile-basic.ctpp
```

A Python 3 standalone run is useful as an additional check, but does **not** replace the Komodo `mozpython` test.

## Project structure

```text
components/        Komodo language and linter components
pylib/             CodeIntel, LangInfo and CILE
udl/               LexUDL source files
lexers/            generated lexer resources in build output
templates/         CTPP new-file templates
skin/              language UI resources
patches/           reviewed patches for Komodo 9 core
tests/             CILE fixtures and smoke tests
docs/              architecture, roadmap and localized documentation
```

Important files:

- `pylib/codeintel_ctpp.py` — CodeIntel triggers, completions, calltips and CILE driver integration;
- `pylib/cile_ctpp.py` — CTPP → CIX scanner;
- `pylib/langinfo_ctpp.py` — static CTPP LangInfo;
- `udl/ctpplex.udl` — CTPP lexer states;
- `patch-komodo-codeintel.sh` — idempotent Komodo 9 core patch manager.

## Compatibility

Primary target:

- Komodo IDE 9.3.2 build 88191;
- Linux x86_64;
- embedded Komodo Python 2.7.

`install.rdf` permits Komodo IDE / Edit 6–9, but current development and acceptance testing are performed on Komodo IDE 9.3.2.

## Diagnostics

Check the core autocomplete patch:

```bash
./patch-komodo-codeintel.sh status
```

After CodeIntel changes, make sure no stale Komodo process remains and remove:

```text
~/.komodoide/9.3/XRE/startupCache
```

Useful log regressions to watch for:

```text
Unable to retrieve langinfo for 'CTPP'
```

The current Code Browser warnings for generic HTML/CIX items are tracked separately from the CTPP completion/CILE milestones.

## License

MIT License. See [LICENSE](LICENSE).
