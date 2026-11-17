# Kontrak pilot ILAD Web v1

Kontrak ini menetapkan pertukaran data untuk login, unggah, dan Overview. [Baseline RPI](RPI_BASELINE.md) menjadi acuan skor dan peringkat. [Kontrak data Streamlit](DATA_CONTRACT.md) tetap menjadi rujukan alur aplikasi yang dimigrasikan.

## Input dan kohor

CSV memerlukan header `lecturer_name`, `study_program`, `faculty`, dan `P1` sampai `P20`. Validator saat ini memeriksa header sebelum normalisasi, menolak baris duplikat penuh, nilai kosong, dan nilai indikator yang gagal dibaca sebagai angka atau berada di luar rentang 1–5. Skor desimal dalam rentang tersebut dapat diterima. Pilot menolak file tanpa baris data.

Controller merata-ratakan butir dalam tiap dimensi dan seluruh 20 butir untuk `overall_score`, lalu menggabungkan baris berdasarkan `lecturer_name`. Jika satu nama memiliki beberapa baris, hasil menyimpan prodi dari baris pertama dan tidak membawa `faculty`. Seluruh dosen yang lolos dalam satu unggahan membentuk kohor RPI. Notebook lama memakai imputasi median dan total sumber sebagai pembanding mentah. Pilot mengikuti aturan CSV Streamlit.

## HTTP

| Permintaan | Kontrak |
| --- | --- |
| `POST /v1/runs` | Badan CSV UTF-8 dengan `Content-Type: text/csv`, token Firebase pada `Authorization: Bearer …`, dan `Idempotency-Key` untuk percobaan ulang unggahan yang sama. Respons 201 untuk run baru yang berhasil, 200 untuk hasil berhasil yang sudah tersimpan, dan 202 bila proses masih berjalan. |
| `GET /v1/runs/{run_id}` | Token Firebase wajib. Respons 200 berisi metadata run dan ringkasan sesuai izin jika tersedia. Server memakai identitas token terverifikasi saat memilih run. |

Respons run memuat `schema_version` bernilai `1`, `run_id`, `created_at` dalam UTC, `analytics_version` yang merujuk pada versi mesin analitik, dan `status` dengan nilai `processing`, `succeeded`, `invalid`, atau `failed`. Pada status `succeeded`, `cohort_size` menyatakan jumlah dosen dan `overview` memuat KPI institusi serta daftar dosen teratas. Pada status `invalid`, `validation` memuat jenis masalah dan jumlah temuan. Pada status lain sebelum hasil tersedia, `overview` dan `cohort_size` bernilai `null`.

| Status HTTP | Kondisi |
| --- | --- |
| 400 | Permintaan tidak lengkap, termasuk key unggah yang hilang atau tidak valid. |
| 401 | Token hilang, kedaluwarsa, atau gagal diverifikasi. |
| 403 | Akun terautentikasi tanpa peran pilot. |
| 404 | Run tidak tersedia bagi akun peminta, termasuk run milik akun lain. |
| 409 | Pemilik memakai ulang idempotency key untuk isi CSV berbeda. |
| 413 / 415 | Unggahan melebihi batas konfigurasi / tipe konten tidak didukung. |
| 422 | CSV kosong, gagal dibaca, atau gagal validasi. |
| 500 | Pemrosesan gagal. Pesan untuk pengguna tidak memuat detail internal. |

Kesalahan HTTP memuat `error.code` dan `error.message`. Untuk kegagalan validasi, respons juga membawa rincian dari daftar kolom kanonis dan hitungan. Data CSV, nama dosen, dan pesan pengecualian mentah tidak masuk log atau respons kesalahan. Nilai numerik yang tidak tersedia diserialisasi sebagai `null`.

## Overview dan definisi keluaran

- `overview.kpis` mengikuti keluaran controller untuk jumlah dosen, jumlah prodi, RPI rerata/tertinggi/terendah, dan jumlah per kuartil.
- `overview.top_lecturers` mengikuti urutan hasil controller dan batas baris Overview Streamlit. Setiap entri memuat nama dosen sintetis, prodi, `overall_score`, `rpi`, `rank`, dan `quartile`.
- `overall_score` adalah rerata 20 butir. `rpi` adalah skor relatif pada kohor unggahan. `rank` adalah peringkat kompetisi menurut RPI menurun. `quartile` adalah kelompok batas persentil RPI dengan Q1 sebagai kelompok tertinggi. `percentile` tidak termasuk respons v1 karena controller saat ini menghasilkan `rank`.

## Otorisasi dan penyimpanan

Run baru yang berhasil juga memuat `institutional_analytics` dengan enam statistik deskriptif per dimensi dan skor EDOM keseluruhan, serta histogram RPI agregat dalam 10 interval berlebar sama. Interval terakhir mencakup skor maksimum. Run lama tetap dapat dibuka di Overview dan perlu diproses ulang untuk menampilkan Analitik Institusi.

Run baru memuat `distribution.edom` dan `distribution.rpi` dengan histogram, ringkasan boxplot, dan delapan statistik dari controller. Boxplot web memakai interpolasi kuartil linear NumPy dan batas pencilan 1,5 kali rentang antarkuartil. Kedua grafik memakai skala skor masing-masing. Run yang dibuat sebelum fitur ini perlu diproses ulang untuk menampilkan halaman Distribusi.

`lecturer_profiles` memuat identitas, prodi, RPI, peringkat, kuartil, dan empat skor dimensi setiap dosen pada kohor. Data profil mengikuti otorisasi run yang sama dengan Overview. Run sebelum migrasi Profil Dosen perlu diproses ulang untuk menghasilkan data ini.

Pilot memakai akun Admin QA yang ditetapkan di server. Akun tersebut dapat mengunggah dan membaca run miliknya. Fitur ekspor dan akses Kaprodi, Dekan, LPM, serta Rektor masuk setelah pilot. Sebelum peran berbasis cakupan diaktifkan, gunakan sumber keanggotaan prodi dan fakultas yang diverifikasi institusi. Tetapkan cara menangani dosen lintas prodi tanpa mengubah kohor RPI.

API menjadi jalur akses ke metadata Firestore dan objek hasil Cloud Storage. Akses langsung dari frontend ditutup. Firestore menyimpan pemilik, status, waktu, versi analitik, rujukan hasil, dan informasi minimum untuk mendeteksi unggahan berulang. Storage menyimpan hasil pilot. Baca objek melalui API setelah pemeriksaan izin. Berkas CSV diproses dalam permintaan dan tidak disimpan. Tetapkan retensi dan uji penghapusan metadata serta hasil sebelum staging menerima unggahan pengguna.

Artefak hasil ditulis sebelum status `succeeded` dipublikasikan. Cakupan idempotensi adalah satu pemilik. Implementasi perlu menguji unggahan bersamaan, retry setelah koneksi terputus, dan pemulihan bila penulisan hasil berhasil tetapi pembaruan metadata gagal.
