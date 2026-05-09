import streamlit as st
from deep_translator import GoogleTranslator
import json
import os
from functools import wraps

# Supported languages
SUPPORTED_LANGUAGES = {
    "English": {"code": "en", "native": "English"},
    "Hindi": {"code": "hi", "native": "हिन्दी"},
    "Bengali": {"code": "bn", "native": "বাংলা"},
    "Tamil": {"code": "ta", "native": "தமிழ்"},
    "Telugu": {"code": "te", "native": "తెలుగు"},
    "Marathi": {"code": "mr", "native": "मराठी"},
    "Gujarati": {"code": "gu", "native": "ગુજરાતી"},
    "Kannada": {"code": "kn", "native": "ಕನ್ನಡ"},
    "Malayalam": {"code": "ml", "native": "മലയാളം"},
    "Punjabi": {"code": "pa", "native": "ਪੰਜਾਬੀ"},
    "Odia": {"code": "or", "native": "ଓଡ଼ିଆ"},
    "Spanish": {"code": "es", "native": "Español"},
    "French": {"code": "fr", "native": "Français"},
    "German": {"code": "de", "native": "Deutsch"},
    "Portuguese": {"code": "pt", "native": "Português"},
    "Chinese": {"code": "zh-CN", "native": "中文"},
    "Japanese": {"code": "ja", "native": "日本語"},
    "Korean": {"code": "ko", "native": "한국어"},
    "Arabic": {"code": "ar", "native": "العربية"},
    "Turkish": {"code": "tr", "native": "Türkçe"}
}

# Google Translate character limit per request
_GT_CHAR_LIMIT = 4500
# Separator used for batch translation (unlikely to appear in normal text)
_BATCH_SEP = " ||||| "


class LanguageManager:
    def __init__(self):
        self.cache_file = "translation_cache.json"
        self.cache = self._load_cache()
        self._new_entries = 0

    def _load_cache(self):
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def _save_cache(self):
        try:
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _cache_key(self, text, lang):
        # Use full-text hash to avoid 50-char collision
        return f"{hash(text)}_{lang}"

    def translate_text(self, text, target_lang="en"):
        """Translate a single string. Google Translate primary, fallback to original."""
        if not text or not text.strip() or target_lang == "en":
            return text

        key = self._cache_key(text, target_lang)
        if key in self.cache:
            return self.cache[key]

        try:
            translator = GoogleTranslator(source="en", target=target_lang)
            translated = translator.translate(text[:4900])  # stay under limit
            if translated:
                self.cache[key] = translated
                self._new_entries += 1
                if self._new_entries % 10 == 0:
                    self._save_cache()
                return translated
        except Exception:
            pass

        # Last resort: return original
        return text

    def batch_translate(self, texts, target_lang="en"):
        """
        Translate a list of strings efficiently using a single Google Translate
        request (joined by separator). Chunks automatically if too long.
        Returns list of translated strings in same order.
        """
        if target_lang == "en":
            return texts

        # Check cache first
        results = [None] * len(texts)
        uncached_indices = []
        uncached_texts = []

        for i, text in enumerate(texts):
            if not text or not text.strip():
                results[i] = text
                continue
            key = self._cache_key(text, target_lang)
            if key in self.cache:
                results[i] = self.cache[key]
            else:
                uncached_indices.append(i)
                uncached_texts.append(text)

        if not uncached_texts:
            return results

        # Chunk into batches that fit within character limit
        chunks = []
        current_chunk = []
        current_len = 0

        for text in uncached_texts:
            seg_len = len(text) + len(_BATCH_SEP)
            if current_len + seg_len > _GT_CHAR_LIMIT and current_chunk:
                chunks.append(current_chunk)
                current_chunk = [text]
                current_len = seg_len
            else:
                current_chunk.append(text)
                current_len += seg_len

        if current_chunk:
            chunks.append(current_chunk)

        # Translate each chunk
        translated_flat = []
        for chunk in chunks:
            joined = _BATCH_SEP.join(chunk)
            try:
                translator = GoogleTranslator(source="en", target=target_lang)
                result = translator.translate(joined)
                parts = result.split(_BATCH_SEP)
                if len(parts) == len(chunk):
                    translated_flat.extend(parts)
                    continue
            except Exception:
                pass
            # Fallback: translate individually
            for text in chunk:
                translated_flat.append(self.translate_text(text, target_lang))

        # Store back into results and cache
        for idx, translated in zip(uncached_indices, translated_flat):
            results[idx] = translated
            key = self._cache_key(texts[idx], target_lang)
            self.cache[key] = translated
            self._new_entries += 1

        if self._new_entries % 10 == 0:
            self._save_cache()

        return results


language_manager = LanguageManager()


def init_language_system():
    """Initialize the language system."""
    if "user_language" not in st.session_state:
        st.session_state.user_language = "English"
        st.session_state.user_language_code = "en"


def get_user_language():
    return st.session_state.get("user_language", "English")


def get_user_language_code():
    lang_name = get_user_language()
    return SUPPORTED_LANGUAGES.get(lang_name, {"code": "en"})["code"]


def set_user_language(language):
    if language in SUPPORTED_LANGUAGES:
        current = st.session_state.get("user_language", "English")
        if current != language:
            clear_ai_responses()
            # Invalidate cached UI text for new language
            st.session_state.pop("_ui_text_cache", None)
            st.session_state.pop("_ui_text_lang", None)
        st.session_state.user_language = language
        st.session_state.user_language_code = SUPPORTED_LANGUAGES[language]["code"]


def translate(text):
    """Translate a single string to the current user language."""
    target_lang = get_user_language_code()
    return language_manager.translate_text(text, target_lang)


def clear_ai_responses():
    """Clear all AI responses and dynamic content when language changes."""
    ai_response_keys = [
        "conversation", "messages",
        "ai_response", "healthcare_results", "recipe_response", "nutrition_response",
        "skill_videos", "business_advice", "market_insights", "government_schemes",
        "weather_data", "farming_insights",
        "pest_analysis_results", "farming_tips",
        "issue_analysis", "authorities_results", "videos_results",
        "crop_prediction_result", "fertilizer_recommendation", "recommendations_warnings"
    ]
    cleared_count = 0
    for key in ai_response_keys:
        if key in st.session_state:
            if key in ("conversation", "messages"):
                st.session_state[key] = []
            else:
                st.session_state[key] = None
            cleared_count += 1

    if cleared_count > 0:
        st.session_state.language_changed = True
        st.session_state.language_change_notified = False


def create_language_selector(sidebar=True):
    container = st.sidebar if sidebar else st

    if sidebar:
        container.markdown("---")
        container.markdown("### 🌍 Language")

    current_lang = get_user_language()

    language_options = []
    for lang_name, lang_info in SUPPORTED_LANGUAGES.items():
        display_name = f"{lang_info['native']} ({lang_name})"
        language_options.append((display_name, lang_name))

    current_index = 0
    for i, (display, name) in enumerate(language_options):
        if name == current_lang:
            current_index = i
            break

    selected_display = container.selectbox(
        "Select Language:",
        options=[display for display, _ in language_options],
        index=current_index,
        key="main_language_selector"
    )

    selected_language = None
    for display, name in language_options:
        if display == selected_display:
            selected_language = name
            break

    if selected_language and selected_language != current_lang:
        set_user_language(selected_language)
        ui_text = get_ui_text()
        container.success(f"🌍 {ui_text['language_changed_to']} {selected_language}")
        st.rerun()

    return current_lang


def multilingual_page(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        init_language_system()
        show_language_change_notification()
        return func(*args, **kwargs)
    return wrapper


def show_language_change_notification():
    """Show notification when language has been changed."""
    if st.session_state.get("language_changed", False) and not st.session_state.get("language_change_notified", False):
        current_lang = get_user_language()
        ui_text = get_ui_text()
        st.info(f"🌍 {ui_text['language_changed_to']} {current_lang}. {ui_text['previous_responses_cleared']}")
        st.session_state.language_change_notified = True


def get_ui_text():
    """
    Return translated UI strings for the current language.
    Results are cached in session_state per language to avoid re-translating
    on every Streamlit rerun.
    """
    target_lang = get_user_language_code()

    # Serve from session-state cache if language hasn't changed
    if (
        st.session_state.get("_ui_text_lang") == target_lang
        and "_ui_text_cache" in st.session_state
    ):
        return st.session_state["_ui_text_cache"]

    ui_text_en = {
        "welcome_back": "Welcome back!",
        "hello_farmer": "Hello Farmer! Ready to optimize your farming journey?",
        "navigation": "Navigation",
        "choose_tool": "Choose your farming tool",
        "logged_in": "Logged in",
        "logout": "Logout",
        "smart_chatbot": "Smart Chatbot",
        "chatbot_desc": "Get personalized farming advice",
        "crop_recommendations": "Crop Recommendations",
        "crop_desc": "AI-powered crop and fertilizer suggestions",
        "weather_advisory": "Weather Advisory",
        "weather_desc": "Real-time weather updates and alerts",
        "healthcare_assistance": "Healthcare Assistance",
        "healthcare_desc": "Health guidance for farmers",
        "economic_opportunities": "Economic Opportunities",
        "economic_desc": "Business and funding opportunities",
        "pest_detection": "Pest Detection",
        "pest_desc": "AI crop disease identification",
        "report_issues": "Report Issues",
        "issues_desc": "Community issue reporting system",
        "submit": "Submit",
        "cancel": "Cancel",
        "search": "Search",
        "loading": "Loading...",
        "processing": "Processing...",
        "success": "Success",
        "error": "Error",
        "warning": "Warning",
        "info": "Information",
        "name": "Name",
        "email": "Email",
        "phone": "Phone",
        "address": "Address",
        "location": "Location",
        "description": "Description",
        "enter_your_name": "Enter your name",
        "enter_location": "Enter your location",
        "please_wait": "Please wait...",
        "thank_you": "Thank you",
        "help": "Help",
        "contact": "Contact",
        "about": "About",
        "language_changed_to": "Language changed to",
        "previous_responses_cleared": "Previous responses have been cleared for a fresh start!",
        "chat_history_cleared": "Chat history cleared for new language. Start a fresh conversation!",
        "fresh_start_message": "Content cleared for new language - fresh start!"
    }

    if target_lang == "en":
        st.session_state["_ui_text_cache"] = ui_text_en
        st.session_state["_ui_text_lang"] = target_lang
        return ui_text_en

    # Batch translate all values in one (chunked) Google Translate request
    keys = list(ui_text_en.keys())
    values = list(ui_text_en.values())
    translated_values = language_manager.batch_translate(values, target_lang)

    translated = dict(zip(keys, translated_values))

    # Cache in session state
    st.session_state["_ui_text_cache"] = translated
    st.session_state["_ui_text_lang"] = target_lang

    return translated