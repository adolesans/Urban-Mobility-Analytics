import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt

# --- PENGATURAN TAMPILAN DAN KONFIGURASI ---
st.set_page_config(
    page_title="Bike Sharing Performance",
    page_icon="🚲",
    layout="wide"
)

# --- FUNGSI CACHING UNTUK MEMPERCEPAT LOAD DATA ---
@st.cache_data
def load_data():
    """Memuat dan membersihkan data dari file CSV."""
    days_df = pd.read_csv("dashboard/day_clean.csv")
    hours_df = pd.read_csv("dashboard/hour_clean.csv")
    for col in ["dteday"]:
        days_df[col] = pd.to_datetime(days_df[col])
        hours_df[col] = pd.to_datetime(hours_df[col])
    return days_df, hours_df

# --- PENGATURAN TEMA DAN PALET WARNA ---
sns.set_theme(style="whitegrid")
custom_palette = ["#FF6B6B", "#FFD166", "#06D6A0", "#118AB2", "#073B4C"]

# --- MEMUAT DATA ---
days_df, hours_df = load_data()
min_date_days = days_df["dteday"].min()
max_date_days = days_df["dteday"].max()

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://i.imgur.com/pEtfl98.png")
    st.title("Panel Kontrol")
    st.markdown("---")
    st.header("📖 Tentang Dashboard")
    st.info(
        "Dashboard ini menyajikan analisis kinerja operasional penyewaan sepeda "
        "Bikeshare Company periode 2011-2012."
    )
    st.markdown("---")
    st.header("🗓️ Filter Rentang Waktu")
    start_date, end_date = st.date_input(
        label='Pilih rentang waktu',
        min_value=min_date_days,
        max_value=max_date_days,
        value=[min_date_days, max_date_days]
    )
    st.markdown("---")
    st.caption("© 2025 Bikeshare Company Dashboard")

# --- MEMFILTER DATA ---
main_df_days = days_df[(days_df["dteday"] >= str(start_date)) & (days_df["dteday"] <= str(end_date))]
main_df_hour = hours_df[(hours_df["dteday"] >= str(start_date)) & (hours_df["dteday"] <= str(end_date))]

# --- MEMBANGUN HALAMAN UTAMA DASBOR ---
st.markdown("<h1 style='text-align: center;'>Dashboard Kinerja Operasional</h1>", unsafe_allow_html=True)

if main_df_days.empty:
    st.warning(f"⚠️ Tidak ada data pada rentang waktu yang dipilih.")
else:
    # --- KPI METRICS ---
    total_orders = main_df_days.count_cr.sum()
    total_registered = main_df_days.registered.sum()
    total_casual = main_df_days.casual.sum()
    
    st.markdown("<h3 style='text-align: center;'>Indikator Kinerja Utama (KPI)</h3>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Penyewaan", value=f"{total_orders:,}")
    with col2:
        st.metric("Penyewa Terdaftar", value=f"{total_registered:,}")
    with col3:
        st.metric("Penyewa Biasa", value=f"{total_casual:,}")

    st.markdown("---")

    # --- GRAFIK & ANALISIS ---
    st.subheader("Segmentasi Pelanggan: Terdaftar vs. Biasa")
    user_type_data = pd.DataFrame({'Tipe Pengguna': ['Terdaftar', 'Biasa'], 'Jumlah': [total_registered, total_casual]}).sort_values(by='Jumlah', ascending=True)
    fig1, ax1 = plt.subplots(figsize=(10, 4))
    bars1 = ax1.barh(user_type_data['Tipe Pengguna'], user_type_data['Jumlah'], color=["#FF6B6B", "#FFD166"])
    ax1.set_xlabel('Jumlah Penyewaan'); ax1.set_title('Total Penyewaan Berdasarkan Tipe Pelanggan')
    ax1.spines[['top', 'right', 'left']].set_visible(False)
    for bar in bars1:
        width = bar.get_width()
        ax1.text(width + 3, bar.get_y() + bar.get_height()/2, f'{width:,.0f}', va='center')
    st.pyplot(fig1)
    with st.expander("Lihat Insight dan Rekomendasi 📈"):
        st.markdown("- **Insight Utama**: Mayoritas pendapatan berasal dari **segmen pengguna terdaftar**.\n- **Rekomendasi Bisnis**: Luncurkan kampanye untuk **mengonversi pengguna biasa** menjadi anggota.")

    st.markdown("---")

    st.subheader("Analisis Jam Sibuk Operasional (Interaktif)")
    hourly_rentals_df = main_df_hour.groupby('hours')['count_cr'].sum().reset_index()
    chart = alt.Chart(hourly_rentals_df).mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5, opacity=0.8, color="#118AB2").encode(x=alt.X("hours:O", title="Jam dalam Sehari"), y=alt.Y("count_cr:Q", title="Total Penyewaan"), tooltip=[alt.Tooltip("hours:O", title="Jam"), alt.Tooltip("count_cr:Q", title="Jumlah Penyewa", format=",")]).properties(title="Volume Penyewaan per Jam").configure_axis(labelFontSize=12, titleFontSize=14).configure_title(fontSize=16)
    st.altair_chart(chart, use_container_width=True)
    with st.expander("Lihat Insight dan Rekomendasi 📈"):
        st.markdown("- **Insight Utama**: Permintaan memuncak pada **jam komuter (08:00 & 17:00-18:00)**.\n- **Rekomendasi Bisnis**: Lakukan **realokasi armada** ke titik-titik strategis sebelum jam sibuk.")

    st.markdown("---")

    st.subheader("Analisis Performa Berdasarkan Musim")
    season_df = main_df_days.groupby(by="season")["count_cr"].sum().reset_index()
    season_labels = {1: 'Semi', 2: 'Panas', 3: 'Gugur', 4: 'Dingin'}
    season_df['season_name'] = season_df['season'].map(season_labels)
    fig3, ax3 = plt.subplots(figsize=(12, 7))
    sns.barplot(x="season_name", y="count_cr", data=season_df.sort_values(by="season", ascending=True), palette=custom_palette, ax=ax3)
    ax3.set_title("Perbandingan Kinerja Antar Musim", fontsize=16); ax3.set_xlabel("Musim"); ax3.set_ylabel("Total Penyewaan")
    for bar in ax3.patches:
        ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f'{int(bar.get_height()):,}', ha='center', va='bottom', size=10, color='gray')
    st.pyplot(fig3)
    with st.expander("Lihat Insight dan Rekomendasi 📈"):
        st.markdown("- **Insight Utama**: **Musim Gugur** adalah periode kinerja puncak.\n- **Rekomendasi Bisnis**: Jadwalkan **perawatan armada** pada Musim Semi (periode terendah).")
        
    # --- FITUR DOWNLOAD DATA ---
    st.markdown("---")
    st.subheader("Unduh Data yang Difilter")
    st.download_button(
        label="📥 Unduh sebagai CSV",
        data=main_df_days.to_csv(index=False).encode('utf-8'),
        file_name='filtered_data.csv',
        mime='text/csv'
    )
