# CTPP language support for Komodo

**English** | [Русский](docs/i18n/README.ru.md)

This extension adds **CTPP2 / CT++** template support to Komodo IDE and Komodo Edit.

It registers the `CTPP` language for `*.ctpp` files, provides syntax highlighting for mixed CTPP/HTML5/CSS/JavaScript templates, and includes UDL support used by the project for Underscore templates.

## Features

- dedicated `CTPP` language in Komodo;
- syntax highlighting for `*.ctpp` files;
- HTML5, CSS and JavaScript sublanguages inside templates;
- CTPP file templates;
- linter and Code Intelligence/CILE integration components;
- dedicated CTPP icon for files and language UI;
- compatibility with Komodo IDE and Komodo Edit 6–9.

Full modern Code Intelligence for CTPP is not implemented yet.

## Installation

Install the XPI package through Komodo's Add-ons Manager.

After updating the extension, fully close Komodo and clear its startup cache before starting it again:

```bash
rm -rf ~/.komodoide/9.3/XRE/startupCache
```

For Komodo Edit, use the corresponding profile directory if it differs on your system.

## Building

Komodo 9 ships with its own Python 2.7 runtime, `mozpython`. On modern Linux systems the generic `python` command may be absent, so the reliable build command is:

```bash
KOMODO_HOME="${KOMODO_HOME:-$HOME/Komodo-IDE-9}"

"$KOMODO_HOME/lib/mozilla/mozpython" \
    "$KOMODO_HOME/lib/sdk/bin/koext" build
```

A successful build produces an XPI similar to:

```text
ctpp_language-1.3-ko.xpi
```

## Language icon

Version 1.3 loads `skin/languages.css` into Komodo's main chrome through a small valid XUL overlay. The stylesheet is also registered through `agent-style-sheets` as a fallback.

```text
overlay chrome://komodo/content/komodo.xul chrome://ctpp/content/overlay.xul
category agent-style-sheets ctpp-language-icons chrome://ctpp/skin/languages.css
```

The overlay contains only the stylesheet declaration and an empty XUL `overlay` element. This is intentionally different from an earlier broken revision where `overlay.xul` was empty and Komodo reported:

```text
no element found in chrome://ctpp/content/overlay.xul
Failed to load overlay from chrome://ctpp/content/overlay.xul
```

The SVG itself is stored in `skin/ctpp.svg`.

## Project layout

- `udl/` — UDL definitions and language-family transitions;
- `components/` — language registration and linter components;
- `pylib/` — Code Intelligence/CILE integration;
- `templates/` — new-file templates;
- `skin/` — UI resources, including `languages.css` and `ctpp.svg`;
- `content/` — chrome resources, including the language-icon overlay.

## Compatibility

Primary tested configuration:

- Komodo IDE 9.3.2;
- Linux x86_64.

`install.rdf` allows Komodo IDE and Komodo Edit versions 6 through 9.

## Troubleshooting

If a newly installed version is not reflected in the UI, close Komodo completely and remove:

```text
~/.komodoide/9.3/XRE/startupCache
```

Then start Komodo again.

If Code Intelligence reports an exception while scanning an unrelated JavaScript file, that is separate from CTPP language registration and should be diagnosed from the Komodo log independently.

## License

MIT License. See [LICENSE](LICENSE).
