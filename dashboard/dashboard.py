import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

sns.set(style='dark')

# --- FUNGSI-FUNGSI ---
# (Fungsi get_total_count_by_hour_df tidak digunakan, jadi bisa dihapus atau diabaikan)

def count_by_day_df(day_df):
    day_df_count = day_df.query(str('dteday >= "2011-01-01" and dteday <= "2012-12-31"'))
    return day_df_count

def total_registered_df(day_df):
    reg_df = day_df.groupby(by="dteday").agg({
      "registered": "sum" # Sudah Benar
    })
    reg_df = reg_df.reset_index()
    reg_df.rename(columns={
        "registered": "register_sum"
    }, inplace=True)
    return reg_df

def total_casual_df(day_df):
    cas_df = day_df.groupby(by="dteday").agg({
      "casual": "sum" # <<< INI YANG DIPERBAIKI
    })
    cas_df = cas_df.reset_index()
    cas_df.rename(columns={
        "casual": "casual_sum"
    }, inplace=True)
    return cas_df

def macem_season(day_df):
    season_df = day_df.groupby(by="season").count_cr.sum().reset_index()
    return season_df

# --- MEMBACA DAN MEMPERSIAPKAN DATA ---
days_df = pd.read_csv("dashboard/day_clean.csv")
hours_df = pd.read_csv("dashboard/hour_clean.csv")

datetime_columns = ["dteday"]
for column in datetime_columns:
    days_df[column] = pd.to_datetime(days_df[column])
    hours_df[column] = pd.to_datetime(hours_df[column])

min_date_days = days_df["dteday"].min()
max_date_days = days_df["dteday"].max()

# --- SIDEBAR ---
with st.sidebar:
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date_days,
        max_value=max_date_days,
        value=[min_date_days, max_date_days]
    )

main_df_days = days_df[(days_df["dteday"] >= str(start_date)) & 
                       (days_df["dteday"] <= str(end_date))]

main_df_hour = hours_df[(hours_df["dteday"] >= str(start_date)) & 
                        (hours_df["dteday"] <= str(end_date))]

# --- MEMPROSES DATA UNTUK VISUALISASI ---
day_df_count = count_by_day_df(main_df_days)
reg_df = total_registered_df(main_df_days)
cas_df = total_casual_df(main_df_days)
season_df = macem_season(main_df_hour)

# --- MEMBANGUN DASHBOARD ---
st.header('Bike Sharing :sparkles:')

st.subheader('Daily Sharing')
col1, col2, col3 = st.columns(3)

total_orders = day_df_count.count_cr.sum()
total_registered = reg_df.register_sum.sum()
total_casual = cas_df.casual_sum.sum()

with col1:
    st.metric("Total Sharing Bike", value=f"{total_orders:,}")

with col2:
    st.metric("Total Registered", value=f"{total_registered:,}")

with col3:
    st.metric("Total Casual", value=f"{total_casual:,}")

# --- VISUALISASI DAN PENJELASAN ---
st.markdown("---")

st.subheader("Perbandingan Pengguna Terdaftar (Registered) vs Biasa (Casual)")
fig1, ax1 = plt.subplots(figsize=(10, 6))
sizes = [total_casual, total_registered]
labels = 'Casual', 'Registered'
explode = (0, 0.1)
ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
        colors=["#D3D3D3", "#90CAF9"], shadow=True, startangle=90)
ax1.axis('equal')
st.pyplot(fig1)

st.markdown("""
**Analisis:**
- Mayoritas penyewa sepeda adalah **pengguna yang sudah terdaftar (Registered)**, mencapai lebih dari 80% dari total penyewaan.
- **Pengguna biasa (Casual)**, yaitu mereka yang menyewa tanpa akun terdaftar, merupakan minoritas yang signifikan (sekitar 18-19%).

**Rekomendasi Bisnis:**
- **Fokus pada Retensi**: Karena basis pengguna terbesar adalah pelanggan terdaftar, program loyalitas, diskon khusus anggota, atau fitur premium dapat meningkatkan retensi.
- **Strategi Konversi**: Perlu adanya strategi untuk mengubah pengguna *casual* menjadi *registered*. Contohnya, menawarkan diskon untuk penyewaan pertama setelah mendaftar.
""")

st.markdown("---")

st.subheader("Pola Penyewaan Sepeda Berdasarkan Jam dalam Sehari")
fig, ax = plt.subplots(figsize=(20, 8))
hourly_rentals = main_df_hour.groupby('hours')['count_cr'].sum()
peak_hour = hourly_rentals.idxmax()
colors = ["#90CAF9" if i == peak_hour else "#D3D3D3" for i in hourly_rentals.index]
sns.barplot(x=hourly_rentals.index, y=hourly_rentals.values, palette=colors, ax=ax)
ax.set_title("Jumlah Total Penyewaan Sepeda per Jam", fontsize=20)
ax.set_xlabel("Jam (0-23)", fontsize=15)
ax.set_ylabel("Total Penyewaan", fontsize=15)
ax.tick_params(axis='x', labelsize=12)
ax.tick_params(axis='y', labelsize=12)
st.pyplot(fig)

st.markdown("""
**Analisis:**
- Grafik menunjukkan **dua puncak utama (jam sibuk)** penyewaan dalam sehari. Biasanya terjadi pada pagi hari (sekitar jam 8 pagi) dan sore hari (sekitar jam 5-6 sore).
- Pola ini sangat identik dengan **jam berangkat dan pulang kerja/sekolah**, menunjukkan bahwa sepeda banyak digunakan untuk komuter.
- Jam dengan penyewaan **paling sedikit** terjadi pada dini hari, yaitu antara jam 1 hingga 4 pagi, di mana aktivitas masyarakat sangat rendah.

**Rekomendasi Operasional:**
- **Alokasi Sepeda**: Pastikan ketersediaan sepeda di stasiun-stasiun populer (terutama di area perumahan dan perkantoran) beberapa saat sebelum jam sibuk pagi dan sore.
- **Penawaran Promosi**: Untuk meningkatkan penggunaan di luar jam sibuk (misalnya, jam 10 pagi - 3 sore), perusahaan bisa menawarkan tarif diskon atau paket "sewa makan siang".
""")

st.markdown("---")

st.subheader("Pola Penyewaan Sepeda Berdasarkan Musim")
fig, ax = plt.subplots(figsize=(16, 8))
season_df_sorted = season_df.sort_values(by="count_cr", ascending=False)
season_labels = {1: 'Springer', 2: 'Summer', 3: 'Fall', 4: 'Winter'}
season_df_sorted['season_name'] = season_df_sorted['season'].map(season_labels)
peak_season = season_df_sorted.iloc[0]['season_name']
colors = ["#90CAF9" if s == peak_season else "#D3D3D3" for s in season_df_sorted['season_name']]
sns.barplot(
    x="season_name",
    y="count_cr",
    data=season_df_sorted,
    palette=colors,
    ax=ax
)
ax.set_title("Total Penyewaan Sepeda per Musim", loc="center", fontsize=20)
ax.set_ylabel("Total Penyewaan", fontsize=15)
ax.set_xlabel("Musim", fontsize=15)
ax.tick_params(axis='x', labelsize=12)
ax.tick_params(axis='y', labelsize=12)
st.pyplot(fig)

st.markdown("""
*(Catatan: 1: Musim Semi (Springer), 2: Musim Panas (Summer), 3: Musim Gugur (Fall), 4: Musim Dingin (Winter))*

**Analisis:**
- **Musim Gugur (Fall)** tercatat sebagai musim dengan jumlah penyewaan sepeda tertinggi, diikuti oleh Musim Panas (Summer) dan Musim Semi (Springer). Cuaca yang sejuk dan nyaman pada musim-musim ini sangat mendukung aktivitas bersepeda.
- **Musim Dingin (Winter)** memiliki jumlah penyewaan terendah. Hal ini wajar karena cuaca yang dingin, bersalju, atau hujan membuat orang enggan bersepeda.

**Rekomendasi Strategis:**
- **Perencanaan Inventaris**: Persiapkan jumlah sepeda dan petugas operasional yang lebih banyak menjelang musim puncak (Gugur dan Panas).
- **Program Musim Dingin**: Selama musim dingin, fokus dapat dialihkan ke perawatan dan perbaikan armada sepeda. Selain itu, promosi khusus "bersepeda di hari yang cerah saat musim dingin" bisa dicoba untuk menarik minat pengguna.
""")
