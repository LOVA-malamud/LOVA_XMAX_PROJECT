import streamlit as st

def apply_custom_css():
    st.markdown("""
    <style>
        /* Modern Financial Dark (OLED Style) */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Orbitron:wght@700&display=swap');
        
        .stApp { 
            background: radial-gradient(circle at top right, #111111, #000000);
            color: #E2E8F0; 
            font-family: 'Inter', sans-serif; 
        }
        
        /* Glassmorphism Metrics */
        [data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.05);
            padding: 24px !important;
            border-radius: 32px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        [data-testid="stMetric"]:hover { 
            transform: translateY(-4px) scale(1.02);
            border-color: #D4AF37;
            background: rgba(255, 255, 255, 0.05);
        }
        [data-testid="stMetricValue"] { 
            color: #D4AF37 !important; 
            font-weight: 800 !important; 
            font-size: 2.2rem !important;
            letter-spacing: -0.02em;
            text-shadow: 0 0 15px rgba(212, 175, 55, 0.3);
        }
        [data-testid="stMetricLabel"] { 
            color: #94A3B8 !important; 
            font-weight: 600 !important;
            text-transform: uppercase;
            font-size: 0.75rem !important;
            letter-spacing: 0.1em;
        }

        /* Tech Max Header */
        .main-header { 
            font-family: 'Orbitron', sans-serif;
            font-size: 3rem; 
            background: linear-gradient(90deg, #D4AF37, #FFFFFF);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800; 
            letter-spacing: 2px;
            margin-bottom: 0px;
        }
        .sub-header { 
            font-size: 0.85rem; 
            color: #64748B; 
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.3em;
            margin-bottom: 40px;
        }

        /* OLED Sidebar */
        section[data-testid="stSidebar"] { 
            background-color: #050505; 
            border-right: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        /* Glowing Health Bars */
        .health-bar-container {
            background: rgba(255, 255, 255, 0.02);
            border-radius: 24px;
            margin-bottom: 16px;
            padding: 24px;
            border: 1px solid rgba(255, 255, 255, 0.05);
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
        
        /* Premium Buttons */
        .stButton>button {
            background: #D4AF37;
            color: #000;
            border: none;
            border-radius: 20px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
            padding: 14px 24px;
            width: 100%;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(212, 175, 55, 0.2);
        }
        .stButton>button:hover {
            transform: scale(1.02);
            box-shadow: 0 0 25px rgba(212, 175, 55, 0.4);
            background-color: #E5C158;
        }

        /* Segmented Control Tabs */
        .stTabs [data-baseweb="tab-list"] { 
            gap: 12px; 
            padding: 6px;
            background-color: rgba(255, 255, 255, 0.03);
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }
        .stTabs [data-baseweb="tab"] {
            background-color: transparent !important;
            border-radius: 12px !important;
            color: #64748B !important;
            border: none !important;
            font-weight: 600;
            padding: 10px 20px;
            transition: all 0.2s ease;
        }
        .stTabs [aria-selected="true"] { 
            background-color: #D4AF37 !important;
            color: #000 !important;
            box-shadow: 0 4px 12px rgba(212, 175, 55, 0.3);
        }

        /* Creative Accents */
        hr { border-color: rgba(255, 255, 255, 0.05); }
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
