import google.generativeai as genai
import streamlit as st
import os
import re
import pandas as pd
import sqlite3
from config import DOCS_DIR

def setup_gemini(api_key):
    if api_key:
        genai.configure(api_key=api_key)
        return True
    return False

def get_ai_response(u_msg, mileage, history, chat_history, api_key, db):
    if not api_key:
        return "API Key Missing", None

    try:
        # --- Step 1: Database Search (RAG) ---
        db_context = ""
        conditions = []
        
        clean_msg = re.sub(r'[^a-zA-Z0-9\s\-]', '', u_msg.lower())
        stop_words = ['which', 'what', 'is', 'the', 'i', 'need', 'for', 'a', 'can', 'you', 'show', 'me', 'part', 'number', 'my', 'scooter', 'yamaha', 'xmax', 'please', 'help', 'do', 'does', 'want', 'to', 'replace', 'broken', 'new']
        for w in stop_words:
            clean_msg = re.sub(rf'\b{w}\b', '', clean_msg)
        
        keywords = clean_msg.split()
        if keywords:
            params = []
            for k in keywords:
                if len(k) > 1: 
                    conditions.append(f"(Description LIKE ? OR Category LIKE ?)")
                    params.extend([f"%{k}%", f"%{k}%"])
            
            if conditions:
                df_db = db.search_parts(u_msg, limit=5) # Utilizing search_parts method
                
                if not df_db.empty:
                    db_context = "\nDATABASE RECORDS FOUND:\n"
                    for _, row in df_db.iterrows():
                        db_context += f"- Exact Part: {row['Description']} | P/N: {row['Part_Number']} | Price: {row['Price_Euro']}\n"

        # --- Step 2: Gemini Prompting with History ---
        custom_rules = db.get_custom_mechanic_rules()
        rules_context = "\n".join([f"- {r}" for r in custom_rules])

        if 'gemini_files' not in st.session_state:
            st.session_state.gemini_files = []
            if os.path.exists(DOCS_DIR):
                for f_name in os.listdir(DOCS_DIR):
                    if f_name.endswith(('.pdf', '.txt')):
                        f_path = os.path.join(DOCS_DIR, f_name)
                        uploaded = genai.upload_file(path=f_path)
                        st.session_state.gemini_files.append(uploaded)
        
        model = genai.GenerativeModel('gemini-flash-lite-latest')
        history_summary = "\n".join([f"- {h['km']} KM: {h['task']}" for h in history[-10:]])
        
        # Format previous messages for context
        chat_context = ""
        for msg in chat_history[-6:]:  # Last 3 rounds
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
        
        res = model.generate_content(st.session_state.gemini_files + [prompt])
        
        # --- Step 3: Visual Context ---
        img_info = None
        if keywords:
            search_conditions = [f"(Description LIKE '%{k}%' OR Category LIKE '%{k}%')" for k in keywords if len(k) > 1]
            if search_conditions:
                df_img = db.get_part_images_for_ai(search_conditions)
                if not df_img.empty:
                    img_info = {"url": df_img.iloc[0]['Image_URL'], "category": df_img.iloc[0]['Category']}

        return res.text, img_info

    except Exception as e:
        print(f"AI Error: {e}")
        return f"Mechanic is currently unavailable. Please try again later. (Error: {str(e)})", None
