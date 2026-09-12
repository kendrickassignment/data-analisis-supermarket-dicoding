# Analisis Bisnis Supermarket Indonesia

Proyek ini merupakan analisis data transaksi sebuah supermarket di Indonesia periode 2014–2017, mencakup proses pembersihan data, analisis deskriptif, visualisasi data, hingga analisis prediktif untuk memperkirakan keuntungan dari hasil penjualan toko.

## Daftar Isi
- [Dataset](#dataset)
- [1. Pembersihan & Analisis Data (Google Sheets + SQL)](#1-pembersihan--analisis-data-google-sheets--sql)
- [2. Visualisasi Data (Looker Studio)](#2-visualisasi-data-looker-studio)
- [3. Supermarket BI by Kendrick Filbert (Plotly Dash)](#3-supermarket-bi-by-kendrick-filbert-plotly-dash)
- [4. Analisis Prediktif (Orange Data Mining)](#4-analisis-prediktif-orange-data-mining)
- [Menjalankan Dashboard](#menjalankan-dashboard)
- [Teknologi yang Digunakan](#teknologi-yang-digunakan)
- [Berkas Proyek](#berkas-proyek)
- [Kontributor](#kontributor)

---

## Dataset

Dataset berisi 10.493 record transaksi mentah yang mencakup detail pemesanan, pengiriman, profil pelanggan, produk, hingga keuntungan. Setelah proses pembersihan (417 baris duplikat ditemukan dan dihapus melalui fitur *Data cleanup > Remove duplicates* di Google Sheets), dataset final berisi **10.076 record transaksi bersih** yang digunakan untuk seluruh tahap analisis berikutnya.

Anomali yang ditangani selama pembersihan:
- **Duplikasi data** — baris yang identik di seluruh kolom di-drop.
- **`tanggal_pengiriman`** — nilai kosong diisi dengan nilai `tanggal_pemesanan` pada kolom baru `clean_tanggal_pengiriman`.
- **`kota`** — inkonsistensi format penulisan (huruf besar/kecil) dan nilai kosong dirapikan pada kolom baru `clean_kota`, menggunakan referensi provinsi → kota untuk mengisi nilai yang kosong.
- **`kode_pos`** — nilai kosong diisi menggunakan referensi provinsi → kode pos pada kolom baru `clean_kode_pos`.

## 1. Pembersihan & Analisis Data (Google Sheets + SQL)

Pembersihan dan analisis data dilakukan di Google Sheets menggunakan kombinasi rumus spreadsheet (`IF`, `INDEX`, `MATCH`, `PROPER`, `TRIM`) dan query mirip SQL melalui fungsi `=QUERY()`.

**Insight kunci:**
- Total penjualan sepanjang 2016: **±Rp9,28 miliar**, dengan total kuantitas terjual **9.995 unit**.
- Jumlah pesanan dengan metode pengiriman *First Class* periode 2014–2017: **1.553 pesanan**.
- Lima produk dengan penjualan tertinggi: Mesin Fotokopi 5577, Ordner Arsip A4 9062, Mesin Laminating 5722, Kursi Kantor 8559, dan Binder Kancing A4 9759.
- Kota dengan jumlah pelanggan terbanyak: **Makassar**, diikuti Surabaya dan Denpasar.
- Kota dengan rata-rata penjualan tertinggi: **Balikpapan** (±Rp4,09 juta per transaksi).
- Hari dengan jumlah transaksi terbanyak: **Senin**.
- Tabel pivot total penjualan per produk per kota tersedia sebagai subsheet terpisah untuk analisis lebih lanjut.

## 2. Visualisasi Data (Looker Studio)

Dua dashboard interaktif dibangun di Looker Studio untuk menyajikan insight secara visual:

### Dashboard 1 — Ringkasan Tren & Proporsi Penjualan (2014–2017)
- **Tren penjualan bulanan**: berfluktuasi sepanjang periode namun cenderung meningkat di akhir periode, puncaknya menjelang akhir 2017 (±Rp1,8 miliar/bulan).
- **Proporsi pesanan per wilayah**: Central memiliki proporsi terbesar (38,4%), West terendah (19,2%).
- **Proporsi penjualan per kategori produk**: Technology memberikan kontribusi terbesar (36,3%), diikuti Furniture (32,3%) dan Office Supplies (31,4%).

### Dashboard 2 — Perbandingan Kota, Metode Pengiriman & Bulan
- **Total penjualan per kota**: Balikpapan tertinggi (Rp4,09 M), Bandung terendah (Rp2,79 M).
- **Metode pengiriman paling sering digunakan**: Standard Class (6.043 transaksi), jauh di atas Second Class, First Class, dan Same Day.
- **Bulan dengan penjualan tertinggi**: November (Rp5,3 M), diikuti Desember (Rp4,9 M) dan September (Rp4,7 M). Februari mencatat penjualan terendah (±Rp900,7 juta) — mengindikasikan pola musiman menjelang akhir tahun (kemungkinan didorong oleh momen akhir tahun/promo).

File dashboard: `informasi_penjualan_super_market_indonesia.pdf`

## 3. Supermarket BI by Kendrick Filbert (Plotly Dash)

Sebagai pengembangan lanjutan dari dashboard Looker Studio, dibangun juga dashboard *business intelligence* interaktif berbasis **Python, Plotly, dan Dash** bernama **Supermarket BI by Kendrick Filbert**. Dashboard ini menggunakan dataset bersih yang sama (10.076 record transaksi) dan menawarkan eksplorasi data yang jauh lebih dalam dibanding enam visualisasi dasar di Looker Studio — mencakup analisis profitabilitas, portofolio produk, segmentasi pelanggan, hingga efisiensi operasional pengiriman.

**Identitas aplikasi:**
- Nama aplikasi: *Supermarket BI by Kendrick Filbert*
- Framework: Plotly Dash (v4.4.1) + Dash Bootstrap Components
- Periode data: 2014–2017
- Footer: *Made by Kendrick Filbert*

Dashboard terbagi menjadi 4 halaman:

**Executive Overview** — KPI utama (total penjualan, total keuntungan, margin keuntungan, jumlah pesanan unik, jumlah pelanggan unik, AOV, jumlah transaksi merugi, rata-rata durasi pengiriman), tren penjualan & keuntungan bulanan, kontribusi kategori produk, kinerja kota (warna batang = margin), serta *seasonality heatmap* tahun × bulan.

**Profitability** — scatter plot penjualan vs keuntungan (ukuran = kuantitas, warna = kategori), profit bridge per subkategori (hijau = untung, merah = rugi), dampak diskon terhadap margin, dan tabel transaksi dengan kerugian terbesar.

**Product Intelligence** — top 15 produk berdasarkan penjualan (dengan indikator margin), matriks portofolio produk 4 kuadran (*Star, Volume Driver, Hidden Gem, Underperformer*), Pareto chart kontribusi produk, dan treemap hierarki kategori → subkategori → nilai penjualan.

**Customer & Operations** — nilai pelanggan per segmen (Consumer, Corporate, Home Office), preferensi metode pengiriman, kecepatan pengiriman per metode (dihitung dari `clean_tanggal_pengiriman - tanggal_pemesanan`), dan daftar top pelanggan berdasarkan total penjualan.

**Fitur pendukung:**
- Filter interaktif: rentang tahun, wilayah, kota (menyesuaikan wilayah terpilih), kategori produk, segmen pelanggan, dengan tombol *Reset filter*.
- Tombol *Unduh data terfilter* → mengunduh `supermarket_filtered.csv`.
- Format nilai dalam Rupiah, tampilan responsif, serta *empty-state handling* saat filter tidak menghasilkan data.

File aplikasi: `app.py` (menggunakan `sources.csv` sebagai sumber data, harus berada di folder yang sama).

## 4. Analisis Prediktif (Orange Data Mining)

**Pertanyaan yang dijawab:** *"Berapa perkiraan keuntungan yang didapatkan dari hasil penjualan toko?"*

Workflow ini dibuat untuk memperkirakan keuntungan yang diperoleh dari transaksi penjualan supermarket. Dataset yang digunakan merupakan dataset hasil pembersihan dengan jumlah 10.076 record transaksi.

Variabel `keuntungan` digunakan sebagai target numerik. Fitur yang digunakan dalam pemodelan meliputi `penjualan`, `kuantitas`, `diskon`, `kategori`, `segmen`, `metode_pengiriman`, `clean_kota`, dan `wilayah`. Penggunaan `kategori`, `segmen`, `metode_pengiriman`, `clean_kota`, dan `wilayah` memastikan bahwa proses pemodelan melibatkan lebih dari dua fitur kategorikal.

Tahap preprocessing menggunakan **Impute** untuk menangani nilai kosong dengan metode Average/Most Frequent. **Continuize** digunakan untuk mengubah variabel kategorikal menjadi representasi numerik menggunakan one-hot encoding.

Dua algoritma regresi yang dibandingkan adalah **Random Forest** dan **Linear Regression**. Evaluasi model dilakukan menggunakan Random Sampling dengan 70% data training, 30% data testing, dan pengulangan sebanyak lima kali.

**Hasil Test and Score:**

| Model | R² | RMSE | MAE | sMAPE |
|---|---|---|---|---|
| Random Forest | 0,415 | Rp2.332.487,257 | Rp415.848,321 | 49,987 |
| Linear Regression | 0,132 | Rp2.841.074,364 | Rp839.525,765 | 117,5 |

Random Forest dipilih sebagai model terbaik karena menghasilkan R² yang lebih tinggi serta RMSE, MAE, dan sMAPE yang lebih rendah dibandingkan Linear Regression. Nilai R² sebesar 0,415 menunjukkan bahwa Random Forest mampu menjelaskan sekitar 41,5% variasi keuntungan pada proses evaluasi Random Sampling.

**Hasil Predictions:**

| Model | R² | RMSE | MAE | sMAPE |
|---|---|---|---|---|
| Random Forest | 0,883 | Rp1.196.304,005 | Rp202.713,204 | 28,728 |
| Linear Regression | 0,310 | Rp2.910.052,015 | Rp817.866,933 | 113,818 |

Widget Predictions berhasil menghasilkan estimasi keuntungan menggunakan kedua model. Hasil Predictions kembali menunjukkan bahwa estimasi Random Forest lebih mendekati keuntungan aktual. Namun, pemilihan model utama tetap didasarkan pada hasil Test and Score karena model dievaluasi menggunakan Random Sampling pada data testing.

Nilai MAPE pada kedua model menghasilkan `inf` karena terdapat keuntungan aktual bernilai nol, sehingga perhitungan persentase error melibatkan pembagian dengan nol. Oleh karena itu, pemilihan model difokuskan pada R², RMSE, MAE, dan sMAPE.

**Kesimpulan:** Random Forest merupakan model yang lebih sesuai untuk memperkirakan keuntungan transaksi supermarket dibandingkan Linear Regression. Meskipun demikian, hasil prediksi tetap perlu digunakan dengan mempertimbangkan nilai error dan faktor lain yang belum tercakup dalam model.

File workflow: `analisis-prediktif-supermarket.ows`

## Menjalankan Dashboard

**Persyaratan:** Python 3.10 atau lebih baru.

1. Pastikan `sources.csv` berada di folder yang sama dengan `app.py`.
2. Buat virtual environment (opsional tapi disarankan):
   ```bash
   python -m venv .venv
   .venv\Scripts\activate      # Windows
   source .venv/bin/activate   # macOS/Linux
   ```
3. Pasang dependencies dan jalankan:
   ```bash
   pip install -r requirements.txt
   python app.py
   ```
4. Buka `http://127.0.0.1:8050` di browser.

Pengguna Windows juga bisa langsung klik dua kali **`run_dashboard.bat`** — launcher ini otomatis membuat virtual environment, memasang dependencies, dan menjalankan dashboard.

## Teknologi yang Digunakan

| Tahap | Tools |
|---|---|
| Data cleaning & descriptive analytics | Google Sheets, Spreadsheet formulas, Google Visualization API Query Language, Pivot Table |
| Business intelligence | Looker Studio, Plotly, Dash, Dash Bootstrap Components |
| Data processing | Python, Pandas, NumPy |
| Predictive analytics | Orange Data Mining, Random Forest Regression, Linear Regression, One-hot Encoding, Random Sampling |

## Berkas Proyek

| Berkas | Deskripsi |
|---|---|
| `synthetic_store_indonesia.xlsx` | Data mentah, proses pembersihan, dan hasil analisis deskriptif/SQL |
| `informasi_penjualan_super_market_indonesia.pdf` | Dashboard visualisasi data (Looker Studio) |
| `app.py` | Aplikasi Supermarket BI by Kendrick Filbert berbasis Plotly Dash |
| `sources.csv` | Dataset bersih (10.076 record transaksi) yang dipakai oleh `app.py` dan workflow Orange |
| `requirements.txt` | Daftar dependencies Python untuk menjalankan dashboard |
| `run_dashboard.bat` | Launcher dashboard untuk Windows |
| `README_DASHBOARD.md` | Dokumentasi khusus cara menjalankan dashboard Plotly Dash |
| `analisis-prediktif-supermarket.ows` | Workflow analisis prediktif keuntungan (Orange Data Mining) |
| `url.txt` | Tautan menuju Google Sheets dan Looker Studio |
| `README.md` | Dokumentasi lengkap proyek ini |

## Kontributor

**Kendrick Filbert** — pengembang *Supermarket BI by Kendrick Filbert*, sekaligus penyusun keseluruhan analisis: data cleaning, spreadsheet analysis, SQL-like query, business intelligence, interactive dashboard development, predictive modeling, hingga komunikasi insight bisnis.

> *Catatan penggunaan data:* seluruh identitas pelanggan dan data transaksi dalam dataset digunakan hanya untuk pembelajaran, submission, eksperimen analisis data, demonstrasi dashboard, dan portofolio. Hasil analisis tidak seharusnya digunakan sebagai dasar keputusan bisnis nyata tanpa validasi data dan pemeriksaan tambahan lebih lanjut.
