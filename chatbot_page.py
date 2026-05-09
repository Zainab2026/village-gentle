import streamlit as st
import requests
from deep_translator import GoogleTranslator
import time
import tempfile
import os
from pymongo import MongoClient
import gridfs
from datetime import datetime
import hashlib
from gtts import gTTS
import io
from language_manager import multilingual_page, translate, get_user_language_code

# Import configuration
from config import config
from modern_ui import modern_header, modern_card


# API Keys from config
ASSEMBLYAI_API_KEY = config.ASSEMBLYAI_API_KEY
GROQ_API_KEY = config.GROQ_API_KEY

# MongoDB Connection
MONGODB_URI = config.MONGODB_URI

# API Endpoints
GROQ_API_URL = config.GROQ_API_URL
ASSEMBLYAI_UPLOAD_URL = config.ASSEMBLYAI_UPLOAD_URL
ASSEMBLYAI_TRANSCRIPT_URL = config.ASSEMBLYAI_TRANSCRIPT_URL



# 🔹 Custom CSS - Minimal styling for chatbot
def apply_custom_css():
    st.markdown(
        """
        <style>
        .chat-message {
            color: white !important;
            font-size: 16px !important;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 1rem;
            margin: 0.5rem 0;
            border-left: 4px solid #4CAF50;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


@st.cache_resource
def init_mongodb():
    try:
        client = MongoClient(MONGODB_URI)
        db = client.smart_farming_chatbot
        fs = gridfs.GridFS(db)
        return db, fs
    except Exception as e:
        st.error(f"{translate('Failed to connect to MongoDB')}: {str(e)}")
        return None, None


def get_audio_hash(text, language="en"):
    return hashlib.md5(f"{text}_{language}".encode()).hexdigest()


def save_conversation(db, user_message, ai_response, session_id, language="en"):
    try:
        conversation = {
            "session_id": session_id,
            "user_message": user_message,
            "ai_response": ai_response,
            "language": language,
            "timestamp": datetime.now()
        }
        db.farming_conversations.insert_one(conversation)
    except Exception as e:
        st.error(f"{translate('Failed to save conversation')}: {str(e)}")


def load_conversations(db, session_id):
    try:
        conversations = list(db.farming_conversations.find(
            {"session_id": session_id}
        ).sort("timestamp", 1))
        return [(conv["user_message"], conv["ai_response"]) for conv in conversations]
    except Exception as e:
        st.error(f"{translate('Failed to load conversations')}: {str(e)}")
        return []


def save_audio_to_gridfs(fs, audio_data, text_hash):
    try:
        file_id = fs.put(audio_data, filename=f"audio_{text_hash}.mp3", content_type="audio/mpeg")
        return file_id
    except Exception as e:
        st.error(f"Failed to save audio: {str(e)}")
        return None


def get_audio_from_gridfs(fs, text_hash):
    try:
        file_data = fs.find_one({"filename": f"audio_{text_hash}.mp3"})
        if file_data:
            return file_data.read()
        return None
    except Exception as e:
        st.error(f"Failed to retrieve audio: {str(e)}")
        return None


@st.cache_resource
def load_whisper_model():
    from transformers import pipeline
    # Load the authentic OpenAI Whisper model locally for offline transcription
    return pipeline("automatic-speech-recognition", model="openai/whisper-tiny")

def transcribe_audio_local(audio_path):
    try:
        st.toast(translate("Loading local Whisper AI model for transcription..."))
        transcriber = load_whisper_model()
        result = transcriber(audio_path)
        return result["text"].strip()
    except Exception as e:
        st.error(f"{translate('Local transcription error')}: {str(e)}")
        return "Error in transcription"


def get_gtts_language_code(language_code):
    gtts_mapping = {
        "en": "en", "hi": "hi", "bn": "bn", "ta": "ta", "te": "te",
        "mr": "mr", "gu": "gu", "kn": "kn", "ml": "ml", "pa": "pa",
        "or": "or", "es": "es", "fr": "fr", "de": "de", "it": "it",
        "pt": "pt", "zh": "zh", "ja": "ja", "ko": "ko", "ar": "ar",
        "tr": "tr", "fa": "fa", "sw": "sw", "ha": "ha", "am": "am"
    }
    return gtts_mapping.get(language_code, "en")


def get_llm_response(text, language="en"):
    smart_prompt = f"""You are an intelligent assistant with expertise in farming and agriculture. 

If the question is related to farming, agriculture, crops, livestock, soil, irrigation, pest control, or rural development, provide detailed, practical farming advice.

If the question is about other topics, provide a helpful response but connect to farming or rural life when possible.

User question: {text}

Provide a helpful and informative response."""

    # 1. OPTION A: Authentic Offline LLM via Local Ollama
    # If the user has Ollama running locally (Apple Silicon native), use it for 100% offline AI
    try:
        ollama_url = "http://localhost:11434/api/generate"
        ollama_data = {
            "model": "llama3.1",
            "prompt": smart_prompt,
            "stream": False,
            "options": {"temperature": 0.7, "num_predict": 2048}
        }
        # Short timeout just to check if local server is alive
        res = requests.post(ollama_url, json=ollama_data, timeout=1.5)
        if res.status_code == 200:
            st.toast(translate("⚡ Powered by Local Offline Llama 3.1 (Ollama)"))
            answer = res.json()["response"]
            
            # Translate local answer if needed
            if language != "en":
                from language_manager import language_manager, get_user_language_code
                answer = language_manager.translate_text(answer, get_user_language_code())
            return answer
    except:
        pass  # Ollama is not running locally, seamlessly fallback to Cloud Groq API

    # 2. OPTION B: Cloud API Fallback (Groq)
    st.toast(translate("☁️ Powered by Groq Cloud Llama 3.1"))
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROQ_API_KEY}"
    }

    data = {
        "model": "llama-3.1-8b-instant",  # Using Llama 3.1 8B - confirmed production model
        "messages": [{"role": "user", "content": smart_prompt}],
        "max_tokens": 2048,  # Increased from 400 to 2048 for complete responses
        "temperature": 0.7
    }

    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            response_data = response.json()
            answer = response_data["choices"][0]["message"]["content"]
            
            if language != "en":
                try:
                    from deep_translator import GoogleTranslator
                    answer = GoogleTranslator(source="en", target=language).translate(answer)
                except Exception as trans_error:
                    st.warning(f"{translate('Translation failed')}: {trans_error}")
                    answer = f"[{translate('English')}] {answer}"
            return answer
        else:
            error_msg = f"GroqCloud API Error: {response.status_code}"
            try:
                error_detail = response.json()
                error_msg += f" - {error_detail}"
            except:
                error_msg += f" - {response.text}"
            
            st.error(error_msg)
            return translate("Sorry, I couldn't process your request. Please try again.")
            
    except requests.exceptions.Timeout:
        st.error(translate("Request timed out. Please try again."))
        return translate("Sorry, the request timed out. Please try again.")
    except requests.exceptions.ConnectionError:
        st.error(translate("Connection error. Please check your internet connection."))
        return translate("Sorry, connection failed. Please check your internet connection.")
    except Exception as e:
        st.error(f"{translate('Unexpected error')}: {str(e)}")
        return translate("Sorry, I encountered an unexpected error.")


def text_to_speech(text, fs, language_code="en"):
    text_hash = get_audio_hash(text, language_code)
    cached_audio = get_audio_from_gridfs(fs, text_hash)

    if cached_audio:
        return cached_audio

    try:
        gtts_lang = get_gtts_language_code(language_code)
        tts = gTTS(text=text, lang=gtts_lang, slow=False)
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_data = audio_buffer.getvalue()
        save_audio_to_gridfs(fs, audio_data, text_hash)
        return audio_data
    except:
        return None


@multilingual_page
def chatbot_page():
    apply_custom_css()

    db, fs = init_mongodb()
    if db is None or fs is None:
        st.error(translate("Cannot connect to MongoDB"))
        st.stop()

    if "session_id" not in st.session_state:
        st.session_state.session_id = f"farming_session_{int(time.time())}"
    if "conversation" not in st.session_state:
        st.session_state.conversation = load_conversations(db, st.session_state.session_id)
    if "processing" not in st.session_state:
        st.session_state.processing = False
    
    # Check if language changed and show info message
    if "conversation" in st.session_state and len(st.session_state.conversation) == 0:
        if st.session_state.get("language_changed", False) and not st.session_state.get("chatbot_notified", False):
            st.info(translate("💬 Chat history cleared for new language. Start a fresh conversation!"))
            st.session_state.chatbot_notified = True

    # Restore the header as requested by the user
    modern_header(translate("Smart Farming Assistant"), translate("Your intelligent guide for sustainable agriculture and crop management."))
    st.write(translate("Type or speak your question. The assistant will reply with text and audio."))

    # Use the centralized language system
    lang_code = get_user_language_code()

    st.subheader(translate("💬 Conversation"))
    for user_msg, bot_msg in st.session_state.conversation:
        st.markdown(f"<p class='chat-message'><b>👤 {translate('You')}:</b> {user_msg}</p>", unsafe_allow_html=True)
        st.markdown(f"<p class='chat-message'><b>🤖 {translate('Assistant')}:</b> {bot_msg}</p>", unsafe_allow_html=True)
        text_hash = get_audio_hash(bot_msg, lang_code)
        cached_audio = get_audio_from_gridfs(fs, text_hash)
        if cached_audio:
            st.audio(cached_audio, format="audio/mpeg")
        st.markdown("---")

    text_input = st.text_area(translate("Type your message"), key="main_input")

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        send_clicked = st.button(f"✉ {translate('Send')}", disabled=st.session_state.processing)
    with col2:
        try:
            audio_bytes = st.audio_input(f"🎙 {translate('Voice input')}", key="voice_input")
            process_voice = st.button(f"🎤 {translate('Process Voice')}") if audio_bytes else False
        except:
            process_voice = False
    with col3:
        new_chat = st.button(f"🆕 {translate('New Chat')}")

    if send_clicked and text_input.strip():
        st.session_state.processing = True
        with st.spinner(translate("Processing...")):
            user_message = text_input.strip()
            english_input = GoogleTranslator(source=lang_code, target="en").translate(user_message) if lang_code != "en" else user_message
            ai_response = get_llm_response(english_input, lang_code)
            text_to_speech(ai_response, fs, lang_code)
            save_conversation(db, user_message, ai_response, st.session_state.session_id, lang_code)
            st.session_state.conversation.append((user_message, ai_response))
        st.session_state.processing = False
        st.rerun()

    if process_voice and audio_bytes is not None:
        st.session_state.processing = True
        with st.spinner(translate("Processing voice...")):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                tmp_file.write(audio_bytes.getvalue())
                tmp_file_path = tmp_file.name
                
            # Run inference locally with Whisper instead of uploading to cloud
            transcribed_text = transcribe_audio_local(tmp_file_path)
            os.unlink(tmp_file_path)
            if transcribed_text and transcribed_text != "Error in transcription":
                user_message = GoogleTranslator(source="en", target=lang_code).translate(transcribed_text) if lang_code != "en" else transcribed_text
                english_input = GoogleTranslator(source=lang_code, target="en").translate(user_message) if lang_code != "en" else user_message
                ai_response = get_llm_response(english_input, lang_code)
                text_to_speech(ai_response, fs, lang_code)
                save_conversation(db, user_message, ai_response, st.session_state.session_id, lang_code)
                st.session_state.conversation.append((user_message, ai_response))
        st.session_state.processing = False
        st.rerun()

    if new_chat:
        st.session_state.session_id = f"farming_session_{int(time.time())}"
        st.session_state.conversation = []
        st.rerun()


if __name__ == "__main__":
    chatbot_page()