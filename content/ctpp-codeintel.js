/* CTPP-specific bridge between HTML5 and CTPP completion.
 *
 * Komodo 9 does not re-evaluate a CodeIntel trigger while an autocomplete
 * popup is already open. HTML5 opens its tag-name completion immediately
 * after '<', so without this bridge the HTML popup can remain active after
 * the lexer has already switched the buffer to the CTPP TPL family.
 */
(function () {
    if (typeof ko === "undefined" || !ko.codeintel) {
        return;
    }

    var log = ko.logging.getLogger("ctpp.codeintel");
    var ctppFragment = /(?:<\/?TMPL_|<-TMPL_)[A-Za-z0-9_]*$/i;

    function isCTPPView(view) {
        try {
            return view && view.koDoc && view.koDoc.language === "CTPP";
        } catch (ex) {
            return false;
        }
    }

    function hasCTPPFragmentAtCaret(view) {
        var scimoz = view.scimoz;
        var pos = scimoz.currentPos;
        var start = Math.max(0, pos - 64);
        return ctppFragment.test(scimoz.getTextRange(start, pos));
    }

    function currentCompletionIsCTPP(view) {
        try {
            return view._ciLastTrg && view._ciLastTrg.lang === "CTPP";
        } catch (ex) {
            return false;
        }
    }

    function retriggerCTPPCompletion(event) {
        try {
            var view = event && event.data && event.data.view;
            if (!isCTPPView(view) || !hasCTPPFragmentAtCaret(view)) {
                return;
            }

            var autocomplete = view.scintilla && view.scintilla.autocomplete;
            if (!autocomplete || !autocomplete.active) {
                return;
            }

            // Once the CTPP popup is active, let Scintilla filter it normally
            // while the user keeps typing the tag name.
            if (currentCompletionIsCTPP(view)) {
                return;
            }

            // The currently visible popup belongs to HTML5. Close it first;
            // ko.codeintel.trigger() otherwise returns immediately while a
            // popup is active. Clear the remembered HTML trigger as well.
            view.scimoz.autoCCancel();
            view._ciLastTrg = null;

            // Run on the next turn so LexUDL has already restyled the newly
            // inserted text as TPL and UDLBuffer delegates to CTPPLangIntel.
            window.setTimeout(function () {
                try {
                    if (!isCTPPView(view) || !hasCTPPFragmentAtCaret(view)) {
                        return;
                    }
                    ko.codeintel.trigger(view, true);
                } catch (ex) {
                    log.exception(ex);
                }
            }, 0);
        } catch (ex) {
            log.exception(ex);
        }
    }

    window.addEventListener("editor_text_modified", retriggerCTPPCompletion, false);

    window.addEventListener("unload", function () {
        window.removeEventListener("editor_text_modified", retriggerCTPPCompletion, false);
    }, false);
}());
