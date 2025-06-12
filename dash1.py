import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(layout="wide", page_title="Complaint Management Dashboard")

@st.cache_data

def load_data():
    file_path = "All Cases 2024-05-16 10-14-01.csv"
    df = pd.read_csv(file_path)
    df['Created On'] = pd.to_datetime(df['Created On'])
    df['(Do Not Modify) Modified On'] = pd.to_datetime(df['(Do Not Modify) Modified On'])
    return df

df = load_data()

today = pd.to_datetime(datetime.today().date())
last_week = today - timedelta(days=7)

import streamlit as st
import pandas as pd
from datetime import datetime

# Ensure 'Created On' is in datetime format
df["Created On"] = pd.to_datetime(df["Created On"])

st.sidebar.header("📅 Filters")

# Ensure 'today' is defined
today = pd.to_datetime(datetime.today().date())

# Date picker
today = pd.to_datetime(datetime.today().date())
selected_date = st.sidebar.date_input("Select Date", today)

# Origin options with 'All'
origin_list = df["Origin"].dropna().unique().tolist()
all_origin_options = ["All"] + origin_list
selected_origin = st.sidebar.multiselect("Select Origin", options=all_origin_options, default=["All"])
origin_to_filter = origin_list if "All" in selected_origin else selected_origin

# Owner options with 'All'
owner_list = df["Owner"].dropna().unique().tolist()
all_owners_option = ["All"] + owner_list
selected_owners = st.sidebar.multiselect("Select Owners", options=all_owners_option, default=["All"])
owners_to_filter = owner_list if "All" in selected_owners else selected_owners

# Apply filters
filtered_df = df[
    (df["Created On"].dt.date <= selected_date) &
    (df["Origin"].isin(origin_to_filter)) &
    (df["Owner"].isin(owners_to_filter))
]

tab1, tab2 = st.tabs(["📊 Dashboard Overview", "👨‍💼 Owner Performance"])

with tab1:
    # --- KPI styles for modern cards ---
 kpi_style = """
    <style>
        .kpi-card {
            background-color: #f9ebea;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.05);
            text-align: center;
            transition: 0.3s;
            margin: 5px 0;
        }
        .kpi-card:hover {
            box-shadow: 0 6px 12px rgba(0,0,0,0.1);
        }
        .kpi-label {
            font-size: 16px;
            color: #6c757d;
            margin-bottom: 8px;
        }
        .kpi-value {
            font-size: 32px;
            font-weight: bold;
            color: #2c3e50;
        }
    </style>
"""
st.markdown(kpi_style, unsafe_allow_html=True)

# --- Compute KPI values ---
todays_cases = filtered_df[filtered_df["Created On"].dt.date == today.date()].shape[0]
last_week_cases = filtered_df[(filtered_df["Created On"] >= last_week) & (filtered_df["Created On"] <= today)].shape[0]
total_resolved = filtered_df[filtered_df["Status Reason"].str.contains("Resolved", na=False)].shape[0]
open_complaints = filtered_df[~filtered_df["Status Reason"].str.contains("Resolved|Declined|Closed", na=False)].shape[0]

# --- Display KPIs inside containers ---
with tab1:
    st.title("Complaint Management Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        with st.container():
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">📝 Today's Complaints</div>
                    <div class="kpi-value">{todays_cases}</div>
                </div>
            """, unsafe_allow_html=True)

    with col2:
        with st.container():
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">📅 Last Week's Complaints</div>
                    <div class="kpi-value">{last_week_cases}</div>
                </div>
            """, unsafe_allow_html=True)

    with col3:
        with st.container():
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">✅ Total Resolved</div>
                    <div class="kpi-value">{total_resolved}</div>
                </div>
            """, unsafe_allow_html=True)

    with col4:
        with st.container():
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">📂 Open Complaints</div>
                    <div class="kpi-value">{open_complaints}</div>
                </div>
            """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("📌 Complaint Origins")
        origin_counts = filtered_df["Origin"].value_counts().reset_index()
        origin_counts.columns = ["Origin", "count"]
        fig_origin = px.pie(origin_counts, names="Origin", values="count", title="Complaint Origin Breakdown")
        st.plotly_chart(fig_origin, use_container_width=True)

    with c2:
        st.subheader("📊 Complaint Status")
        status_counts = filtered_df["Status Reason"].value_counts().reset_index()
        status_counts.columns = ["Status Reason", "count"]
        fig_status = px.bar(status_counts, x="Status Reason", y="count", title="Status of Complaints")
        st.plotly_chart(fig_status, use_container_width=True)

    st.subheader("📈 Complaints Over Time")
    df_time = filtered_df.copy()
    df_time["Date"] = df_time["Created On"].dt.date
    daily_counts = df_time.groupby("Date").size().reset_index(name="Complaints")
    fig_timeline = px.line(daily_counts, x="Date", y="Complaints", title="Complaint Trends Over Time")
    st.plotly_chart(fig_timeline, use_container_width=True)

with tab2:
    st.subheader("👨‍💼 Owner Resolution Performance")

    owner_total = filtered_df["Owner"].value_counts().reset_index()
    owner_total.columns = ["Owner", "Total"]

    resolved_df = filtered_df[filtered_df["Status Reason"].str.contains("Resolved", na=False)]
    resolved_df["Resolution Time (Days)"] = (resolved_df["(Do Not Modify) Modified On"] - resolved_df["Created On"]).dt.total_seconds() / 86400

    owner_resolved = resolved_df["Owner"].value_counts().reset_index()
    owner_resolved.columns = ["Owner", "Resolved"]

    avg_time = resolved_df.groupby("Owner")["Resolution Time (Days)"].mean().reset_index()
    avg_time.columns = ["Owner", "Avg Resolution Time (Days)"]

    owner_perf = pd.merge(owner_total, owner_resolved, on="Owner", how="left")
    owner_perf = pd.merge(owner_perf, avg_time, on="Owner", how="left")
    owner_perf["Resolved"] = owner_perf["Resolved"].fillna(0).astype(int)
    owner_perf["Avg Resolution Time (Days)"] = owner_perf["Avg Resolution Time (Days)"].fillna(0).round(1)
    owner_perf["Percent"] = (owner_perf["Resolved"] / owner_perf["Total"] * 100).round(1)
    owner_perf = owner_perf.sort_values(by="Percent", ascending=False).reset_index(drop=True)

    def get_color(percent):
        if percent >= 75:
            return "#4CAF50"
        elif percent >= 50:
            return "#2196F3"
        elif percent >= 25:
            return "#FF9800"
        else:
            return "#F44336"

    def time_tag(days):
        if days <= 2:
            return f"<span style='color: green;'>🟢 {days} days</span>"
        elif days <= 5:
            return f"<span style='color: orange;'>🟡 {days} days</span>"
        else:
            return f"<span style='color: red;'>🔴 {days} days</span>"

    visible = owner_perf.head(6)
    extra = owner_perf.iloc[6:]

    cols = st.columns(3)
    for idx, row in visible.iterrows():
        color = get_color(row["Percent"])
        col = cols[idx % 3]
        with col:
            st.markdown(f"""
            <div style="background-color: #f9f9f9; border: 1px solid #ddd; border-radius: 10px; padding: 15px; margin: 10px 0;">
                <h4 style="margin-bottom: 5px;">{row['Owner']}</h4>
                <p style="margin: 5px 0;">✅ <b>{row['Resolved']}</b> of <b>{row['Total']}</b> resolved</p>
                <p style="margin: 5px 0;">📊 <b>{row['Percent']}%</b> resolution rate</p>
                <p style="margin: 5px 0;">🕒 Avg Time: {time_tag(row['Avg Resolution Time (Days)'])}</p>
                <div style="background-color: #ddd; border-radius: 5px; height: 12px; overflow: hidden;">
                    <div style="width: {row['Percent']}%; background-color: {color}; height: 100%;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    if not extra.empty:
        with st.expander("🔽 View More Owner Performance"):
            more_cols = st.columns(3)
            for idx, row in extra.iterrows():
                color = get_color(row["Percent"])
                col = more_cols[idx % 3]
                with col:
                    st.markdown(f"""
                    <div style="background-color: #f9f9f9; border: 1px solid #ddd; border-radius: 10px; padding: 15px; margin: 10px 0;">
                        <h4 style="margin-bottom: 5px;">{row['Owner']}</h4>
                        <p style="margin: 5px 0;">✅ <b>{row['Resolved']}</b> of <b>{row['Total']}</b> resolved</p>
                        <p style="margin: 5px 0;">📊 <b>{row['Percent']}%</b> resolution rate</p>
                        <p style="margin: 5px 0;">🕒 Avg Time: {time_tag(row['Avg Resolution Time (Days)'])}</p>
                        <div style="background-color: #ddd; border-radius: 5px; height: 12px; overflow: hidden;">
                            <div style="width: {row['Percent']}%; background-color: {color}; height: 100%;"></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

st.markdown("---")
st.caption("Generated with 💼 Streamlit for Complaint Analysis - CCA Dashboard 2024")
