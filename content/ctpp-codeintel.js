/* CTPP-specific bridge between HTML5 and CTPP completion.
 *
 * Komodo 9's ko.codeintel.trigger() returns immediately while an autocomplete
 * popup is already open. HTML5 opens tag completion after '<', therefore the
 * HTML popup can survive after LexUDL has switched to the CTPP TPL family.
 *
 * Do not depend on editor_text_modified here: that event is dispatched only
 * for views with _dispatch_events enabled. Instead wrap ko.codeintel.trigger()
 * itself. This is deliberately scoped to CTPP documents and only intervenes
 * for an unfinished CTPP tag at the caret.
 */
(function () {
    var installed = false;
    var attempts = 0;
    var maxAttempts = 200; // ~20 seconds; CodeIntel can initialize late on Komodo 9.

    function isCTPPView(view) {
        try {
            return view && view.koDoc && view.koDoc.language === "CTPP";
        } catch (ex) {
            return false;
        }
    }

    function hasCTPPFragmentAtCaret(view) {
        try {
            var scimoz = view.scimoz;
            var pos = scimoz.currentPos;
            var start = Math.max(0, pos - 64);
            var text = scimoz.getTextRange(start, pos);
            return /(?:<\/?TMPL_|<-TMPL_)[A-Za-z0-9_]*$/i.test(text);
        } catch (ex) {
            return false;
        }
    }

    function currentCompletionIsCTPP(view) {
        try {
            return view._ciLastTrg && view._ciLastTrg.lang === "CTPP";
        } catch (ex) {
            return false;
        }
    }

    function installBridge() {
        if (installed) {
            return;
        }

        attempts += 1;
        if (typeof ko === "undefined" ||
            !ko.codeintel ||
            typeof ko.codeintel.trigger !== "function") {
            if (attempts < maxAttempts) {
                window.setTimeout(installBridge, 100);
            }
            return;
        }

        var log = ko.logging.getLogger("ctpp.codeintel");
        var originalTrigger = ko.codeintel.trigger;

        // Avoid double wrapping if an overlay is reloaded in a development run.
        if (originalTrigger.__ctppCodeIntelBridge__) {
            installed = true;
            return;
        }

        function ctppAwareTrigger(view, triggerPrefCheck) {
            try {
                if (isCTPPView(view) && hasCTPPFragmentAtCaret(view)) {
                    var autocomplete = view.scintilla && view.scintilla.autocomplete;

                    if (autocomplete && autocomplete.active &&
                        !currentCompletionIsCTPP(view)) {
                        // The active popup belongs to HTML/XML completion.
                        // Cancel it before calling the original trigger; otherwise
                        // Komodo 9 returns immediately and never asks TPL CodeIntel.
                        view.scimoz.autoCCancel();
                        view._ciLastTrg = null;

                        // Let LexUDL finish styling the newly inserted character,
                        // then evaluate the same CodeIntel trigger again. Calling
                        // originalTrigger directly avoids recursive wrapping.
                        window.setTimeout(function () {
                            try {
                                if (isCTPPView(view) && hasCTPPFragmentAtCaret(view)) {
                                    originalTrigger.call(ko.codeintel, view,
                                                         triggerPrefCheck);
                                }
                            } catch (ex) {
                                log.exception(ex);
                            }
                        }, 0);
                        return;
                    }
                }
            } catch (ex) {
                log.exception(ex);
            }

            return originalTrigger.call(ko.codeintel, view, triggerPrefCheck);
        }

        ctppAwareTrigger.__ctppCodeIntelBridge__ = true;
        ctppAwareTrigger.__ctppOriginalTrigger__ = originalTrigger;
        ko.codeintel.trigger = ctppAwareTrigger;
        installed = true;
        log.info("CTPP CodeIntel autocomplete bridge installed");
    }

    // The overlay can be evaluated before codeintel.p.js has created
    // ko.codeintel.trigger. Retry until the core function becomes available.
    window.setTimeout(installBridge, 0);
}());
