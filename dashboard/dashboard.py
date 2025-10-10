import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import altair as alt 

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
    st.image("https://img.icons8.com/?size=100&id=9pAKclTpHTMC&format=png&color=ef8a1b")
    st.title("Informasi")
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
        "Dasbor ini menganalisis data penyewaan sepeda dari Bikeshare Company "
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

    with st.expander("Lihat Analisis Tipe Pengguna 💡"):
        st.markdown(
            """
            Grafik di atas menunjukkan perbandingan jumlah penyewaan antara pengguna yang sudah **terdaftar (registered)** dengan pengguna **biasa (casual)**.
            
            - **Insight**: Mayoritas penyewaan (lebih dari 80%) dilakukan oleh pengguna terdaftar. Ini menandakan adanya basis pelanggan yang kuat dan loyal.
            - **Rekomendasi**: 
                1.  Fokus pada program retensi untuk menjaga loyalitas pengguna terdaftar.
                2.  Buat strategi untuk mengubah pengguna biasa menjadi pengguna terdaftar, misalnya dengan menawarkan diskon pada pendaftaran pertama.
            """
        )

    st.markdown("---")

    # --- PERUBAHAN: Grafik Jam menjadi Interaktif dengan Altair ---
    st.subheader("⏰ Pola Penyewaan Berdasarkan Jam")
    
    hourly_rentals_df = main_df_hour.groupby('hours')['count_cr'].sum().reset_index()
    
    chart = (
        alt.Chart(hourly_rentals_df)
        .mark_bar(
            cornerRadiusTopLeft=5,
            cornerRadiusTopRight=5,
            opacity=0.8,
            color="#118AB2"
        )
        .encode(
            x=alt.X("hours:O", title="Jam dalam Sehari"),
            y=alt.Y("count_cr:Q", title="Total Penyewaan"),
            tooltip=[
                alt.Tooltip("hours:O", title="Jam"),
                alt.Tooltip("count_cr:Q", title="Jumlah Penyewa", format=","),
            ],
        )
        .properties(
            title="Pola Penyewaan Sepeda Sepanjang Hari",
        )
        .configure_axis(labelFontSize=12, titleFontSize=14)
        .configure_title(fontSize=16)
    )
    st.altair_chart(chart, use_container_width=True)

    with st.expander("Lihat Analisis Pola Per Jam 💡"):
        st.markdown(
            """
            Arahkan kursor pada batang untuk melihat jumlah penyewa di setiap jam. 
            Pola komuter sangat jelas terlihat dengan adanya puncak penyewaan di pagi (sekitar jam 8) dan sore hari (sekitar jam 17-18).
            """
        )

    st.markdown("---")
    
    st.subheader("Musim apa yang paling banyak disewa?")

    colors = ["#D3D3D3", "#D3D3D3", "#D3D3D3", "#90CAF9"]
    fig3, ax3 = plt.subplots(figsize=(20, 10))
    sns.barplot(
        y="count_cr", 
        x="season",
        data=season_df.sort_values(by="season", ascending=False),
        palette=colors,
        ax=ax3
        )
    ax3.set_title("Grafik Antar Musim", loc="center", fontsize=50)
    ax3.set_ylabel(None)
    ax3.set_xlabel(None)
    ax3.tick_params(axis='x', labelsize=35)
    ax3.tick_params(axis='y', labelsize=30)
    st.pyplot(fig3)

    with st.expander("Lihat Analisis Pola Musim 💡"):
        st.markdown(
            """
            Grafik ini membandingkan total penyewaan di empat musim yang berbeda.
            
            - **Insight**: Penyewaan sepeda sangat dipengaruhi oleh cuaca. Musim dengan cuaca paling nyaman (Gugur/Fall) memiliki jumlah penyewaan tertinggi.
            - **Rekomendasi**: 
                1.  Alokasikan lebih banyak sepeda untuk menghadapi musim puncak.
                2.  Manfaatkan musim sepi untuk melakukan perawatan pada armada sepeda.
            """
        )






