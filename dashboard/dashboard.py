import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

sns.set(style='dark')

def create_hourly_day_type_df(df):
    hourly_df = df.groupby(['hr', 'day_type'])['cnt'].mean().reset_index()
    return hourly_df

def create_seasonal_users_df(df):
    seasonal_df = df.groupby('season_label')[['casual', 'registered']].mean().reset_index()
    return seasonal_df

def create_time_category_df(df):
    def get_time_category(hour):
        if hour in [7, 8, 17, 18]:
            return 'Rush Hour'
        elif 9 <= hour <= 16:
            return 'Working Hours'
        else:
            return 'Off-Peak (Night/Early Morning)'
            
    df['time_category'] = df['hr'].apply(get_time_category)
    cluster_time_result = df.groupby('time_category')['cnt'].mean().reset_index()
    return cluster_time_result

script_dir = os.path.dirname(__file__)
file_path = os.path.join(script_dir, "hour.csv")

main_df = pd.read_csv(file_path)
main_df['dteday'] = pd.to_datetime(main_df['dteday'])

season_mapping = {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}
main_df['season_label'] = pd.Categorical(
    main_df['season'].map(season_mapping), 
    categories=['Spring', 'Summer', 'Fall', 'Winter'], 
    ordered=True
)

weather_mapping = {
    1: 'Clear/Partly Cloudy',
    2: 'Misty/Cloudy',
    3: 'Light Snow/Rain',
    4: 'Heavy Rain/Ice Pallets'
}
main_df['weather_label'] = main_df['weathersit'].map(weather_mapping)

workingday_mapping = {0: 'Weekend/Holiday', 1: 'Working Day'}
main_df['day_type'] = main_df['workingday'].map(workingday_mapping)

min_date = main_df['dteday'].min()
max_date = main_df['dteday'].max()

with st.sidebar:
    st.title("Bike Sharing Analytics")
    
    st.markdown("---")
    st.subheader("Filter Data")
    
    date_range = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
    
    if len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = min_date, max_date

    st.markdown("---")
    st.subheader("Tentang Dashboard")
    st.write("Dashboard ini menyajikan analisis data penyewaan sepeda (*Bike Sharing*) periode 2011-2012 untuk membandingkan jam sibuk penyewaan, tren musiman antar tipe pengguna, serta pengelompokan waktu operasional.")
    
    st.markdown("---")
    st.subheader("Informasi Dataset")
    st.write(f"- **Total Data:** {len(main_df):,} baris")
    st.write("- **Rentang Waktu:** 2011 - 2012")
    
    st.markdown("---")
    st.subheader("Author")
    st.write("**Nama:** Yohanes Pratama")
    st.write("**Submission:** Belajar Fundamental Analisis Data")

filtered_df = main_df[(main_df['dteday'] >= pd.to_datetime(start_date)) & 
                      (main_df['dteday'] <= pd.to_datetime(end_date))]

hourly_day_type_df = create_hourly_day_type_df(filtered_df)
seasonal_users_df = create_seasonal_users_df(filtered_df)
cluster_time_result = create_time_category_df(filtered_df)

st.header('Bike Sharing Dashboard Overview')
st.write("Selamat datang di Bike Sharing Dashboard. Gunakan filter rentang waktu di sidebar untuk mengeksplorasi data secara interaktif.")

st.markdown("---")

st.subheader("Pola Penyewaan Sepeda per Jam (Hari Kerja vs Hari Libur)")

fig1, ax1 = plt.subplots(figsize=(16, 6))
sns.lineplot(
    x="hr",
    y="cnt",
    hue="day_type",
    data=hourly_day_type_df,
    palette=["#FF9999", "#90CAF9"],
    linewidth=2.5,
    ax=ax1
)
ax1.set_title("Rata-rata Penyewaan Sepeda per Jam", fontsize=15)
ax1.set_ylabel("Rata-rata Penyewaan", fontsize=12)
ax1.set_xlabel("Jam (0-23)", fontsize=12)
ax1.set_xticks(range(0, 24))
ax1.legend(title="Tipe Hari")
st.pyplot(fig1)

st.write("**Hari Kerja (Working Day):** Terdapat lonjakan penyewaan yang signifikan pada jam sibuk berangkat kerja (07:00-08:00) dan pulang kerja (17:00-18:00).")
st.write("**Hari Libur (Weekend/Holiday):** Pola penyewaan cenderung terdistribusi merata di siang hari dari jam 10:00 hingga 16:00.")

st.markdown("---")

st.subheader("Tren Penyewaan per Musim antara Pengguna Kasual dan Terdaftar")

seasonal_melt = seasonal_users_df.melt(
    id_vars='season_label',
    value_vars=['casual', 'registered'],
    var_name='user_type',
    value_name='avg_rentals'
)

fig2, ax2 = plt.subplots(figsize=(12, 6))
sns.barplot(
    x="season_label",
    y="avg_rentals",
    hue="user_type",
    data=seasonal_melt,
    palette=["#D3D3D3", "#90CAF9"],
    ax=ax2
)
ax2.set_title("Rata-rata Penyewaan Berdasarkan Musim", fontsize=15)
ax2.set_ylabel("Rata-rata Penyewaan", fontsize=12)
ax2.set_xlabel("Musim", fontsize=12)
ax2.legend(title="Tipe Pengguna", labels=['Casual', 'Registered'])

for p in ax2.patches:
    if p.get_height() > 0:
        ax2.annotate(
            f"{p.get_height():.0f}",
            (p.get_x() + p.get_width() / 2., p.get_height()),
            ha='center', va='bottom',
            fontsize=11,
            xytext=(0, 5),
            textcoords='offset points'
        )

st.pyplot(fig2)

st.write("**Dominasi Pengguna Terdaftar:** Pengguna terdaftar (*registered*) mendominasi penyewaan di seluruh musim.")
st.write("**Musim Tertinggi:** Rata-rata penyewaan sepeda memuncak pada musim gugur (*Fall*) untuk kedua tipe pengguna.")

st.markdown("---")

st.subheader("Analisis Lanjutan: Rata-rata Penyewaan Berdasarkan Kategori Waktu Operasional")

cluster_time_result_sorted = cluster_time_result.sort_values(by='cnt', ascending=False)

fig3, ax3 = plt.subplots(figsize=(10, 6))
sns.barplot(
    data=cluster_time_result_sorted, 
    x='time_category', 
    y='cnt', 
    palette='viridis',
    ax=ax3
)

ax3.set_title('Rata-rata Penyewaan Sepeda Berdasarkan Kategori Waktu Operasional', fontsize=14, fontweight='bold')
ax3.set_xlabel('Kategori Waktu', fontsize=12)
ax3.set_ylabel('Rata-rata Penyewaan (cnt)', fontsize=12)
ax3.grid(axis='y', linestyle='--', alpha=0.6)

for index, row in enumerate(cluster_time_result_sorted['cnt']):
    ax3.text(index, row + 5, f'{row:.0f}', color='black', ha="center", fontsize=11)

st.pyplot(fig3)

st.write("**Analisis Waktu Operasional:** Pengelompokan waktu menunjukkan bahwa kategori *Rush Hour* mencatatkan rata-rata penyewaan tertinggi.")

st.caption('Copyright © Data Analytics Project 2026')
