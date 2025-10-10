import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# --- PENGATURAN TEMA DAN PALET WARNA ---
sns.set_theme(style="whitegrid")
custom_palette = ["#FF6B6B", "#FFD166", "#06D6A0", "#118AB2", "#073B4C"]

# --- FUNGSI-FUNGSI UNTUK MEMPROSES DATA ---
def total_registered_df(day_df):
    """Menghitung total pengguna terdaftar per hari."""
    reg_df = day_df.groupby(by="dteday").agg({"registered": "sum"})
    reg_df = reg_df.reset_index()
    reg_df.rename(columns={"registered": "register_sum"}, inplace=True)
    return reg_df

def total_casual_df(day_df):
    """Menghitung total pengguna biasa per hari."""
    cas_df = day_df.groupby(by="dteday").agg({"casual": "sum"})
    cas_df = cas_df.reset_index()
    cas_df.rename(columns={"casual": "casual_sum"}, inplace=True)
    return cas_df

def macem_season(day_df):
    """Menghitung total penyewaan per musim."""
    season_df = day_df.groupby(by="season")["count_cr"].sum().reset_index()
    return season_df

# --- MEMBACA DAN MEMPERSIAPKAN DATA ---
days_df = pd.read_csv("dashboard/day_clean.csv")
hours_df = pd.read_csv("dashboard/hour_clean.csv")

# Mengonversi kolom tanggal ke tipe datetime
for col in ["dteday"]:
    days_df[col] = pd.to_datetime(days_df[col])
    hours_df[col] = pd.to_datetime(hours_df[col])

min_date_days = days_df["dteday"].min()
max_date_days = days_df["dteday"].max()

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://www.onepointltd.com/wp-content/uploads/2020/03/inno2.png")
    st.title("Kontrol & Informasi")
    st.markdown("---")
    st.header("🗓️ Filter Rentang Waktu")
    start_date, end_date = st.date_input(
        label='Pilih tanggal analisis',
        min_value=min_date_days,
        max_value=max_date_days,
        value=[min_date_days, max_date_days]
    )
    st.markdown("---")
    st.header("📖 Tentang Proyek")
    st.info(
        "Dasbor ini menganalisis data penyewaan sepeda dari Capital Bikeshare "
        "selama 2011-2012 untuk memahami pola penyewaan berdasarkan waktu dan musim."
    )
    st.markdown("---")
    st.caption("Made in Streamlit by andwynt")

# --- MEMFILTER DATA BERDASARKAN INPUT SIDEBAR ---
main_df_days = days_df[(days_df["dteday"] >= str(start_date)) &
                       (days_df["dteday"] <= str(end_date))]
main_df_hour = hours_df[(hours_df["dteday"] >= str(start_date)) &
                        (hours_df["dteday"] <= str(end_date))]

# --- MEMBANGUN HALAMAN UTAMA DASBOR ---
st.header('Bike Sharing Dashboard :bike:')

if main_df_days.empty:
    st.warning(f"⚠️ Tidak ada data pada rentang waktu yang dipilih. Silakan pilih rentang antara {min_date_days.strftime('%d-%m-%Y')} dan {max_date_days.strftime('%d-%m-%Y')}.")
else:
    reg_df = total_registered_df(main_df_days)
    cas_df = total_casual_df(main_df_days)
    season_df = macem_season(main_df_days)
    
    total_orders = main_df_days.count_cr.sum()
    total_registered = reg_df.register_sum.sum()
    total_casual = cas_df.casual_sum.sum()
    
    st.subheader('Ringkasan Data Penyewaan')
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Penyewaan", value=f"{total_orders:,}")
    with col2:
        st.metric("Pengguna Terdaftar", value=f"{total_registered:,}")
    with col3:
        st.metric("Pengguna Biasa", value=f"{total_casual:,}")

    st.markdown("---")

    st.subheader("📊 Perbandingan Tipe Pengguna")
    user_type_data = pd.DataFrame({
        'Tipe Pengguna': ['Terdaftar', 'Biasa'],
        'Jumlah': [total_registered, total_casual]
    }).sort_values(by='Jumlah', ascending=True)

    fig1, ax1 = plt.subplots(figsize=(10, 4))
    bars1 = ax1.barh(user_type_data['Tipe Pengguna'], user_type_data['Jumlah'], color=custom_palette[:2])
    ax1.set_xlabel('Jumlah Penyewaan')
    ax1.set_title('Total Penyewaan Berdasarkan Tipe Pengguna')
    ax1.spines[['top', 'right', 'left']].set_visible(False)
    for bar in bars1:
        width = bar.get_width()
        ax1.text(width + 3, bar.get_y() + bar.get_height()/2, f'{width:,.0f}', va='center')
    st.pyplot(fig1)

    st.markdown("---")

    st.subheader("⏰ Pola Penyewaan Berdasarkan Jam")
    fig2, ax2 = plt.subplots(figsize=(16, 8))
    hourly_rentals = main_df_hour.groupby('hours')['count_cr'].sum()
    bars2 = sns.barplot(x=hourly_rentals.index, y=hourly_rentals.values, palette=custom_palette, ax=ax2)
    ax2.set_title("Jumlah Total Penyewaan Sepeda per Jam", fontsize=16)
    ax2.set_xlabel("Jam dalam Sehari (0-23)")
    ax2.set_ylabel("Total Penyewaan")
    for bar in bars2.patches:
        ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f'{bar.get_height():,.0f}',
                 ha='center', va='bottom', size=10, color='gray')
    st.pyplot(fig2)

    st.markdown("---")

    # PERBAIKAN: Baris berlebihan di bawah ini dihapus
    # st.pyplot(fig) 
    
    # PERBAIKAN: Seluruh blok grafik musim ini dipindahkan ke dalam blok 'else'
   st.subheader("🍂 Pola Penyewaan Berdasarkan Musim")
fig3, ax3 = plt.subplots(figsize=(12, 7))

# PERBAIKAN: Mengurutkan berdasarkan 'season' (1, 2, 3, 4) bukan 'count_cr'
season_df_sorted = season_df.sort_values(by="season", ascending=True)

# Proses sisa kode tetap sama
season_labels = {1: 'Semi', 2: 'Panas', 3: 'Gugur', 4: 'Dingin'}
season_df_sorted['season_name'] = season_df_sorted['season'].map(season_labels)

# Menggunakan sns.barplot untuk membuat grafik vertikal seperti contoh
bars3 = sns.barplot(
    x="season_name", 
    y="count_cr", 
    data=season_df_sorted, 
    palette=custom_palette, 
    ax=ax3
)

ax3.set_title("Total Penyewaan Sepeda per Musim", fontsize=16)
ax3.set_xlabel("Musim")
ax3.set_ylabel("Total Penyewaan")

# Menyesuaikan loop untuk grafik vertikal
for bar in bars3.patches:
    ax3.text(
        bar.get_x() + bar.get_width() / 2, 
        bar.get_height(), 
        f'{int(bar.get_height()):,}', 
        ha='center', 
        va='bottom', 
        size=10, 
        color='gray'
    )

st.pyplot(fig3)
