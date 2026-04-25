import streamlit as st
import os
import pandas as pd
from datetime import date
from dotenv import load_dotenv

import config
import ui_styles
from database_manager import ScooterDB
import ai_mechanic
import plotly.express as px
from streamlit_lottie import st_lottie
import requests
from utils.logging_cfg import setup_logging
from utils.validation import Validator, ValidationError
from services.maintenance import get_predictive_tasks, estimate_due_date

setup_logging()


class DashboardApp:
    def __init__(self, db: ScooterDB):
        self.db = db
        self.load_environment()
        self.setup_ui()

    def load_lottieurl(self, url: str):
        try:
            r = requests.get(url, timeout=5)
            if r.status_code != 200:
                return None
            return r.json()
        except Exception:
            return None

    def load_environment(self):
        load_dotenv()
        self.api_key = os.getenv("GEMINI_API_KEY")
        ai_mechanic.setup_gemini(self.api_key)

        for folder in [config.SCHEMATICS_DIR, config.DOCS_DIR]:
            os.makedirs(folder, exist_ok=True)

        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = self.db.get_chat_history()

    def setup_ui(self):
        ui_styles.apply_custom_css()

    def get_last_service_km(self, task_name):
        keywords = config.MAINTENANCE_INTERVALS[task_name]["keywords"]
        return self.db.get_last_service_km(keywords)

    def render_sidebar(self, current_mileage, usage_stats):
        with st.sidebar:
            image_url = "https://imgd.aeplcdn.com/1280x360/bw/models/yamaha-xmax-400-tech-max-standard20200508124956.jpg"
            try:
                st.image(image_url, use_container_width=True)
            except Exception:
                st.warning("⚠️ 2020 Yamaha XMAX 400 Tech Max")

            st.markdown(
                "<h2 style='text-align: center; color: #D4AF37; font-family: Orbitron; "
                "font-size: 1.8rem; text-shadow: 0 0 10px rgba(212,175,55,0.5);'>TECH MAX</h2>",
                unsafe_allow_html=True,
            )
            st.markdown(
                "<p style='text-align: center; color: #64748B; font-size: 0.8rem; margin-top: -10px;'>SPECIAL EDITION</p>",
                unsafe_allow_html=True,
            )

            st.write("---")
            st.markdown("#### 🧭 NAVIGATION")
            page = st.selectbox("Go to:", [
                "📊 Dashboard", "🔧 Log Service", "🚨 Repairs", "⛽ Fuel",
                "📚 Specs", "🛠️ Schematics", "🔍 Parts", "🤖 AI Mechanic", "📋 History"
            ])

            st.write("---")
            st.markdown("#### ⛽ QUICK FUEL LOG")
            with st.container():
                q_liters = st.number_input("Liters", min_value=0.1, max_value=20.0, step=0.1, key="q_liters")
                q_price = st.number_input("Total Price (₪)", min_value=0.0, step=1.0, key="q_price")
                if st.button("➕ LOG FUEL"):
                    try:
                        Validator.validate_fuel_entry(q_liters, q_price)
                        self.db.add_fuel_log(str(date.today()), current_mileage, q_liters, q_price)
                        st.toast("Fuel log added!")
                        st.rerun()
                    except (ValidationError, Exception) as e:
                        st.error(str(e))

            st.write("---")
            st.markdown("#### 🛠️ ODOMETER")
            new_km = st.number_input(
                "Enter KM", value=current_mileage, step=100,
                label_visibility="collapsed", min_value=current_mileage
            )
            if new_km != current_mileage:
                try:
                    self.db.update_mileage(new_km)
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

            if usage_stats:
                st.write("---")
                st.markdown("#### 📈 ANALYTICS")
                col_a, col_b = st.columns(2)
                col_a.metric("DAILY", f"{usage_stats['avg_km_day']:.0f} km")
                col_b.metric("MONTHLY", f"{usage_stats['avg_km_month']:.0f} km")

        return page

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

        page = self.render_sidebar(current_mileage, usage_stats)
        self.render_header(current_mileage, history)

        if page == "📊 Dashboard":
            self.render_dashboard_tab(current_mileage, usage_stats)
        elif page == "🔧 Log Service":
            self.render_log_service_tab(current_mileage)
        elif page == "🚨 Repairs":
            self.render_repairs_tab()
        elif page == "⛽ Fuel":
            self.render_fuel_tab(current_mileage)
        elif page == "📚 Specs":
            self.render_specs_tab()
        elif page == "🛠️ Schematics":
            self.render_schematics_tab()
        elif page == "🔍 Parts":
            self.render_parts_tab()
        elif page == "🤖 AI Mechanic":
            self.render_ai_mechanic_tab(current_mileage, history)
        elif page == "📋 History":
            self.render_history_tab(history)

    def render_dashboard_tab(self, current_mileage, usage_stats):
        lottie_scooter = self.load_lottieurl("https://lottie.host/677028b1-382a-4389-9e8c-8f9d0c644d6c/U06ZInJvC9.json")
        if lottie_scooter:
            st_lottie(lottie_scooter, height=200, key="scooter_anim")

        st.subheader("🛡️ Maintenance Health")
        for task, info in config.MAINTENANCE_INTERVALS.items():
            last_km = self.get_last_service_km(task)
            ui_styles.draw_health_bar(task, current_mileage, info['interval'], last_km)

            if usage_stats and usage_stats['avg_km_day'] > 0:
                km_since = current_mileage - last_km
                km_left = info['interval'] - km_since
                due = estimate_due_date(km_left, usage_stats['avg_km_day'])
                if due:
                    days_left = (due - date.today()).days
                    st.caption(f"📅 Estimated due: **{due.strftime('%d %b %Y')}** ({days_left} days)")
                else:
                    st.error(f"⚠️ OVERDUE by {abs(km_left):,} KM!")

        st.write("---")
        st.subheader("🔮 Predictive Maintenance")
        if usage_stats and usage_stats['avg_km_day'] > 0:
            for task in get_predictive_tasks(config.MAINTENANCE_INTERVALS):
                if task not in config.MAINTENANCE_INTERVALS:
                    continue
                info = config.MAINTENANCE_INTERVALS[task]
                last_km = self.get_last_service_km(task)
                km_since = current_mileage - last_km
                km_left = info['interval'] - km_since
                progress = min(max(km_since / info['interval'], 0.0), 1.0)
                due = estimate_due_date(km_left, usage_stats['avg_km_day'])
                days_left = (due - date.today()).days if due else 0

                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{task}**")
                    st.progress(progress)
                with col2:
                    st.write(f"{days_left} days left" if due else "OVERDUE")

                if due and 0 < days_left <= 14:
                    st.markdown(
                        f"<p style='color: #FF4B4B; font-weight: bold;'>🚨 URGENT: {task} replacement predicted on {due.strftime('%d %b %Y')}!</p>",
                        unsafe_allow_html=True,
                    )
                elif km_left <= 0:
                    st.markdown(
                        f"<p style='color: #FF4B4B; font-weight: bold;'>🚨 CRITICAL: {task} is OVERDUE!</p>",
                        unsafe_allow_html=True,
                    )
                elif due:
                    st.caption(f"Next replacement: {due.strftime('%d %b %Y')}")
        else:
            st.info("💡 Start logging your mileage to enable predictive analytics!")

    def render_log_service_tab(self, current_mileage):
        st.subheader("Record New Maintenance")
        with st.form("service_form", clear_on_submit=True):
            s_task = st.text_input("Service Description (e.g. Oil Change)")
            s_km = st.number_input("Mileage", value=current_mileage, min_value=0)
            s_cost = st.number_input("Cost (₪)", min_value=0.0)
            s_date = st.date_input("Date", date.today())
            s_notes = st.text_area("Notes")
            if st.form_submit_button("✅ Save Service"):
                try:
                    task = Validator.validate_task(s_task)
                    self.db.add_service_log(str(s_date), task, s_km, s_cost, s_notes)
                    st.toast("Service saved!")
                    st.rerun()
                except (ValidationError, Exception) as e:
                    st.error(str(e))

    def render_repairs_tab(self):
        st.subheader("🚨 Pending Repairs & To-Do List")
        c1, c2 = st.columns([1, 2])
        with c1:
            st.markdown("#### ➕ Add Task")
            with st.form("todo_form", clear_on_submit=True):
                t_task = st.text_input("What needs fixing?")
                t_priority = st.selectbox("Priority", ["Low", "Medium", "High"])
                if st.form_submit_button("Add to List"):
                    try:
                        task = Validator.validate_task(t_task)
                        self.db.add_todo_item(task, t_priority)
                        st.toast(f"Added: {task}")
                        st.rerun()
                    except (ValidationError, Exception) as e:
                        st.error(str(e))
        with c2:
            st.markdown("#### 📋 Open Tasks")
            try:
                todo_df = self.db.get_todo_list()
                if todo_df.empty:
                    st.success("🎉 Everything is fixed!")
                else:
                    for _, row in todo_df.iterrows():
                        color = "🔴" if row['priority'] == "High" else "🟡" if row['priority'] == "Medium" else "🟢"
                        col_task, col_btn = st.columns([4, 1])
                        col_task.markdown(f"**{color} {row['task']}**")
                        col_task.caption(f"Added: {row['added_date']}")
                        confirm_key = f"confirm_todo_{row['id']}"
                        if col_btn.button("Done", key=f"todo_{row['id']}"):
                            st.session_state[confirm_key] = True
                        if st.session_state.get(confirm_key):
                            st.warning(f"Mark '{row['task']}' as complete?")
                            yes_col, no_col = st.columns(2)
                            if yes_col.button("Yes", key=f"yes_{row['id']}"):
                                try:
                                    self.db.complete_todo_item(row['id'])
                                    st.session_state.pop(confirm_key, None)
                                    st.toast("Task completed!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(str(e))
                            if no_col.button("Cancel", key=f"no_{row['id']}"):
                                st.session_state.pop(confirm_key, None)
                                st.rerun()
            except Exception as e:
                st.error(f"Failed to load todo list: {e}")

    def render_fuel_tab(self, current_mileage):
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
                        Validator.validate_fuel_entry(f_liters, f_price)
                        self.db.add_fuel_log(str(f_date), f_km, f_liters, f_price)
                        st.toast("Fuel logged!")
                        st.rerun()
                    except (ValidationError, Exception) as e:
                        st.error(str(e))
        with c2:
            fuel_df = self.db.get_fuel_history()
            if not fuel_df.empty and len(fuel_df) > 1:
                st.write("### 📈 Fuel Efficiency (KM/L)")
                fuel_df['km_per_l'] = fuel_df['km_diff'] / fuel_df['liters']
                plot_df = fuel_df.dropna(subset=['km_per_l'])

                fig = px.line(
                    plot_df, x='date', y='km_per_l',
                    title='KM/L Over Time',
                    labels={'km_per_l': 'KM/L', 'date': 'Date'},
                    markers=True,
                )
                fig.update_layout(hovermode="x unified")
                st.plotly_chart(fig, use_container_width=True)

                avg_km_l = plot_df['km_per_l'].mean()
                col_a, col_b, col_c = st.columns(3)
                col_a.metric("Avg Efficiency", f"{avg_km_l:.2f} KM/L")
                col_b.metric("Total Liters", f"{fuel_df['liters'].sum():.1f} L")
                col_c.metric("Total Fuel Cost", f"₪ {fuel_df['price'].sum():.0f}")

                st.download_button(
                    label="📥 Download Fuel CSV",
                    data=fuel_df[['date', 'km', 'liters', 'price']].to_csv(index=False).encode("utf-8"),
                    file_name=f"xmax_fuel_{date.today()}.csv",
                    mime="text/csv",
                )
            else:
                st.info("Log 2+ refuels to see stats and charts.")

    def render_specs_tab(self):
        st.subheader("📚 Detailed Technical Specifications")
        spec_result = self.db.get_tech_specs()
        if spec_result["status"] == "success":
            specs_data = spec_result["data"]
            cats = list(specs_data.keys())
            for i in range(0, len(cats), 2):
                col_left, col_right = st.columns(2)
                with col_left:
                    st.markdown(f"#### {cats[i]}")
                    st.table(pd.DataFrame(specs_data[cats[i]]).rename(
                        columns={"name": "Parameter", "value": "Spec", "unit": "Unit"}
                    ))
                if i + 1 < len(cats):
                    with col_right:
                        st.markdown(f"#### {cats[i+1]}")
                        st.table(pd.DataFrame(specs_data[cats[i+1]]).rename(
                            columns={"name": "Parameter", "value": "Spec", "unit": "Unit"}
                        ))
        else:
            st.error(spec_result.get("message", "Failed to load specs."))

    def render_schematics_tab(self):
        st.subheader("🛠️ Local Schematics Browser")
        files = [
            f for f in os.listdir(config.SCHEMATICS_DIR)
            if f.lower().endswith(('.jpg', '.jpeg', '.png'))
        ]
        if not files:
            st.info("No images found in the schematics folder. Add JPG/PNG files to the `schematics/` directory.")
        else:
            selected_file = st.selectbox("Select Schematic:", files)
            if selected_file:
                st.image(os.path.join(config.SCHEMATICS_DIR, selected_file), use_container_width=True)

    def render_parts_tab(self):
        st.subheader("🔍 Parts Search")
        search_query = st.text_input("Part name or number:", placeholder="e.g. Brake, V-Belt, NGK...")
        if search_query:
            df_results = self.db.search_parts(search_query)
            if df_results.empty:
                st.info("No parts found. Run `python seed_parts.py` to populate the parts database.")
            else:
                st.caption(f"Found {len(df_results)} part(s)")
                for _, row in df_results.iterrows():
                    with st.expander(f"📦 {row['Description']} ({row['Part_Number']})"):
                        c1, c2 = st.columns([1, 1.5])
                        with c1:
                            st.write(f"**Category:** {row['Category']}")
                            st.write(f"**Price:** {row['Price_Euro']} €")
                        with c2:
                            if row['Image_URL'] != "No Image":
                                st.image(row['Image_URL'], use_container_width=True)

    def render_ai_mechanic_tab(self, current_mileage, history):
        st.subheader("🤖 Virtual AI Mechanic")

        _, col_clear = st.columns([5, 1])
        with col_clear:
            if st.button("🗑️ Clear"):
                st.session_state["confirm_clear_chat"] = True

        if st.session_state.get("confirm_clear_chat"):
            st.warning("Clear all chat history?")
            yes_col, no_col = st.columns(2)
            if yes_col.button("Yes, clear", key="yes_clear_chat"):
                self.db.clear_chat_history()
                st.session_state.chat_history = []
                st.session_state.pop("confirm_clear_chat", None)
                st.rerun()
            if no_col.button("Cancel", key="no_clear_chat"):
                st.session_state.pop("confirm_clear_chat", None)
                st.rerun()

        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("What's the issue?"):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            self.db.save_chat_message("user", prompt)
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
                        self.db.save_chat_message("assistant", answer)
                    except Exception as e:
                        error_msg = "The AI Mechanic encountered an error. Please try again later."
                        st.error(error_msg)
                        st.session_state.chat_history.append({"role": "assistant", "content": error_msg})
                        self.db.save_chat_message("assistant", error_msg)

    def render_history_tab(self, history):
        st.subheader("📋 Service Logs & Analytics")
        if not history:
            st.info("No service history yet. Log your first service in the 'Log Service' tab.")
            return

        st.dataframe(pd.DataFrame(history), use_container_width=True)

        st.download_button(
            label="📥 Download History CSV",
            data=pd.DataFrame(history).to_csv(index=False).encode("utf-8"),
            file_name=f"xmax_history_{date.today()}.csv",
            mime="text/csv",
        )

        st.divider()

        df_h = pd.DataFrame(history)
        df_h['date'] = pd.to_datetime(df_h['date'])

        def categorize(task):
            if any(kw in task.lower() for kw in config.COST_CATEGORY_KEYWORDS):
                return "Parts"
            return "Service"

        df_h['Category'] = df_h['task'].apply(categorize)
        df_h = df_h[['date', 'cost', 'Category']]

        fuel_df = self.db.get_fuel_history()
        if not fuel_df.empty:
            df_f = fuel_df[['date', 'price']].rename(columns={'price': 'cost'})
            df_f['Category'] = 'Fuel'
            combined_df = pd.concat([df_h, df_f], ignore_index=True)
        else:
            combined_df = df_h

        combined_df['Month'] = combined_df['date'].dt.to_period('M').dt.to_timestamp()
        monthly_stats = combined_df.groupby(['Month', 'Category'])['cost'].sum().reset_index()

        st.write("### 💰 Monthly Expense Breakdown")
        fig = px.bar(
            monthly_stats, x='Month', y='cost', color='Category',
            title='Expenses by Category',
            labels={'cost': 'Total Cost (₪)', 'Month': 'Month'},
            barmode='stack',
        )
        fig.update_xaxes(dtick="M1", tickformat="%b %Y")
        st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    db = ScooterDB(config.DB_PATH, config.DATA_FILE)
    app = DashboardApp(db)
    app.run()
