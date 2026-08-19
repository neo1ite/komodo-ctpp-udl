# CTPP language support for Komodo

**English** | [Русский](docs/i18n/README.ru.md)

This extension adds **CTPP2 / CT++** template support to Komodo IDE and Komodo Edit.

It registers the `CTPP` language for `*.ctpp` files, provides syntax highlighting for mixed CTPP/HTML5/CSS/JavaScript templates, supports Underscore templates, linting, and Code Intelligence integration.

## Features

- dedicated `CTPP` language in Komodo;
- syntax highlighting for `*.ctpp` files;
- HTML5, CSS and JavaScript sublanguages inside templates;
- CTPP highlighting inside HTML attributes, `<script>` attributes and JavaScript strings;
- Underscore template highlighting in HTML and JavaScript contexts;
- HTML5-based linting with CTPP sanitizing;
- **Code Intelligence 2.0:** CTPP language registration in CodeIntel and autocomplete for `TMPL_*` tags;
- native HTML5, CSS and JavaScript CodeIntel delegation inside mixed CTPP documents;
- CTPP file templates;
- dedicated CTPP icon for files and language UI;
- compatibility with Komodo IDE and Komodo Edit versions 6–9.

Further CodeIntel stages (expressions, CILE, Go to Definition, variables, Code Browser/project index) are tracked in [the CodeIntel roadmap](docs/CODEINTEL.ru.md).

## Installation

Install the XPI package through Komodo's Add-ons Manager.

After updating a development build, fully close Komodo and clear its startup cache before starting it again:

```bash
rm -rf ~/.komodoide/9.3/XRE/startupCache
```

For CodeIntel changes it is also useful to restart Komodo completely so that the CodeIntel backend process is recreated.

## Building

Komodo 9 ships with its own Python 2.7 runtime, `mozpython`. On modern Linux systems the generic `python` command may be absent, so build through Komodo's runtime.

**Important:** use `--unjarred`. Komodo SDK otherwise packs `content/`, `skin/` and `locale/` into `ctpp_language.jar`, while this extension's chrome manifest addresses `chrome://ctpp/skin/languages.css` and `ctpp.svg` as ordinary chrome directories. The language-menu icon therefore requires the unjarred build.

```bash
KOMODO_HOME="${KOMODO_HOME:-$HOME/Komodo-IDE-9}"

"$KOMODO_HOME/lib/mozilla/mozpython" \
    "$KOMODO_HOME/lib/sdk/bin/koext" build --unjarred
```

A successful version 2.0 build creates:

```text
ctpp_language-2.0-ko.xpi
```

The build output must contain top-level `skin/` and `content/` directories and must **not** contain `ctpp_language.jar`.

## Code Intelligence 2.0

Version 2.0 introduces the first functional CTPP CodeIntel layer:

- explicit `LangInfo` registration for `CTPP`, removing the `Unable to retrieve langinfo for 'CTPP'` warning;
- `TPL_*`-based CodeIntel instead of the old generated `SSL_*` stub;
- automatic `TMPL_*` tag completion after `<TMPL_` and after two characters of a tag name;
- explicit completion (`Ctrl+J`) for a partially typed `TMPL_*` tag;
- container-tag completion for closing forms such as `</TMPL_...>`;
- HTML5/XML completion in markup areas;
- JavaScript and CSS CodeIntel/CILE delegation in their respective UDL families.

Expression completion is intentionally deferred to version 2.1.

## Language icon

CTPP file/tab icons are resolved through Komodo's file-icon machinery. The language selector is a different UI path: Komodo creates menu items with class `languageicon` and the attribute `language="CTPP"`.

The extension injects the CTPP language CSS directly into the main Komodo chrome:

```text
style chrome://komodo/content/komodo.xul chrome://ctpp/skin/languages.css
```

The stylesheet overrides the language-menu image for `language="CTPP"`; the SVG itself is stored in `skin/ctpp.svg`.

The XPI must be built with `koext build --unjarred`, otherwise Komodo SDK places the skin inside a JAR and the chrome URL above does not resolve to the packaged stylesheet as intended.

## Project layout

- `udl/` — UDL definitions and language-family transitions;
- `components/` — language registration and linter components;
- `pylib/` — Code Intelligence, LangInfo and future CILE integration;
- `templates/` — new-file templates;
- `skin/` — UI resources, including `languages.css` and `ctpp.svg`;
- `content/` — other chrome resources when needed.

## Compatibility

Primary tested configuration:

- Komodo IDE 9.3.2 build 88191;
- Linux x86_64.

`install.rdf` allows Komodo IDE and Komodo Edit versions 6 through 9.

## Troubleshooting

If a newly installed development build is not reflected in the UI, close Komodo completely and remove:

```text
~/.komodoide/9.3/XRE/startupCache
```

Then start Komodo again.

If the old CodeIntel state remains after installing 2.0, fully terminate all Komodo processes before restarting the IDE. CodeIntel runs in a separate backend process and must reload extension `pylib/` modules.

## License

MIT License. See [LICENSE](LICENSE).
