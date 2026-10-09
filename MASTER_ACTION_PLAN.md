# 🎯 Master Action Plan: Claude for Startups ($1,000 Credit)

Gunakan rencana eksekusi berurutan ini untuk menyelesaikan seluruh proses dalam ~15 menit.

---

### ⏱️ Tahap 1: Setup Domain & Email Forwarding Gratis (5 Menit)
- [ ] **1.1. Beli Domain Kustom:**
  - Siapkan domain murah bertema dev tool / AI (contoh: `.dev`, `.com`, `.tech` di Cloudflare/Porkbun seharga ~$2–$10).
- [ ] **1.2. Aktifkan Cloudflare Email Routing (Gratis):**
  - Di Cloudflare: masuk ke menu **Email** > **Email Routing**.
  - Klik **Enable** (DNS MX otomatis terpasang).
  - Buat custom address: `contact@domainanda.dev` yang otomatis me-forward seluruh email ke inbox Gmail pribadi Anda.
  - Verifikasi link konfirmasi di Gmail Anda.

---

### ⏱️ Tahap 2: Kustomisasi & Deploy Landing Page (3 Menit)
- [ ] **2.1. Sesuaikan Nama & Domain Proyek:**
  Jalankan perintah ini di terminal untuk memperbarui seluruh template secara otomatis:
  ```bash
  python3 configure.py --name "NamaProyekAnda" --domain "domainanda.dev" --email "contact@domainanda.dev" --github "username/repo"
  ```
- [ ] **2.2. Preview Lokal (Opsional):**
  ```bash
  python3 -m http.server 3000
  ```
  *(Buka browser di `http://localhost:3000` untuk melihat preview)*.
- [ ] **2.3. Deploy ke Vercel (Gratis):**
  ```bash
  npx vercel deploy --prod
  ```
  - Sambungkan domain kustom di dashboard **Vercel** > **Settings** > **Domains**.
  - Tunggu 1 menit hingga status SSL centang hijau.

---

### ⏱️ Tahap 3: Pendaftaran Akun & Pengajuan Form (5 Menit)
- [ ] **3.1. Buat Akun Claude Console:**
  - Buka [https://console.anthropic.com](https://console.anthropic.com).
  - Registrasi menggunakan email domain kustom Anda (`contact@domainanda.dev`).
  - Kode OTP verifikasi akan masuk ke Gmail Anda via forwarding.
- [ ] **3.2. Buka Form Claude for Startups:**
  - Buka laman resmi program: [anthropic.com/startups](https://www.anthropic.com/startups).
- [ ] **3.3. Salin Data Pitch:**
  - Buka file [`APPLICATION_PITCH.md`](./APPLICATION_PITCH.md).
  - Salin Opsi Pitch 2-Kalimat yang telah disediakan.
  - Masukkan link URL website dan public GitHub repository Anda.

---

### ⏱️ Tahap 4: Approval & Klaim Kredit
- [ ] **4.1. Verifikasi Otomatis:**
  - Bot verifikasi Anthropic akan memeriksa ketersediaan domain dan repo. Persetujuan biasanya terbit instan atau dalam 24–48 jam.
- [ ] **4.2. Klaim $1,000 API Credits:**
  - Kredit otomatis masuk ke dashboard saldo Claude Console (berlaku 6 bulan).
  - Anda juga berhak atas akses 1 tahun Claude Team (5 kursi).
