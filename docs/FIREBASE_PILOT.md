# Menjalankan backend pilot ILAD

Gunakan Python 3.13 untuk menyamai runtime Firebase, Firebase CLI, dan JDK 21 untuk emulator. Perintah di bawah memakai PowerShell dari root repositori. Ganti `python` dengan executable Python 3.13 jika instalasi lokal memakai versi lain.

```powershell
python firebase/stage_functions.py
python -m venv .ilad-functions/venv
.\.ilad-functions\venv\Scripts\python.exe -m pip install -r firebase/requirements.txt
$env:ILAD_STORAGE_BUCKET = 'demo-ilad.appspot.com'
$env:ILAD_ANALYTICS_VERSION = 'emulator-baseline'
$env:ILAD_ALLOWED_ORIGINS = 'http://localhost:5173'
firebase emulators:exec --project demo-ilad --only auth,firestore,storage,functions '.\.ilad-functions\venv\Scripts\python.exe firebase/emulator_smoke.py'
```

Di Linux, gunakan `.ilad-functions/venv/bin/python` dan sintaks lingkungan shell setempat. Uji smoke memakai akun sintetis dan alamat loopback. Uji HTTP lokal dapat dijalankan dengan `python -m pytest -q` setelah memasang dependensi root dan `firebase/requirements.txt`.

Script staging menyalin kode analitik dan backend ke `.ilad-functions/`. Gunakan direktori staging yang bersih untuk deployment. Sebelum staging eksternal, isi `ILAD_STORAGE_BUCKET`, `ILAD_ANALYTICS_VERSION` dengan commit atau versi analitik, serta `ILAD_ALLOWED_ORIGINS` dengan origin frontend Netlify yang diizinkan. Backend menerima Firebase ID token dengan custom claim `ilad_role=admin_qa`. Klaim diberikan melalui Firebase Admin SDK oleh pengelola akun yang berwenang. Identitas pengguna diambil dari token, dan URL run hanya dapat dibaca pemiliknya.

Gunakan proyek dan bucket terpisah untuk staging. Rules untuk Firestore dan Cloud Storage menolak akses langsung dari klien dan ditujukan untuk proyek khusus ILAD. Tetapkan retensi sebelum menerima unggahan pengguna. Batas awal unggahan adalah 2 MiB agar pengujian sumber daya punya titik awal. Data CSV diproses di memori dan hasil pilot disimpan secara privat. [Kontrak pilot](WEB_API_CONTRACT.md)

## Frontend React

Jalankan emulator dengan `firebase emulators:start --project demo-ilad --only auth,firestore,storage,functions` dan variabel backend di atas. Siapkan akun uji sintetis dengan custom claim `ilad_role=admin_qa` melalui Admin SDK emulator. Di terminal lain, dari folder `web/`, jalankan `npm ci` lalu `npm run dev -- --mode emulator`. Gunakan alamat `http://localhost:5173` agar origin cocok dengan konfigurasi backend demo.

Untuk E2E otomatis, sertakan `http://127.0.0.1:5173` pada `ILAD_ALLOWED_ORIGINS`. Siapkan akun sintetis dengan `python firebase/browser_seed.py` setelah `FIREBASE_AUTH_EMULATOR_HOST` menunjuk ke `127.0.0.1:9099`. Dari `web/`, jalankan `npm ci`, `npx playwright install chromium`, lalu `npm run test:e2e`. Playwright membuka server Vite sendiri di port 5173. Job integrasi Firebase di GitHub menjalankan rangkaian ini dengan proyek demo yang baru setiap kali.

Pada Netlify, variabel `VITE_FIREBASE_PROJECT_ID`, `VITE_FIREBASE_AUTH_DOMAIN`, `VITE_FIREBASE_API_KEY`, dan `VITE_FIREBASE_APP_ID` berasal dari konfigurasi Web SDK proyek `ilad-staging`. Isi `VITE_ILAD_API_URL` dengan URL Function `ilad_api` yang sudah terdeploy, tanpa akhiran `/v1/runs`. Gunakan origin Netlify yang sama pada `ILAD_ALLOWED_ORIGINS` di backend. Template variabel tersedia di [web/.env.example](../web/.env.example).

## Staging di Render dengan Firebase Spark

Siapkan database Firestore default dalam mode Production pada proyek `ilad-staging`. Firestore menyimpan metadata dan hasil run dalam satu batch. Hasil dikompresi dan dibagi ke dokumen kecil agar tetap di bawah batas ukuran dokumen. Run Cloud Storage lama memerlukan backend asal atau unggahan ulang.

Di Render, buat Free Web Service dari repositori ILAD dengan branch `codex/ilad-rpi-ci`. Biarkan Root Directory kosong.

| Pengaturan | Nilai |
| --- | --- |
| Language | Python 3 |
| Build Command | `pip install -r firebase/requirements.txt` |
| Start Command | `gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 2 --timeout 120 render_api:app` |
| Health Check Path | `/health` |
| `PYTHON_VERSION` | `3.13.11` |
| `ILAD_FIREBASE_PROJECT` | `ilad-staging` |
| `ILAD_ALLOWED_ORIGINS` | `https://ilad-rpi-dashboard.netlify.app` |
| `GOOGLE_APPLICATION_CREDENTIALS` | `/etc/secrets/firebase-service-account.json` |

Tambahkan kredensial service account khusus backend sebagai Secret File `firebase-service-account.json` di Render. Gunakan izin Firestore untuk membaca dan menulis run serta izin baca akun Firebase Authentication untuk verifikasi token dan status akun. Simpan berkas itu di luar Git dan Netlify.

Setelah `/health` merespons 200, gunakan URL dasar `https://<nama-layanan>.onrender.com` sebagai `VITE_ILAD_API_URL` di Netlify dan deploy ulang frontend. Lakukan uji login, unggah sintetis, refresh, unduhan, dan akses lintas akun pada staging sebelum mengundang peserta.
