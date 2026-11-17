# Checklist pengembangan ILAD Web

Targetnya adalah dashboard React dan TypeScript di Netlify, dengan Firebase Authentication, Cloud Functions Python, Firestore, dan Cloud Storage. Pilot mencakup login, unggah CSV EDOM sintetis, pemrosesan melalui controller ILAD, dan tampilan Overview. Streamlit menjadi pembanding selama migrasi.

Centang tugas setelah kriteria pada butir tersebut terpenuhi. Catat tautan PR, hasil CI, tangkapan layar, atau versi deployment pada PR terkait. Untuk evaluasi penelitian, catat versi aplikasi dan simpan bukti peserta di ruang penelitian dengan akses terbatas.

## 1. Baseline dan pemeriksaan pengembangan

- [x] Audit alur Streamlit dari unggah, validasi, praproses, analitik, hingga tampilan dan ekspor.
- [x] Catat versi notebook, rumus RPI, bobot, dan aturan peringkat di [baseline RPI](RPI_BASELINE.md).
- [x] Cocokkan skor dan peringkat RPI pada profil sintetis dengan nilai seri, dimensi yang berbeda, dan kohor satu dosen.
- [x] Tambahkan [panduan agen](../AGENTS.md) dan [workflow Python CI](../.github/workflows/python-ci.yml) pada branch `codex/ilad-rpi-ci` di GitHub. Suite lokal mencatat 44 tes lulus.
- [x] Buka [PR #1](https://github.com/syamsudintekno/ILAD/pull/1) ke `main`.
- [x] Verifikasi job `ILAD Python tests` lulus di [runner GitHub](https://github.com/syamsudintekno/ILAD/actions/runs/44007713627).
- [ ] Aktifkan job `ILAD Python tests` sebagai *required status check* pada `main`, lalu verifikasi statusnya di PR.
- [ ] Rekam versi Python serta dependensi analitik yang dipakai untuk perbandingan pilot. Pakai sumber paket dan versi yang sama untuk pengujian dan deployment pilot.
- [x] Tambahkan job Firebase Emulator ke workflow CI. Script lulus secara lokal.
- [ ] Verifikasi job `ILAD Firebase emulator tests` pada runner GitHub.
- [x] Tambahkan typecheck dan build frontend ke CI. Build lokal lulus.
- [ ] Verifikasi job `ILAD web build` pada runner GitHub dan tambahkan E2E browser.

## 2. Kontrak API dan akses data

- [x] Dokumentasikan kolom CSV, rentang P1–P20, validasi, agregasi, dan selisih praproses notebook di [kontrak pilot v1](WEB_API_CONTRACT.md).
- [x] Definisikan kontrak respons API berversi, metadata run, ukuran kohor, ringkasan validasi, dan bentuk Overview.
- [x] Dokumentasikan definisi `overall_score`, `rpi`, `rank`, dan `quartile`. Kontrak API v1 mengecualikan `percentile` karena controller belum menghasilkannya.
- [x] Definisikan status run dan respons HTTP untuk validasi, akses, hasil tertunda, serta kegagalan.
- [x] Tetapkan cakupan pilot untuk Admin QA pemilik run. Firestore menyimpan metadata dan Cloud Storage menyimpan hasil. CSV diproses tanpa disimpan.
- [ ] Tetapkan matriks izin per aksi dan cakupan data. Admin QA mengunggah dan memicu analitik. Kaprodi dibatasi ke prodi, Dekan ke fakultas, LPM ke cakupan institusi yang disetujui, dan Rektor ke ringkasan eksekutif. Verifikasi kebijakan ekspor secara terpisah.
- [ ] Tentukan sumber keanggotaan prodi dan fakultas untuk otorisasi. Kontrak unggah memuat fakultas, tetapi hasil lecturer-level saat ini perlu diperiksa sebelum dipakai untuk pembatasan cakupan. Uji dosen yang muncul pada lebih dari satu program.
- [ ] Tetapkan masa retensi hasil dan log serta prosedur penghapusan metadata dan objek hasil sebelum staging menerima unggahan pengguna.

## 3. Pilot autentikasi, unggah, dan Overview

- [x] Implementasikan tampilan login dan Overview di React dan TypeScript, termasuk status sesi dan pembatasan tampilan ke Admin QA.
- [x] Siapkan Firebase Emulator dengan proyek sintetis `demo-ilad` dan [panduan pengujian](FIREBASE_PILOT.md).
- [x] Buat proyek Firebase staging dengan Project ID `ilad-staging`.
- [x] Aktifkan metode login Email/Password di Firebase Authentication staging.
- [x] Daftarkan aplikasi web di proyek staging dan siapkan konfigurasi Firebase Web SDK untuk frontend.
- [ ] Konfigurasikan layanan staging dan pisahkan konfigurasi serta kredensial server dari lingkungan lain.
- [x] Implementasikan endpoint HTTPS Python untuk unggah dan pembacaan run. Verifikasi token, peran Admin QA, dan kepemilikan run di server. Origin diatur per lingkungan.
- [x] Buat adapter Python dari CSV ke payload Overview melalui `AnalyticsController.run_uploaded_csv`. Tes lokal mencakup KPI, peringkat seri, batas 10 baris, serialisasi JSON, CSV kosong, data invalid, dan encoding.
- [x] Hubungkan endpoint unggah ke adapter, batasi unggahan awal ke 2 MiB, dan gunakan respons validasi yang hanya membawa kolom kanonis serta hitungan.
- [x] Implementasikan penyimpanan status dan metadata di Firestore, hasil di Cloud Storage, dan rules yang menolak akses langsung dari klien.
- [x] Implementasikan tampilan kesalahan unggah dan rincian validasi di frontend.
- [x] Verifikasi dua unggahan bersamaan dan pengulangan sesudah berhasil menghasilkan satu run. Tolak penggunaan key yang sama untuk isi CSV berbeda.
- [ ] Uji pemulihan setelah koneksi terputus, lease kedaluwarsa, dan kegagalan parsial antar Firestore dan Storage.
- [x] Implementasikan KPI, distribusi kuartil, tabel dosen teratas, serta status unggahan di frontend.
- [x] Jalankan uji HTTP lokal untuk penolakan autentikasi dan peran, penerusan UID pemilik, validasi, ukuran unggahan, serta status retry dan konflik.
- [x] Verifikasi akses pengguna berwenang, penolakan run lintas akun, serta penolakan pembacaan langsung Firestore dan Storage dengan script smoke di Firebase Emulator.
- [ ] Uji alur sesi yang kedaluwarsa ketika frontend tersedia. Verifikasi penolakan token kedaluwarsa di staging.
- [ ] Jalankan E2E dengan CSV sintetis yang valid serta gagal validasi. Pilot diterima setelah pengguna berwenang dapat login, unggah, melihat hasil yang sesuai Streamlit, membukanya kembali setelah refresh, dan keluar dari sesi.

## 4. Migrasi halaman dan kesetaraan hasil

- [ ] Migrasikan Analitik Institusi. Cocokkan statistik deskriptif, distribusi RPI, dan jumlah dosen per kuartil.
- [ ] Migrasikan Distribusi. Cocokkan input histogram dan boxplot, tabel statistik, dan skala skor. Jelaskan bahwa perubahan distribusi merupakan hasil deskriptif pada kohor yang dianalisis.
- [ ] Migrasikan Profil Dosen. Cocokkan skor dimensi, RPI, peringkat, dan kuartil. Uji tautan langsung ke profil di luar cakupan pengguna.
- [ ] Migrasikan Laporan dan ekspor CSV/JSON. Cocokkan kolom dan isi dengan Streamlit untuk cakupan yang sama. Uji bahwa ekspor hanya berisi baris dan kolom yang diizinkan.
- [ ] Uji filter prodi dan fakultas tanpa menghitung ulang RPI, peringkat, atau kuartil kohor asal. Beri label cakupan KPI atau ringkasan yang memang dihitung untuk subset tampilan.
- [ ] Bandingkan notebook, controller, dan API pada skor dimensi sintetis yang sama. RPI sebelum pembulatan harus cocok dalam toleransi absolut `1e-10` dan peringkat harus identik.
- [ ] Bandingkan Streamlit dan web dengan CSV sintetis yang sama. Cakup baris invalid, nama ganda, nilai seri, nilai hampir konstan, batas kuartil, dan kohor kecil. Cocokkan validasi, kohor, skor, peringkat, kuartil, KPI, dan isi ekspor.
- [ ] Verifikasi penyajian nilai hilang atau tak hingga pada JSON dan UI. Uji navigasi keyboard, fokus, keterbacaan grafik, dan tata letak di desktop dan ponsel.

## 5. Staging, rilis, dan pemeliharaan

- [x] Tambahkan konfigurasi build Netlify dan fallback rute SPA.
- [ ] Verifikasi login, refresh, serta endpoint Firebase pada URL Netlify staging.
- [ ] Uji konfigurasi Firebase staging, termasuk rules yang terpasang, domain autentikasi, serta pemisahan akun dan data dari lingkungan lain.
- [ ] Pastikan build publik, log, artefak CI, dan demo hanya menggunakan data sintetis serta bebas dari kredensial server.
- [ ] Ukur waktu dan penggunaan sumber daya pada beberapa ukuran CSV sintetis. Tetapkan kriteria penerimaan untuk pemrosesan, respons Overview, dan pemulihan kegagalan berdasarkan kebutuhan pilot.
- [ ] Catat cara memantau kegagalan unggah dan pemrosesan tanpa merekam identitas dosen. Dokumentasikan cara memulihkan versi frontend serta backend yang kompatibel dan uji pemulihan di staging.
- [ ] Jalankan Streamlit dan web secara paralel pada skenario penerimaan. Catat selisih yang ditemukan dan selesaikan selisih metodologis serta celah akses sebelum perpindahan pengguna.
- [ ] Jika data EDOM asli akan digunakan, verifikasi otorisasi institusi, akses per peran, retensi, serta penghapusan pada deployment privat sebelum data dimuat.

## 6. Evaluasi ADDIE dan mixed methods

- [ ] **Analysis.** Catat kebutuhan dan tugas QA, Kaprodi, Dekan, LPM, serta Rektor. Pilih tugas yang dapat dilakukan pada kedua aplikasi untuk studi perbandingan.
- [ ] **Design.** Petakan kebutuhan ke tugas uji, indikator keberhasilan, sumber data, dan versi aplikasi. Definisikan sejak awal kapan waktu mulai dan berhenti, apa yang dianggap berhasil, dan kesalahan apa yang dicatat.
- [ ] **Development dan expert review.** Siapkan rubrik untuk ketepatan metode RPI, interpretasi grafik, alur kerja, dan akses data. Catat masukan, revisi, serta hasil pemeriksaan ulang per versi.
- [ ] **Implementation dan FGD.** Siapkan skenario, panduan moderator, dan prosedur persetujuan peserta sesuai protokol. Catat tema, perbedaan pendapat, serta keputusan revisi yang dapat ditelusuri ke data.
- [ ] **Evaluation dan SUS.** Berikan instrumen SUS setelah peserta menyelesaikan skenario tugas. Catat versi instrumen, aturan penskoran dan respons hilang, serta jumlah respons yang dianalisis.
- [ ] **Efektivitas operasional.** Bandingkan waktu penyelesaian, keberhasilan, dan kesalahan pada tugas yang sama di Streamlit dan web. Dokumentasikan peserta, urutan penggunaan platform, serta pengaruh latihan atau familiaritas yang perlu dipertimbangkan.
- [ ] **Integrasi hasil.** Kaitkan hasil SUS dan metrik tugas dengan tema FGD dan temuan expert review. Laporkan keterbatasan pengukuran dan dukung klaim evaluasi hanya dengan data yang benar-benar terkumpul.
