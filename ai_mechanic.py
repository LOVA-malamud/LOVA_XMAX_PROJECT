import google.generativeai as genai
import streamlit as st
import os
import re
import time
import logging
from config import DOCS_DIR, GEMINI_MODEL, AI_STOP_WORDS, GEMINI_MAX_RETRIES

logger = logging.getLogger(__name__)


def setup_gemini(api_key):
    if api_key:
        genai.configure(api_key=api_key)
        return True
    return False


def _call_gemini_with_retry(model, content):
    for attempt in range(GEMINI_MAX_RETRIES):
        try:
            return model.generate_content(content)
        except Exception as e:
            err_str = str(e).lower()
            is_rate_limit = "quota" in err_str or "rate" in err_str or "429" in err_str
            if is_rate_limit and attempt < GEMINI_MAX_RETRIES - 1:
                wait = 2 ** attempt
                logger.warning(f"Gemini rate limit, retrying in {wait}s (attempt {attempt + 1})")
                time.sleep(wait)
                continue
            raise
    raise RuntimeError("Gemini API failed after max retries")


def get_ai_response(u_msg, mileage, history, chat_history, api_key, db):
    if not api_key:
        return "API Key Missing — set GEMINI_API_KEY in your .env file.", None

    try:
        # --- Step 1: Database Search (RAG) ---
        db_context = ""

        clean_msg = re.sub(r'[^a-zA-Z0-9\s]', '', u_msg.lower())
        for w in AI_STOP_WORDS:
            clean_msg = re.sub(rf'\b{re.escape(w)}\b', '', clean_msg)

        keywords = [k for k in clean_msg.split() if len(k) > 1]

        if keywords:
            df_db = db.search_parts(u_msg, limit=5)
            if not df_db.empty:
                db_context = "\nDATABASE RECORDS FOUND:\n"
                for _, row in df_db.iterrows():
                    db_context += f"- Part: {row['Description']} | P/N: {row['Part_Number']} | Price: {row['Price_Euro']} €\n"

        # --- Step 2: Gemini Prompting ---
        custom_rules = db.get_custom_mechanic_rules()
        rules_context = "\n".join([f"- {r}" for r in custom_rules])

        if 'gemini_files' not in st.session_state:
            st.session_state.gemini_files = []
            if os.path.exists(DOCS_DIR):
                for f_name in os.listdir(DOCS_DIR):
                    if f_name.endswith(('.pdf', '.txt')):
                        f_path = os.path.join(DOCS_DIR, f_name)
                        try:
                            uploaded = genai.upload_file(path=f_path)
                            st.session_state.gemini_files.append(uploaded)
                        except Exception as e:
                            logger.warning(f"Failed to upload {f_name}: {e}")

        model = genai.GenerativeModel(GEMINI_MODEL)
        history_summary = "\n".join([f"- {h['km']} KM: {h['task']}" for h in history[-10:]])

        chat_context = ""
        for msg in chat_history[-6:]:
            chat_context += f"{msg['role'].upper()}: {msg['content']}\n"

        prompt = f"""
        You are a Master Yamaha Mechanic for XMAX 400.
        Vehicle Stats: Odometer: {mileage} KM. Recent History: {history_summary}.

        Custom Mechanic Rules & Expert Knowledge:
        {rules_context}

        Context from Parts Database: {db_context}

        Previous Conversation:
        {chat_context}

        Current User Question: {u_msg}

        Instructions:
        1. Be technical and precise.
        2. If part numbers are in the database context, use them!
        3. Reference the vehicle history ONLY if it is relevant to the user's question or if there is an overdue service.
        4. Do NOT list the service logs unless explicitly asked to summarize the history.
        5. Keep answers concise and helpful.
        6. ALWAYS prioritize the "Custom Mechanic Rules & Expert Knowledge" provided above when answering technical questions.
        """

        res = _call_gemini_with_retry(model, st.session_state.gemini_files + [prompt])

        # --- Step 3: Visual Context ---
        img_info = None
        if keywords:
            df_img = db.get_part_images_for_ai(keywords)
            if not df_img.empty:
                img_info = {
                    "url": df_img.iloc[0]['Image_URL'],
                    "category": df_img.iloc[0]['Category'],
                }

        return res.text, img_info

    except Exception as e:
        logger.error(f"AI Error: {e}")
        err_str = str(e).lower()
        if "quota" in err_str or "429" in err_str:
            return "The AI Mechanic is temporarily unavailable due to API rate limits. Please try again in a moment.", None
        if "api_key" in err_str or "invalid" in err_str:
            return "Invalid API key. Please check your GEMINI_API_KEY in the .env file.", None
        return "The AI Mechanic encountered an error. Please try again later.", None
