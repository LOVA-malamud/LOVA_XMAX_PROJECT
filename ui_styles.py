import streamlit as st

def apply_custom_css():
    st.markdown("""
    <style>
        /* Mat Gray & Gold Tech Max Theme */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Orbitron:wght@700&display=swap');
        
        .stApp { 
            background: #121212;
            color: #FFFFFF; 
            font-family: 'Inter', sans-serif; 
        }
        
        /* Glassmorphism Metrics */
        [data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(212, 175, 55, 0.2);
            padding: 24px !important;
            border-radius: 20px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
            transition: all 0.3s ease;
        }
        [data-testid="stMetric"]:hover { 
            transform: translateY(-2px);
            border-color: #D4AF37;
            background: rgba(255, 255, 255, 0.05);
        }
        [data-testid="stMetricValue"] { 
            color: #D4AF37 !important; 
            font-weight: 800 !important; 
            font-size: 2.2rem !important;
        }
        [data-testid="stMetricLabel"] { 
            color: #FFFFFF !important; 
            font-weight: 500 !important;
            opacity: 0.8;
        }

        /* Tech Max Header */
        .main-header { 
            font-family: 'Orbitron', sans-serif;
            font-size: 2.8rem; 
            color: #D4AF37;
            font-weight: 800; 
            letter-spacing: 2px;
            margin-bottom: 5px;
        }
        .sub-header { 
            font-size: 0.8rem; 
            color: #FFFFFF; 
            font-weight: 400;
            opacity: 0.6;
            text-transform: uppercase;
            letter-spacing: 0.2em;
            margin-bottom: 30px;
        }

        /* Sidebar Styling */
        section[data-testid="stSidebar"] { 
            background-color: #0A0A0A; 
            border-right: 1px solid rgba(212, 175, 55, 0.3);
        }
        
        /* Health Bars */
        .health-bar-container {
            background: #363636;
            border-radius: 16px;
            margin-bottom: 16px;
            padding: 20px;
            border: 1px solid rgba(212, 175, 55, 0.1);
        }
        .health-bar-label { 
            font-size: 0.8rem; 
            font-weight: 700; 
            color: #94A3B8;
            margin-bottom: 12px;
            display: flex;
            justify-content: space-between;
        }
        .health-bar-bg { 
            background-color: #1A1A1A; 
            height: 6px; 
            border-radius: 3px; 
            overflow: hidden;
        }
        .health-bar-fill { 
            height: 100%; 
            border-radius: 3px;
            box-shadow: 0 0 10px currentColor;
        }
        
        /* Selectbox & Inputs */
        div[data-baseweb="select"] > div {
            background-color: #363636 !important;
            border-color: rgba(212, 175, 55, 0.3) !important;
        }
        
        /* Premium Buttons */
        .stButton>button {
            background: #D4AF37;
            color: #1E1E1E;
            border: none;
            border-radius: 12px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
            padding: 12px 24px;
            width: 100%;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(212, 175, 55, 0.2);
        }
        .stButton>button:hover {
            transform: scale(1.02);
            box-shadow: 0 0 25px rgba(212, 175, 55, 0.4);
            background-color: #E5C158;
            border-color: #D4AF37;
        }

        /* Creative Accents */
        hr { border-color: rgba(212, 175, 55, 0.1); }
        .stMarkdown code { background-color: rgba(255, 255, 255, 0.05); }
    </style>
    """, unsafe_allow_html=True)

def draw_health_bar(label, current, interval, last_service_km):
    km_since = current - last_service_km
    remaining = interval - km_since
    pct = max(0, min(100, (remaining / interval) * 100))
    color = "#10B981" if pct > 40 else "#F59E0B" if pct > 15 else "#EF4444"
    st.markdown(f"""
    <div class="health-bar-container">
        <div class="health-bar-label">
            <span>{label}</span>
            <span style="color: {color};">{remaining:,} KM LEFT</span>
        </div>
        <div class="health-bar-bg">
            <div class="health-bar-fill" style="width: {pct}%; background-color: {color}; color: {color};"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
