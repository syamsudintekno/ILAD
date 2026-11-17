# Panduan pengembangan ILAD

- Baca [panduan pengembang](docs/AI_DEVELOPER_GUIDE.md), [konteks proyek](docs/PROJECT_CONTEXT.md), dan [arsitektur](docs/ARCHITECTURE.md) sebelum mengubah aplikasi. Untuk pekerjaan migrasi web, ikuti ruang lingkup migrasi yang disetujui pengguna.
- Jalankan analitik melalui `application.controller.AnalyticsController`. Antarmuka web dan API memakai hasil dari kohor yang sama. Filter tampilan menyaring hasil tersebut tanpa menghitung ulang skor atau peringkat.
- Pertahankan [baseline RPI](docs/RPI_BASELINE.md) dan nilai acuan sintetis di `tests/test_rpi.py`. Perubahan metode, pembentukan kohor, atau interpretasi keluaran perlu keputusan eksplisit dan harus tercermin dalam kontrak data serta pengujian.
- Gunakan data sintetis untuk tes, demo, dan deployment publik. Jaga data EDOM asli, identitas dosen, hasil per dosen, dan kredensial di luar Git, log CI, serta aset frontend publik.
- Saat menambahkan autentikasi atau penyimpanan Firebase, periksa otorisasi per run di backend dan aturan untuk akses langsung ke penyimpanan. Uji akses yang sah, akses tanpa login, dan penolakan akses ke run pengguna lain dengan Firebase Emulator.
- Jalankan `python -m pytest -q` sebelum menyerahkan perubahan. Untuk perubahan API atau antarmuka, verifikasi juga alur yang diubah. Laporkan pemeriksaan yang masih tertunda. Klaim hasil expert review, FGD, SUS, atau efektivitas operasional harus didukung data evaluasi nyata.
