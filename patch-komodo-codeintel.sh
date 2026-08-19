#!/bin/sh
set -eu

# Идемпотентный менеджер патча Komodo 9 CodeIntel.
#
# Патч удаляет ранний выход из ko.codeintel.trigger(), который запрещает
# пересчитать trigger, пока уже открыт autocomplete popup. Для смешанных
# UDL-языков это мешает переключению HTML5 -> CTPP после <TMPL_.
#
# Использование:
#   sh ./patch-komodo-codeintel.sh status
#   sh ./patch-komodo-codeintel.sh install
#   sh ./patch-komodo-codeintel.sh uninstall
#
# Переменные окружения:
#   KOMODO_HOME                   корень Komodo
#   KOMODO_JAR                    путь к komodo.jar
#   KOMODO_PROFILE                профиль Komodo
#   KOMODO_CTPP_PATCH_STATE_DIR   каталог состояния/backup

PROG=${0##*/}
ACTION=${1:-status}

KOMODO_HOME=${KOMODO_HOME:-"$HOME/Komodo-IDE-9"}
JAR=${KOMODO_JAR:-"$KOMODO_HOME/lib/mozilla/chrome/komodo.jar"}
ENTRY='content/codeintel/codeintel.js'
KOMODO_PROFILE=${KOMODO_PROFILE:-"$HOME/.komodoide/9.3"}
STARTUP_CACHE="$KOMODO_PROFILE/XRE/startupCache"
STATE_DIR=${KOMODO_CTPP_PATCH_STATE_DIR:-"$KOMODO_HOME/lib/mozilla/chrome/.ctpp-codeintel-patch"}
ORIGINAL_JS="$STATE_DIR/codeintel.js.orig"
META_FILE="$STATE_DIR/meta"

ORIGINAL_SENTINEL="No need to trigger if it's already open (bug 100035)"
PATCH_MARKER='CTPP PATCH: allow CodeIntel retrigger while autocomplete is active.'
ANCHOR='var ciBuf = this._codeintelSvc.buf_from_koIDocument(view.koDoc);'
SECONDARY_GUARD='trg.is_same(view._ciLastTrg)'

TMP_ROOT=''

say() {
    printf '%s\n' "$*"
}

warn() {
    printf '%s: %s\n' "$PROG" "$*" >&2
}

die() {
    warn "$*"
    exit 1
}

usage() {
    cat <<EOF
Использование: $PROG {status|install|uninstall|help}

  status     показать состояние патча
  install    установить патч; повторный запуск безопасен
  uninstall  удалить патч; повторный запуск безопасен
  help       показать эту справку

Текущие пути:
  KOMODO_HOME=$KOMODO_HOME
  KOMODO_JAR=$JAR
  KOMODO_PROFILE=$KOMODO_PROFILE
EOF
}

cleanup() {
    if [ -n "$TMP_ROOT" ] && [ -d "$TMP_ROOT" ]; then
        rm -rf "$TMP_ROOT"
    fi
}
trap cleanup EXIT HUP INT TERM

need_cmd() {
    command -v "$1" >/dev/null 2>&1 || die "не найдена обязательная команда: $1"
}

check_tools() {
    need_cmd unzip
    need_cmd zip
    need_cmd perl
    need_cmd cmp
    need_cmd mktemp
    need_cmd grep
}

check_jar() {
    [ -f "$JAR" ] || die "не найден komodo.jar: $JAR"
    unzip -t "$JAR" >/dev/null 2>&1 \
        || die "архив повреждён или не является ZIP/JAR: $JAR"
    unzip -Z1 "$JAR" 2>/dev/null | grep -Fx "$ENTRY" >/dev/null 2>&1 \
        || die "в $JAR отсутствует $ENTRY"
}

komodo_running() {
    if command -v pgrep >/dev/null 2>&1; then
        pgrep -x komodo >/dev/null 2>&1 && return 0
    fi
    if command -v pidof >/dev/null 2>&1; then
        pidof komodo >/dev/null 2>&1 && return 0
    fi
    return 1
}

require_stopped() {
    if komodo_running; then
        die "Komodo запущен. Полностью закрой IDE перед изменением komodo.jar"
    fi
}

make_tmp() {
    [ -n "$TMP_ROOT" ] && return 0
    TMP_ROOT=$(mktemp -d "${JAR%/*}/.ctpp-codeintel.XXXXXX") \
        || die "не удалось создать временный каталог рядом с $JAR"
}

extract_entry() {
    out=$1
    unzip -p "$JAR" "$ENTRY" >"$out" \
        || die "не удалось извлечь $ENTRY из $JAR"
    [ -s "$out" ] || die "извлечённый $ENTRY пуст"
}

state_of_file() {
    file=$1

    if grep -F "$PATCH_MARKER" "$file" >/dev/null 2>&1; then
        printf '%s\n' installed
        return
    fi

    if grep -F "$ORIGINAL_SENTINEL" "$file" >/dev/null 2>&1; then
        printf '%s\n' not-installed
        return
    fi

    # Совместимость с ручным вариантом патча: guard уже удалён, но marker ещё
    # не существовал. Такой файл считаем установленным, но автоматически
    # удалить его без известного backup не пытаемся.
    if grep -F "$ANCHOR" "$file" >/dev/null 2>&1 \
       && grep -F "$SECONDARY_GUARD" "$file" >/dev/null 2>&1; then
        printf '%s\n' installed-unmarked
        return
    fi

    printf '%s\n' unknown
}

validate_original() {
    file=$1
    grep -F "$ORIGINAL_SENTINEL" "$file" >/dev/null 2>&1 \
        || die "не найден ожидаемый исходный guard: $ORIGINAL_SENTINEL"
    grep -F "$ANCHOR" "$file" >/dev/null 2>&1 \
        || die "не найден контрольный фрагмент CodeIntel: $ANCHOR"
    grep -F "$SECONDARY_GUARD" "$file" >/dev/null 2>&1 \
        || die "не найден штатный secondary guard: $SECONDARY_GUARD"
}

validate_patched() {
    file=$1
    if grep -F "$ORIGINAL_SENTINEL" "$file" >/dev/null 2>&1; then
        die "патч не применился: исходный guard всё ещё присутствует"
    fi
    grep -F "$ANCHOR" "$file" >/dev/null 2>&1 \
        || die "после патча исчез контрольный фрагмент CodeIntel"
    grep -F "$SECONDARY_GUARD" "$file" >/dev/null 2>&1 \
        || die "после патча исчез штатный secondary guard"
}

patch_file() {
    file=$1

    perl -0pi -e '
        $n = s{
            (^([ \t]*)if[ \t]*\([ \t]*view\.scintilla\.autocomplete\.active[ \t]*\)[ \t]*\{\r?\n)
            ([ \t]*//[ \t]*No[ \t]+need[ \t]+to[ \t]+trigger[ \t]+if[ \t]+it\x27s[ \t]+already[ \t]+open[ \t]+\(bug[ \t]+100035\)\r?\n)
            ([ \t]*return;\r?\n)
            ([ \t]*\}\r?\n)
        }{$2// CTPP PATCH: allow CodeIntel retrigger while autocomplete is active.\n}mx;
        END { exit 23 unless $n == 1; }
    ' "$file" || die "не удалось однозначно заменить ожидаемый guard"
}

unpatch_file() {
    file=$1

    perl -0pi -e '
        $n = s{
            ^([ \t]*)//[ \t]*CTPP[ \t]+PATCH:[ \t]+allow[ \t]+CodeIntel[ \t]+retrigger[ \t]+while[ \t]+autocomplete[ \t]+is[ \t]+active\.\r?\n
        }{
            $1 . "if (view.scintilla.autocomplete.active) {\n" .
            $1 . "    // No need to trigger if it\x27s already open (bug 100035)\n" .
            $1 . "    return;\n" .
            $1 . "}\n"
        }emx;
        END { exit 23 unless $n == 1; }
    ' "$file" || die "не удалось однозначно восстановить guard"
}

replace_entry_atomically() {
    file=$1

    make_tmp

    newjar="$TMP_ROOT/komodo.jar.new"
    work="$TMP_ROOT/work"
    mkdir -p "$work/${ENTRY%/*}"

    cp -p "$JAR" "$newjar" \
        || die "не удалось создать временную копию $JAR"
    cp "$file" "$work/$ENTRY" \
        || die "не удалось подготовить новую запись $ENTRY"

    # Не используем `zip -u`: при install -> uninstall в пределах одной секунды
    # timestamp новой записи может оказаться не новее записи в JAR, и Info-ZIP
    # возвращает "Nothing to do". Удаляем ровно одну запись и добавляем её снова.
    zip -q -d "$newjar" "$ENTRY" \
        || die "zip не смог удалить старую запись $ENTRY"
    (
        cd "$work"
        zip -q "$newjar" "$ENTRY"
    ) || die "zip не смог добавить новую запись $ENTRY"

    unzip -t "$newjar" >/dev/null 2>&1 \
        || die "проверка нового komodo.jar завершилась ошибкой"

    unzip -p "$newjar" "$ENTRY" | cmp - "$file" >/dev/null 2>&1 \
        || die "верификация записи $ENTRY в новом JAR не прошла"

    mv -f "$newjar" "$JAR" \
        || die "не удалось атомарно заменить $JAR"
}

save_original_once() {
    file=$1

    mkdir -p "$STATE_DIR"

    if [ -f "$ORIGINAL_JS" ]; then
        validate_original "$ORIGINAL_JS"
        return
    fi

    cp "$file" "$ORIGINAL_JS" \
        || die "не удалось сохранить резервную копию $ORIGINAL_JS"

    {
        printf 'jar=%s\n' "$JAR"
        printf 'entry=%s\n' "$ENTRY"
        printf 'created=%s\n' "$(date '+%Y-%m-%dT%H:%M:%S%z' 2>/dev/null || date)"
    } >"$META_FILE"
}

clear_startup_cache() {
    if [ -d "$STARTUP_CACHE" ]; then
        rm -rf "$STARTUP_CACHE"
        say "startup cache: удалён $STARTUP_CACHE"
    fi
}

do_status() {
    check_tools
    check_jar
    make_tmp

    current="$TMP_ROOT/codeintel.js.current"
    extract_entry "$current"
    state=$(state_of_file "$current")

    case "$state" in
        installed)
            say 'patch: installed'
            ;;
        installed-unmarked)
            say 'patch: installed (без marker; вероятно применён вручную)'
            ;;
        not-installed)
            say 'patch: not installed'
            ;;
        *)
            say 'patch: unknown/incompatible'
            ;;
    esac

    say "jar:   $JAR"
    say "entry: $ENTRY"
    if [ -f "$ORIGINAL_JS" ]; then
        say "backup: $ORIGINAL_JS"
    else
        say 'backup: none'
    fi

    [ "$state" != unknown ]
}

do_install() {
    check_tools
    check_jar
    require_stopped
    make_tmp

    current="$TMP_ROOT/codeintel.js.current"
    patched="$TMP_ROOT/codeintel.js.patched"
    extract_entry "$current"
    state=$(state_of_file "$current")

    case "$state" in
        installed)
            say 'patch: already installed'
            clear_startup_cache
            return 0
            ;;
        installed-unmarked)
            say 'patch: already installed (без marker; изменений не требуется)'
            clear_startup_cache
            return 0
            ;;
        not-installed)
            ;;
        *)
            die "неизвестная версия codeintel.js; автоматический патч отменён"
            ;;
    esac

    validate_original "$current"
    save_original_once "$current"
    cp "$current" "$patched"
    patch_file "$patched"
    validate_patched "$patched"

    replace_entry_atomically "$patched"

    verify="$TMP_ROOT/codeintel.js.verify"
    extract_entry "$verify"
    [ "$(state_of_file "$verify")" = installed ] \
        || die "финальная проверка установленного патча не прошла"

    clear_startup_cache
    say 'patch: installed successfully'
}

do_uninstall() {
    check_tools
    check_jar
    require_stopped
    make_tmp

    current="$TMP_ROOT/codeintel.js.current"
    restored="$TMP_ROOT/codeintel.js.restored"
    extract_entry "$current"
    state=$(state_of_file "$current")

    case "$state" in
        not-installed)
            say 'patch: already not installed'
            clear_startup_cache
            return 0
            ;;
        installed)
            ;;
        installed-unmarked)
            die "патч присутствует без marker-комментария; безопасный uninstall невозможен автоматически"
            ;;
        *)
            die "неизвестная версия codeintel.js; автоматический uninstall отменён"
            ;;
    esac

    [ -f "$ORIGINAL_JS" ] \
        || die "не найден backup $ORIGINAL_JS; безопасный uninstall отменён"
    validate_original "$ORIGINAL_JS"

    cp "$current" "$restored"
    unpatch_file "$restored"
    validate_original "$restored"

    replace_entry_atomically "$restored"

    verify="$TMP_ROOT/codeintel.js.verify"
    extract_entry "$verify"
    [ "$(state_of_file "$verify")" = not-installed ] \
        || die "финальная проверка удаления патча не прошла"

    clear_startup_cache
    say 'patch: uninstalled successfully'
}

case "$ACTION" in
    status)
        do_status
        ;;
    install)
        do_install
        ;;
    uninstall|remove)
        do_uninstall
        ;;
    help|-h|--help)
        usage
        ;;
    *)
        usage >&2
        exit 2
        ;;
esac
