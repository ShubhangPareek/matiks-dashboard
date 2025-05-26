import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import timedelta

st.set_page_config(layout="wide", page_title="Matiks Dashboard")
st.title("📊 Matiks - User Behavior & Revenue Dashboard")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("data/Matiks - Data Analyst Data - Sheet1.csv")
    df['Signup_Date'] = pd.to_datetime(df['Signup_Date'], errors='coerce')
    df['Last_Login'] = pd.to_datetime(df['Last_Login'], errors='coerce')
    df['Login_Date'] = df['Last_Login'].dt.date
    return df

df = load_data()

# Sidebar filters
st.sidebar.header("🔍 Filter Data")
selected_country = st.sidebar.multiselect("Country", sorted(df['Country'].dropna().unique()))
selected_device = st.sidebar.multiselect("Device Type", sorted(df['Device_Type'].dropna().unique()))
selected_game = st.sidebar.multiselect("Game Title", sorted(df['Game_Title'].dropna().unique()))

if selected_country:
    df = df[df['Country'].isin(selected_country)]
if selected_device:
    df = df[df['Device_Type'].isin(selected_device)]
if selected_game:
    df = df[df['Game_Title'].isin(selected_game)]

# Active Users
st.header("🧑‍💻 Active User Metrics")
daily_active = df.groupby('Login_Date')['User_ID'].nunique().reset_index(name='DAU')
weekly_active = df.groupby(df['Last_Login'].dt.to_period("W"))['User_ID'].nunique().reset_index(name='WAU')
monthly_active = df.groupby(df['Last_Login'].dt.to_period("M"))['User_ID'].nunique().reset_index(name='MAU')

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total DAU Days", len(daily_active))
    st.line_chart(daily_active.rename(columns={'Login_Date': 'index'}).set_index('index'))
with col2:
    st.metric("Total WAU Weeks", len(weekly_active))
    st.line_chart(weekly_active.rename(columns={'Last_Login': 'index'}).set_index('index'))
with col3:
    st.metric("Total MAU Months", len(monthly_active))
    st.line_chart(monthly_active.rename(columns={'Last_Login': 'index'}).set_index('index'))

# Revenue Trends
st.header("💸 Revenue Trends Over Time")
revenue_trend = df.groupby(df['Last_Login'].dt.to_period("M"))['Total_Revenue_USD'].sum().reset_index()
revenue_trend['Last_Login'] = revenue_trend['Last_Login'].astype(str)
fig_rev = px.line(revenue_trend, x='Last_Login', y='Total_Revenue_USD', title='Monthly Revenue')
st.plotly_chart(fig_rev, use_container_width=True)

# Revenue Breakdown
st.header("📂 Revenue Breakdown by Segment")
col4, col5 = st.columns(2)
with col4:
    dev_rev = df.groupby('Device_Type')['Total_Revenue_USD'].sum().reset_index()
    fig1 = px.bar(dev_rev, x='Device_Type', y='Total_Revenue_USD', title='Revenue by Device Type')
    st.plotly_chart(fig1, use_container_width=True)
with col5:
    mode_rev = df.groupby('Preferred_Game_Mode')['Total_Revenue_USD'].mean().reset_index()
    fig2 = px.bar(mode_rev, x='Preferred_Game_Mode', y='Total_Revenue_USD', title='Avg Revenue by Game Mode')
    st.plotly_chart(fig2, use_container_width=True)

# Churn Users
st.header("⚠️ Potential Churn Users")
latest_login = df['Last_Login'].max()
churn_df = df[df['Last_Login'] < (latest_login - timedelta(days=14))]
st.write(f"Users inactive since before {latest_login - timedelta(days=14)}:")
st.dataframe(churn_df[['User_ID', 'Username', 'Last_Login', 'Total_Play_Sessions', 'Total_Revenue_USD']])

# High-Value Users
st.header("💎 Top High-Value Users")
top_users = df.sort_values(by='Total_Revenue_USD', ascending=False).head(10)
st.dataframe(top_users[['User_ID', 'Username', 'Total_Revenue_USD', 'Total_Hours_Played', 'In_Game_Purchases_Count', 'Preferred_Game_Mode']])

# Cohort Analysis
st.header("🧪 Cohort Analysis: Avg Revenue by Signup Month")
df['Signup_Month'] = df['Signup_Date'].dt.to_period("M").astype(str)
cohort_df = df.groupby('Signup_Month')['Total_Revenue_USD'].mean().reset_index()
fig_cohort = px.bar(cohort_df, x='Signup_Month', y='Total_Revenue_USD', title='Avg Revenue per User by Signup Month')
st.plotly_chart(fig_cohort, use_container_width=True)

# Export button
st.sidebar.header("⬇️ Export Data")
csv = df.to_csv(index=False).encode('utf-8')
st.sidebar.download_button("Download Filtered CSV", csv, "filtered_matiks_data.csv", "text/csv")