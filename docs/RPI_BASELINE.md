# Baseline RPI untuk migrasi ILAD

Rujukan perhitungan adalah [RPI_pipeline_colab_REVISED2 new.ipynb](https://drive.google.com/file/d/1AD10VsxKpp863H72IZ7p8AAJC5k_j77G/view), versi Drive dengan waktu modifikasi `2026-07-15T07:36:54.754Z`. Penomoran sel di bawah dimulai dari 0.

Sel 1 memilih bobot sama untuk empat dimensi. Sel 22 menghitung peringkat menaik per dimensi dalam kohor yang sama. Nilai seri mendapat peringkat rata-rata. Posisi Blom adalah `p = (r - 0.375) / (N + 0.25)`, lalu `z = Φ⁻¹(p)`. Sel 24 memberi tiap dimensi bobot 0,25 dan menghitung `RPI = 50 + 10 × Σ(w × z)` langsung dari komposit. Peringkat RPI menurun dan memakai peringkat kompetisi, sehingga dua dosen yang seri di posisi pertama diikuti peringkat ketiga.

Uji migrasi memakai tabel skor dimensi sintetis yang sama pada notebook dan ILAD. Bandingkan RPI sebelum pembulatan dengan toleransi absolut `1e-10` serta peringkat dengan kecocokan eksak. Sertakan profil dimensi yang berbeda, nilai seri, dan kohor satu dosen. Filter tampilan harus memakai hasil dari kohor asal.

Notebook mengisi nilai butir yang hilang atau tidak valid dengan median dan memakai total dari data sumber sebagai pembanding mentah. ILAD memvalidasi CSV sebelum praproses dan menghitung `overall_score` dari rerata 20 butir. Kuartil ILAD memakai batas persentil RPI, sedangkan kuadran notebook memakai posisi pada dua sumbu. Untuk pilot, gunakan controller ILAD dan pertahankan definisi keluaran Streamlit. Kesetaraan dari CSV mentah hingga seluruh keluaran notebook memerlukan keputusan tersendiri tentang praproses, pembanding, dan klasifikasi.
