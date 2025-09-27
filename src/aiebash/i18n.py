import json
import locale
from pathlib import Path
from typing import Any, Dict, Optional


class Translator:
    """
    JSON-based i18n. English text is used as the lookup key.

    Rules:
    - If translation for the key is missing, return the key itself
    - Locales are stored under `locales/<lang>.json` next to this file
    - Default language is 'en'
    - Supports simple .format(**kwargs)
    """

    def __init__(self, base_dir: Optional[Path] = None, default_lang: str = "en") -> None:
        self.base_dir = base_dir or Path(__file__).parent / "locales"
        self.default_lang = default_lang
        self._lang = default_lang
        self._cache: Dict[str, Dict[str, str]] = {}

    @property
    def lang(self) -> str:
        return self._lang

    def set_language(self, lang: Optional[str]) -> None:
        if not lang:
            self._lang = self.default_lang
            return
        # lazily load
        if lang not in self._cache:
            self._cache[lang] = self._load_locale(lang)
        self._lang = lang

    def t(self, key: str, **kwargs: Any) -> str:
        # For English, return key itself (English-as-key approach)
        if self._lang == "en":
            text = key
        else:
            translations = self._cache.get(self._lang)
            if translations is None:
                translations = self._load_locale(self._lang)
                self._cache[self._lang] = translations
            text = translations.get(key, key)
        try:
            return text.format(**kwargs)
        except Exception:
            return text

    def _load_locale(self, lang: str) -> Dict[str, str]:
        path = Path(self.base_dir) / f"{lang}.json"
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Ensure mapping of str->str
                return {str(k): str(v) for k, v in data.items()}
        except FileNotFoundError:
            return {}
        except Exception:
            return {}


translator = Translator()


def t(key: str, **kwargs: Any) -> str:
    return translator.t(key, **kwargs)


def detect_system_language(supported: Optional[list[str]] = None) -> str:
    """Detect system language code like 'en', 'ru'. Defaults to 'en'.

    If `supported` provided, return first supported match or the first element of supported.
    """
    code = "en"
    try:
        loc = locale.getdefaultlocale()
        if loc and loc[0]:
            code = loc[0].split("_")[0].lower()
    except Exception:
        pass
    if supported:
        return code if code in supported else supported[0]
    return code


def init_system_info_translations() -> None:
    """Инициализирует переводы для модуля sys_info в существующую систему."""
    # Автоматически определяем язык системы
    detected_lang = detect_system_language(['en', 'ru', 'de', 'fr', 'es'])
    
    # Устанавливаем язык если он поддерживается
    if detected_lang != 'en':
        translator.set_language(detected_lang)


# Инициализируем переводы при импорте модуля
init_system_info_translations()
