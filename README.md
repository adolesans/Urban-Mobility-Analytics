# Dashboard Analisis Kinerja Bike Sharing

## Deskripsi Singkat
Dasbor interaktif ini dibuat dengan **Streamlit** untuk menganalisis data penyewaan sepeda dari BikeShare Company (2011–2012). Tujuannya adalah menemukan pola penyewaan, segmentasi pelanggan, dan faktor musiman.

## Demo
- **GitHub:** [https://github.com/adolesans/bike-sharing-dashboard](https://github.com/adolesans/bike-sharing-dashboard)
- **Streamlit:** [https://bike-sharing-dashboard-andwynt.streamlit.app/](https://bike-sharing-dashboard-andwynt.streamlit.app/)

## Fitur Utama
- Menampilkan **KPI utama** (total sewa, pengguna member, casual)
- **Filter tanggal dinamis**
- **Grafik interaktif** (Altair)
- **Analisis musiman dan pelanggan**
- **Unduh data CSV**

## Pertanyaan Bisnis
1. Kapan periode waktu (jam) dengan frekuensi penyewaan sepeda tertinggi dan terendah?
2. Musim apa yang menunjukkan volume penyewaan sepeda tertinggi, dan bagaimana faktor musiman memengaruhi permintaan?
3. Berapa rasio antara penyewa terdaftar dan penyewa kasual?

## Tools
Python · Streamlit · Pandas · Matplotlib · Seaborn · Altair

## Cara Menjalankan
```bash
git clone https://github.com/adolesans/bike-sharing-dashboard.git
cd bike-sharing-dashboard
pip install -r requirements.txt
streamlit run dashboard.py
```

## Struktur Proyek
```
├── dashboard.py
├── dashboard/
│   ├── day_clean.csv
│   └── hour_clean.csv
├── requirements.txt
└── README.md
```

## Lisensi
Dibuat oleh andwynt(Annisa Dewiyanti)
