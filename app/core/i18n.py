from __future__ import annotations

import gettext
from pathlib import Path
from typing import Callable


# Domain and locales directory structure compatible with GNU gettext
_DOMAIN = "messages"
_LOCALES_DIR = Path(__file__).resolve().parent.parent / "locales"

_current_lang = "en"
_translator: gettext.NullTranslations = gettext.NullTranslations()

# Minimal built-in RU translations as a safety net if .mo catalogs are not present yet.
_MANUAL_RU: dict[str, str] = {
    "invalid credentials": "Неверные учетные данные",
    "invalid token": "Неверный токен",
    "invalid refresh token": "Неверный токен обновления",
    "insufficient privileges": "Недостаточно прав",
    "HTTPS required": "Требуется HTTPS",
    "invalid reset token": "Недействительный токен сброса",
    "user not found": "Пользователь не найден",
}


def set_language(lang: str) -> None:
    """Set global language for server-side messages.

    Tries gettext catalogs in app/locales/<lang>/LC_MESSAGES/messages.mo;
    falls back to English or to minimal dictionary if catalogs are missing.
    """
    global _current_lang, _translator
    _current_lang = lang
    try:
        _translator = gettext.translation(
            _DOMAIN, localedir=str(_LOCALES_DIR), languages=[lang], fallback=True
        )
    except Exception:
        _translator = gettext.NullTranslations()


def gettext_(message: str) -> str:
    """Translate message using current translator, with optional RU fallback map."""
    translated = _translator.gettext(message)
    if translated == message and _current_lang.startswith("ru"):
        return _MANUAL_RU.get(message, message)
    return translated


# Conventional alias
_: Callable[[str], str] = gettext_
