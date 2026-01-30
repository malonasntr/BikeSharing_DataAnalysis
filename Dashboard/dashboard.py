import pandas as pd
import seaborn as sns
import streamlit as st
import plotly.graph_objects as go
sns.set(style='dark')

import os

def load_data():
    base_dir = os.path.dirname(__file__)
    day_path = os.path.join(base_dir, "day_clean.csv")
    hour_path = os.path.join(base_dir, "hour_clean.csv")

    day_df = pd.read_csv(day_path)
    hour_df = pd.read_csv(hour_path)

    day_df['dateday'] = pd.to_datetime(day_df['dateday'])
    hour_df['dateday'] = pd.to_datetime(hour_df['dateday'])

    return day_df, hour_df
    
st.title("🚲 Bike Sharing Dashboard")
st.caption("Analisis Pola Penyewaan Sepeda 2011-2012 | Dicoding Data Science")

with st.sidebar:
    st.header("🔎 Filter Data")

    start_date, end_date = st.date_input(
        "Pilih Rentang Tanggal",
        [
            hour_df['dateday'].min().date(),
            hour_df['dateday'].max().date()
        ])

    hour_range = st.slider(
        "Rentang Jam",
        min_value=0,
        max_value=23,
        value=(0, 23)
    )

    weather_filter = st.selectbox(
        "Kondisi Cuaca",
        ["Semua", "Clear / Partly Cloudy", "Light Rain / Snow", "Misty / Cloudy"]
    )

main_day_df = day_df[
    (day_df["dateday"] >= pd.to_datetime(start_date)) &
    (day_df["dateday"] <= pd.to_datetime(end_date))
]

main_hour_df = hour_df[
    (hour_df["dateday"] >= pd.to_datetime(start_date)) &
    (hour_df["dateday"] <= pd.to_datetime(end_date))
]

# Filter jam
main_hour_df = main_hour_df[
    (main_hour_df["hour"] >= hour_range[0]) &
    (main_hour_df["hour"] <= hour_range[1])
]

# Filter cuaca
if weather_filter != "Semua":
    main_hour_df = main_hour_df[main_hour_df["weather_label"] == weather_filter]

st.subheader('Daily Orders🌻')
col1, col2, col3 = st.columns(3)

with col1:

    st.metric("Total Penyewaan", f"{main_hour_df['count'].sum():,}")

with col2:
    st.metric("Rata-rata Harian", round(main_hour_df['count'].mean(), 1))

with col3:
    st.metric("Hari Aktif", main_hour_df['dateday'].nunique())

# Monthly Order
st.subheader('Monthly Orders📈')
monthly_orders_df = (
    main_hour_df.groupby(pd.Grouper(key="dateday", freq="M"))["count"].sum().reset_index()
    )

monthly_orders_df["month"] = monthly_orders_df["dateday"].dt.strftime("%Y-%m")

fig_monthly = go.Figure()

fig_monthly.add_trace(go.Scatter(
    x=monthly_orders_df["month"],
    y=monthly_orders_df["count"],
    mode="lines+markers",
    line=dict(width=2),
    marker=dict(size=6),
    name="Total Orders"
))

fig_monthly.update_layout(
    xaxis_title="Bulan",
    yaxis_title="Total Penyewaan",
    template="plotly_dark",
    hovermode="x unified"
)

st.plotly_chart(fig_monthly, use_container_width=True)

# Weather
weather_rental_df = main_hour_df.groupby("weather_label").agg({
    "count": "mean"
    }).reset_index()
weather_rental_df = weather_rental_df.sort_values("count", ascending=False)
max_value = weather_rental_df["count"].max()

# Season
season_rental_df = main_hour_df.groupby(by="season_label").agg({
    "count": "mean"
}).reset_index()
season_rental_df = season_rental_df.sort_values("count", ascending=False)


st.subheader("Pola Penyewaan Sepeda Berdasarkan Faktor Lingkungan")

# Coloring
colors = [
    "#4A3283" if val == max_value else "#B9ACEA"
    for val in weather_rental_df["count"]
]

# Visualisasi Rata-rata Penyewaan Berdasarkan Kondisi Cuaca
fig_weather = go.Figure()

fig_weather.add_trace(go.Bar(
    x=weather_rental_df["weather_label"],
    y=weather_rental_df["count"],
    name="Cuaca",
    marker_color=colors
))

fig_weather.update_layout(
    title="Rata-rata Penyewaan Berdasarkan Kondisi Cuaca⛅️",
    xaxis_title="Cuaca",
    yaxis_title="Rata-rata Penyewaan",
    template="plotly_dark"
)

fig_weather.update_traces(
    text=weather_rental_df["count"].round(1),
    textposition="outside"
)

st.plotly_chart(fig_weather, use_container_width=True)


max_value = season_rental_df["count"].max()

# Coloring
colors = [
    "#3257AE" if val == max_value else "#8FBCF3"
    for val in season_rental_df["count"]
]

# Visualisasi Rata-rata Penyewaan Berdasarkan Musim
fig_season = go.Figure()

fig_season.add_trace(go.Bar(
    x=season_rental_df["season_label"],
    y=season_rental_df["count"],
    name="Musim",
    marker_color=colors
))

fig_season.update_layout(
    title="Rata-rata Penyewaan Berdasarkan Kondisi Musim❄️",
    xaxis_title="Musim",
    yaxis_title="Rata-rata Penyewaan",
    template="plotly_dark"
)

fig_season.update_traces(
    text=season_rental_df["count"].round(1),
    textposition="outside"
)
st.plotly_chart(fig_season, use_container_width=True)


# Berdasarkan Hari Kerja
st.markdown("---")
workingday_rental_df = main_hour_df.groupby("workingday").agg({
    "count": "mean"
}).reset_index()

workingday_rental_df["workingday_label"] = workingday_rental_df["workingday"].map({
    0: "Libur",
    1: "Hari Kerja"
})

workingday_rental_df = workingday_rental_df.sort_values("count", ascending=False)

max_value = workingday_rental_df["count"].max()
colors = [
    "#A75851" if val == max_value else "#EDC3B7"
    for val in workingday_rental_df["count"]
]

st.subheader("Pola Penyewaan Sepeda Berdasarkan Hari Kerja📆")

fig_workingday = go.Figure()

fig_workingday.add_trace(go.Bar(
    x=workingday_rental_df["workingday_label"],
    y=workingday_rental_df["count"],
    marker_color=colors
))

fig_workingday.update_layout(
    xaxis_title="Jenis Hari",
    yaxis_title="Rata-rata Penyewaan",
    template="plotly_dark"
)

fig_workingday.update_traces(
    text=workingday_rental_df["count"].round(1),
    textposition="outside"
)

st.plotly_chart(fig_workingday, use_container_width=True)
st.caption(
    "Note: Distribusi pengguna Casual dan Registered dianalisis lebih lanjut pada visualisasi per jam di bawah."
)

# Pola Penyewaan Sepeda per Jam
st.markdown("---")

st.subheader("Pola Penyewaan Sepeda per Jam🕛")

# Checkbox kontrol
show_casual = st.checkbox("Tampilkan Casual", value=True)
show_registered = st.checkbox("Tampilkan Registered", value=True)

# Agregasi data
holiday_hourly = (
    main_hour_df[main_hour_df['workingday'] == 0].groupby("hour")[["casual", "registered"]].sum().reset_index()
)

workday_hourly = (
    main_hour_df[main_hour_df['workingday'] == 1].groupby("hour")[["casual", "registered"]].sum().reset_index()
)

fig = go.Figure()

# Casual
if show_casual:
    fig.add_trace(go.Scatter(
        x=holiday_hourly["hour"],
        y=holiday_hourly["casual"],
        mode='lines+markers',
        name='Casual (Libur)',
        line=dict(dash='dash')
    ))

    fig.add_trace(go.Scatter(
        x=workday_hourly["hour"],
        y=workday_hourly["casual"],
        mode='lines+markers',
        name='Casual (Kerja)'
    ))

# Registered
if show_registered:
    fig.add_trace(go.Scatter(
        x=holiday_hourly["hour"],
        y=holiday_hourly["registered"],
        mode='lines+markers',
        name='Registered (Libur)',
        line=dict(dash='dash')
    ))

    fig.add_trace(go.Scatter(
        x=workday_hourly["hour"],
        y=workday_hourly["registered"],
        mode='lines+markers',
        name='Registered (Kerja)'
    ))

fig.update_layout(
    title="Pola Penyewaan Sepeda per Jam (Hari Libur vs Hari Kerja)",
    xaxis_title="Hour",
    yaxis_title="Total Rental Count",
    xaxis=dict(tickmode='linear', tick0=0, dtick=1),
    template="plotly_dark"
)

st.plotly_chart(fig, use_container_width=True)
st.write("Range tanggal:", start_date, "s/d", end_date)
st.write("Jumlah baris hour:", len(main_hour_df))
st.write("Total rental:", main_hour_df["count"].sum())

# Analisis Lanjutan
st.markdown("---")
st.subheader("Clustering Analysis: Operational Efficiency✨️")
st.caption("Identifikasi Waktu dan Kondisi Suhu Optimal Berdasarkan Pola Penyewaan")

def time_category(hour):
    if 0 <= hour < 5:
        return "Early Morning"
    elif 5 <= hour < 11:
        return "Morning"
    elif 11 <= hour < 15:
        return "Afternoon"
    elif 15 <= hour < 19:
        return "Evening"
    else:
        return "Night"

def temp_category(temp):
    if temp < 0.3:
        return "Cool/Cold"
    elif temp < 0.6:
        return "Moderate/Normal"
    else:
        return "Warm/Hot"

main_hour_df["time_category"] = main_hour_df["hour"].apply(time_category)
main_hour_df["temp_category"] = main_hour_df["temp"].apply(temp_category)

# Agregasi rata-rata

time_mean = (
    main_hour_df
    .groupby("time_category", as_index=False)["count"]
    .mean()
)

temp_mean = (
    main_hour_df
    .groupby("temp_category", as_index=False)["count"]
    .mean()
)

# Peak Time
idx_time = time_mean["count"].idxmax()
peak_time_cat = time_mean.loc[idx_time, "time_category"]
peak_time_val = round(time_mean.loc[idx_time, "count"], 1)

# Peak Temp
idx_temp = temp_mean["count"].idxmax()
peak_temp_cat = temp_mean.loc[idx_temp, "temp_category"]
peak_temp_val = round(temp_mean.loc[idx_temp, "count"], 1)

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Waktu Paling Ramai",
        peak_time_cat,
        f"{peak_time_val} sewa/jam"
    )

with col2:
    st.metric(
        "Suhu Paling Optimal",
        peak_temp_cat,
        f"{peak_temp_val} sewa/hari"
    )

# Visualisasi Time 
order_time = ['Early Morning', 'Morning', 'Afternoon', 'Evening', 'Night']
time_mean = (
    time_mean.set_index("time_category").reindex(order_time).dropna().reset_index()
    )

time_mean = time_mean.sort_values("count", ascending=False)
max_time = time_mean["count"].max()

colors_time = [
    "#396D29" if val == max_time else "#8FC97E"
    for val in time_mean["count"]
    ]

fig_time = go.Figure()

fig_time.add_trace(go.Bar(
    x=time_mean["time_category"],
    y=time_mean["count"],
    marker_color=colors_time,
    text=time_mean["count"].round(1),
    textposition="outside"
    ))

fig_time.update_layout(
    title="Rata-rata Penyewaan Berdasarkan Kategori Waktu☀️",
    xaxis_title="Kategori Waktu",
    yaxis_title="Rata-rata Penyewaan",
    template="plotly_dark"
    )

st.plotly_chart(fig_time, use_container_width=True)

# Visualisasi Temp
order_temp = ['Cool/Cold', 'Moderate/Normal', 'Warm/Hot']
temp_mean = (
    temp_mean.set_index("temp_category").reindex(order_temp).dropna().reset_index()
    )

temp_mean = temp_mean.sort_values("count", ascending=False)
max_temp = temp_mean["count"].max()

colors_temp = [
    "#5B3E1C" if val == max_temp else "#CBB38A"
    for val in temp_mean["count"]
    ]

fig_temp = go.Figure()

fig_temp.add_trace(go.Bar(
    x=temp_mean["temp_category"],
    y=temp_mean["count"],
    marker_color=colors_temp,
    text=temp_mean["count"].round(1),
    textposition="outside"
))

fig_temp.update_layout(
    title="Rata-rata Penyewaan Berdasarkan Kategori Suhu🌡",
    xaxis_title="Kategori Suhu",
    yaxis_title="Rata-rata Penyewaan",
    template="plotly_dark"
)

st.plotly_chart(fig_temp, use_container_width=True)

st.caption('Copyright (c) Sarma Elvita Malona Sianturi')

