import streamlit as st
import os
import pandas as pd
from datetime import date, datetime, timedelta
from dotenv import load_dotenv

import config
import ui_styles
from database_manager import ScooterDB
import ai_mechanic
import plotly.express as px

class DashboardApp:
    def __init__(self, db: ScooterDB):
        self.db = db
        self.load_environment()
        self.setup_ui()

    def load_environment(self):
        load_dotenv()
        self.api_key = os.getenv("GEMINI_API_KEY")
        ai_mechanic.setup_gemini(self.api_key)
        
        # Ensure folders exist
        for folder in [config.SCHEMATICS_DIR, config.DOCS_DIR]:
            os.makedirs(folder, exist_ok=True)

        # Session State for AI Chat
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []

    def setup_ui(self):
        ui_styles.apply_custom_css()

    def get_last_service_km(self, task_name):
        keywords = config.MAINTENANCE_INTERVALS[task_name]["keywords"]
        return self.db.get_last_service_km(keywords)

    def render_sidebar(self, current_mileage, usage_stats):
        with st.sidebar:
            st.image("https://dd5394a0.rocketcdn.me/wp-content/uploads/2019/11/2020-Yamaha-XMAX-400-Tech-MAX-EU-Tech-Kamo-Studio-001-03.jpg", use_container_width=True)
            st.markdown("<h2 style='text-align: center; color: #D4AF37; font-family: Orbitron; font-size: 1.8rem; text-shadow: 0 0 10px rgba(212,175,55,0.5);'>TECH MAX</h2>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #64748B; font-size: 0.8rem; margin-top: -10px;'>SPECIAL EDITION</p>", unsafe_allow_html=True)
            
            st.write("---")
            st.markdown("#### ⚡ QUICK LOG")
            if st.button("🛢️ LOG OIL CHANGE"):
                self.db.add_service_log(str(date.today()), "Engine Oil Change (Quick Log)", current_mileage, 0.0, "Logged via Quick Action.")
                st.toast("Oil change logged!")
                st.rerun()

            st.write("---")
            st.markdown("#### 🛠️ ODOMETER")
            new_km = st.number_input("Enter KM", value=current_mileage, step=100, label_visibility="collapsed", min_value=0)
            if new_km != current_mileage:
                try:
                    self.db.update_mileage(new_km)
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to update odometer: {e}")
            
            if usage_stats:
                st.write("---")
                st.markdown("#### 📈 ANALYTICS")
                col_a, col_b = st.columns(2)
                col_a.metric("DAILY", f"{usage_stats['avg_km_day']:.0f}")
                col_b.metric("MONTHLY", f"{usage_stats['avg_km_month']:.0f}")

    def render_header(self, current_mileage, history):
        st.markdown(f"<h1 class='main-header'>{config.APP_TITLE}</h1>", unsafe_allow_html=True)
        st.markdown("<p class='sub-header'>400cc Performance | Mat Gray Edition | 2020</p>", unsafe_allow_html=True)
        
        total_spent = sum(float(item.get('cost', 0)) for item in history)
        m1, m2, m3 = st.columns(3)
        m1.metric("DISTANCE", f"{current_mileage:,} KM")
        m2.metric("INVESTED", f"₪ {total_spent:,.0f}")
        m3.metric("SERVICES", f"{len(history)}")

    def run(self):
        current_mileage = self.db.get_mileage()
        history = self.db.get_history()
        usage_stats = self.db.calculate_usage_stats()

        self.render_sidebar(current_mileage, usage_stats)
        self.render_header(current_mileage, history)

        tabs = st.tabs([
            "📊 Dashboard", "🔧 Log Service", "🚨 Repairs", "⛽ Fuel", 
            "📚 Specs", "🛠️ Schematics", "🔍 Parts", "🤖 AI Mechanic", "📋 History"
        ])

        self.render_dashboard_tab(tabs[0], current_mileage, usage_stats)
        self.render_log_service_tab(tabs[1], current_mileage)
        self.render_repairs_tab(tabs[2])
        self.render_fuel_tab(tabs[3], current_mileage)
        self.render_specs_tab(tabs[4])
        self.render_schematics_tab(tabs[5])
        self.render_parts_tab(tabs[6])
        self.render_ai_mechanic_tab(tabs[7], current_mileage, history)
        self.render_history_tab(tabs[8], history)

    def render_dashboard_tab(self, tab, current_mileage, usage_stats):
        with tab:
            st.subheader("🛡️ Maintenance Health")
            for task, info in config.MAINTENANCE_INTERVALS.items():
                last_km = self.get_last_service_km(task)
                ui_styles.draw_health_bar(task, current_mileage, info['interval'], last_km)
                
                if usage_stats and usage_stats['avg_km_day'] > 0:
                    km_since = current_mileage - last_km
                    km_left = info['interval'] - km_since
                    if km_left > 0:
                        days_left = km_left / usage_stats['avg_km_day']
                        due_date = date.today() + timedelta(days=int(days_left))
                        st.caption(f"📅 Estimated due: **{due_date.strftime('%d %b %Y')}** ({int(days_left)} days)")
                    else:
                        st.error(f"⚠️ OVERDUE by {abs(km_left):,} KM!")
            
            st.write("---")
            st.subheader("🔮 Predictive Maintenance")
            if usage_stats and usage_stats['avg_km_day'] > 0:
                predictive_tasks = ["V-Belt", "Air Filters"]
                for task in predictive_tasks:
                    if task in config.MAINTENANCE_INTERVALS:
                        info = config.MAINTENANCE_INTERVALS[task]
                        last_km = self.get_last_service_km(task)
                        km_since = current_mileage - last_km
                        km_left = info['interval'] - km_since
                        
                        progress = min(max(km_since / info['interval'], 0.0), 1.0)
                        days_left = max(km_left / usage_stats['avg_km_day'], 0)
                        due_date = date.today() + timedelta(days=int(days_left))
                        
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.write(f"**{task}**")
                            st.progress(progress)
                        with col2:
                            if km_left > 0:
                                st.write(f"{int(days_left)} days left")
                            else:
                                st.write("OVERDUE")
                        
                        if 0 < days_left <= 14:
                            st.markdown(f"<p style='color: #FF4B4B; font-weight: bold;'>🚨 URGENT: {task} replacement predicted on {due_date.strftime('%d %b %Y')}!</p>", unsafe_allow_html=True)
                        elif days_left <= 0:
                            st.markdown(f"<p style='color: #FF4B4B; font-weight: bold;'>🚨 CRITICAL: {task} is OVERDUE!</p>", unsafe_allow_html=True)
                        else:
                            st.caption(f"Next replacement: {due_date.strftime('%d %b %Y')}")
            else:
                st.info("💡 Start logging your mileage to enable predictive analytics!")

    def render_log_service_tab(self, tab, current_mileage):
        with tab:
            st.subheader("Record New Maintenance")
            with st.form("service_form", clear_on_submit=True):
                s_task = st.text_input("Service Description (e.g. Oil Change)")
                s_km = st.number_input("Mileage", value=current_mileage, min_value=0)
                s_cost = st.number_input("Cost (₪)", min_value=0.0)
                s_date = st.date_input("Date", date.today())
                s_notes = st.text_area("Notes")
                if st.form_submit_button("✅ Save Service"):
                    if not s_task:
                        st.error("Please provide a service description.")
                    else:
                        try:
                            self.db.add_service_log(str(s_date), s_task, s_km, s_cost, s_notes)
                            st.success("Saved!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to save service log: {e}")

    def render_repairs_tab(self, tab):
        with tab:
            st.subheader("🚨 Pending Repairs & To-Do List")
            c1, c2 = st.columns([1, 2])
            with c1:
                st.markdown("#### ➕ Add Task")
                with st.form("todo_form", clear_on_submit=True):
                    t_task = st.text_input("What needs fixing?")
                    t_priority = st.selectbox("Priority", ["Low", "Medium", "High"])
                    if st.form_submit_button("Add to List"):
                        if not t_task:
                            st.error("Task description cannot be empty.")
                        else:
                            try:
                                self.db.add_todo_item(t_task, t_priority)
                                st.toast(f"Added: {t_task}")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Failed to add task: {e}")
            with c2:
                st.markdown("#### 📋 Open Tasks")
                try:
                    todo_df = self.db.get_todo_list()
                    if todo_df.empty:
                        st.success("🎉 Everything is fixed!")
                    else:
                        for idx, row in todo_df.iterrows():
                            color = "🔴" if row['priority'] == "High" else "🟡" if row['priority'] == "Medium" else "🟢"
                            col_task, col_btn = st.columns([4, 1])
                            col_task.markdown(f"**{color} {row['task']}**  \n<small>Added: {row['added_date']}</small>", unsafe_allow_html=True)
                            if col_btn.button("Done", key=f"todo_{row['id']}"):
                                try:
                                    self.db.complete_todo_item(row['id'])
                                    st.success("Task completed!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Failed to complete task: {e}")
                except Exception as e:
                    st.error(f"Failed to load todo list: {e}")

    def render_fuel_tab(self, tab, current_mileage):
        with tab:
            st.subheader("⛽ Fuel Consumption Tracker")
            c1, c2 = st.columns([1, 2])
            with c1:
                with st.form("fuel_form", clear_on_submit=True):
                    f_date = st.date_input("Refuel Date", date.today())
                    f_km = st.number_input("Odometer at Refuel", value=current_mileage, min_value=0)
                    f_liters = st.number_input("Liters Filled", min_value=0.1, step=0.1)
                    f_price = st.number_input("Total Price (₪)", min_value=0.0)
                    if st.form_submit_button("➕ Log Fuel"):
                        try:
                            self.db.add_fuel_log(str(f_date), f_km, f_liters, f_price)
                            st.success("Fuel logged!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to log fuel: {e}")
            with c2:
                fuel_df = self.db.get_fuel_history()
                if not fuel_df.empty and len(fuel_df) > 1:
                    st.write("### 📈 Fuel Efficiency (KM/L)")
                    
                    # Calculate KM/L
                    fuel_df['km_per_l'] = fuel_df['km_diff'] / fuel_df['liters']
                    
                    fig = px.line(fuel_df.dropna(subset=['km_per_l']), 
                                  x='date', y='km_per_l', 
                                  title='KM/L Over Time',
                                  labels={'km_per_l': 'KM/L', 'date': 'Date'},
                                  markers=True)
                    fig.update_layout(hovermode="x unified")
                    st.plotly_chart(fig, use_container_width=True)
                    
                    avg_km_l = fuel_df['km_per_l'].mean()
                    st.metric("Avg Efficiency", f"{avg_km_l:.2f} KM/L")
                else:
                    st.info("Log 2+ refuels for stats.")

    def render_specs_tab(self, tab):
        with tab:
            st.subheader("📚 Detailed Technical Specifications")
            spec_result = self.db.get_tech_specs()
            if spec_result["status"] == "success":
                specs_data = spec_result["data"]
                cats = list(specs_data.keys())
                for i in range(0, len(cats), 2):
                    col_left, col_right = st.columns(2)
                    cat_l = cats[i]
                    with col_left:
                        st.markdown(f"#### {cat_l}")
                        st.table(pd.DataFrame(specs_data[cat_l]).rename(columns={"name": "Parameter", "value": "Spec", "unit": "Unit"}))
                    if i + 1 < len(cats):
                        cat_r = cats[i+1]
                        with col_right:
                            st.markdown(f"#### {cat_r}")
                            st.table(pd.DataFrame(specs_data[cat_r]).rename(columns={"name": "Parameter", "value": "Spec", "unit": "Unit"}))

    def render_schematics_tab(self, tab):
        with tab:
            st.subheader("🛠️ Local Schematics Browser")
            files = [f for f in os.listdir(config.SCHEMATICS_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            if not files:
                st.info("No images found in schematics folder.")
            else:
                selected_file = st.selectbox("Select Schematic:", files)
                if selected_file:
                    st.image(os.path.join(config.SCHEMATICS_DIR, selected_file), use_container_width=True)

    def render_parts_tab(self, tab):
        with tab:
            st.subheader("🔍 Parts Search")
            search_query = st.text_input("Part name or number:", placeholder="e.g. Brake...")
            if search_query:
                df_results = self.db.search_parts(search_query)
                if not df_results.empty:
                    for _, row in df_results.iterrows():
                        with st.expander(f"📦 {row['Description']} ({row['Part_Number']})"):
                            c1, c2 = st.columns([1, 1.5])
                            with c1:
                                st.write(f"**Price:** {row['Price_Euro']} €")
                                st.markdown(f"[🔗 Part Link](https://partsss.com/en/search/part/{row['Part_Number']})")
                            with c2:
                                if row['Image_URL'] != "No Image":
                                    st.image(row['Image_URL'], use_container_width=True)

    def render_ai_mechanic_tab(self, tab, current_mileage, history):
        with tab:
            st.subheader("🤖 Virtual AI Mechanic")
            for message in st.session_state.chat_history:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
            if prompt := st.chat_input("What's the issue?"):
                st.session_state.chat_history.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        try:
                            answer, img_info = ai_mechanic.get_ai_response(
                                prompt, current_mileage, history, 
                                st.session_state.chat_history, self.api_key, self.db
                            )
                            st.markdown(answer)
                            if img_info:
                                st.image(img_info['url'], caption=img_info['category'])
                            st.session_state.chat_history.append({"role": "assistant", "content": answer})
                        except Exception as e:
                            error_msg = f"The AI Mechanic encountered an error: {e}"
                            st.error(error_msg)
                            st.session_state.chat_history.append({"role": "assistant", "content": error_msg})

    def render_history_tab(self, tab, history):
        with tab:
            st.subheader("📋 Service Logs & Analytics")
            if history:
                st.dataframe(pd.DataFrame(history), use_container_width=True)
                st.divider()
                
                # Combine Maintenance and Fuel data for Analytics
                df_h = pd.DataFrame(history)
                df_h['date'] = pd.to_datetime(df_h['date'])
                
                # Categorize Maintenance History
                parts_keywords = ["filter", "plug", "belt", "weights", "fluid", "part", "tyre", "tire", "brake", "oil", "coolant", "battery", "spark", "roller"]
                def categorize(task):
                    if any(kw in task.lower() for kw in parts_keywords):
                        return "Parts"
                    return "Service"
                
                df_h['Category'] = df_h['task'].apply(categorize)
                df_h = df_h[['date', 'cost', 'Category']]
                
                # Get Fuel data
                fuel_df = self.db.get_fuel_history()
                if not fuel_df.empty:
                    df_f = fuel_df[['date', 'price']].rename(columns={'price': 'cost'})
                    df_f['Category'] = 'Fuel'
                    combined_df = pd.concat([df_h, df_f], ignore_index=True)
                else:
                    combined_df = df_h

                combined_df['Month'] = combined_df['date'].dt.to_period('M').dt.to_timestamp()
                
                # Group by Month and Category
                monthly_stats = combined_df.groupby(['Month', 'Category'])['cost'].sum().reset_index()
                
                st.write("### 💰 Monthly Expense Breakdown")
                fig = px.bar(monthly_stats, x='Month', y='cost', color='Category',
                             title='Expenses by Category',
                             labels={'cost': 'Total Cost (₪)', 'Month': 'Month'},
                             barmode='stack')
                fig.update_xaxes(dtick="M1", tickformat="%b %Y")
                st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    db = ScooterDB(config.DB_PATH, config.DATA_FILE)
    app = DashboardApp(db)
    app.run()
