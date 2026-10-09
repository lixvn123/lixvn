# 🌐 Panduan Lengkap Pembelian Domain & Setup Email Bisnis Gratis

Panduan ini menjelaskan tempat membeli domain termurah, metode pembayaran yang didukung di Indonesia, dan cara mengaktifkan email domain gratis dalam 5 menit.

---

## 🏆 1. Rekomendasi Tempat Beli Domain

| Registrar | Biaya Rata-rata | Keunggulan Utama | Metode Pembayaran |
| :--- | :--- | :--- | :--- |
| **Cloudflare Registrar** *(Paling Direkomendasikan)* | **At-cost** (~$9.77/thn untuk `.com`, ~$12/thn untuk `.dev`) | Tanpa markup harga, gratis privasi WHOIS selamanya, dan **langsung terhubung** dengan Cloudflare Email Routing tanpa perlu setting Nameserver manual. | Kartu Debit/Kredit (Visa/Mastercard: Jenius, Jago, Mandiri, BCA), PayPal |
| **Porkbun** | Mulai **$2 - $10/thn** (sering ada diskon) | Biaya perpanjangan transparan, interface simpel, gratis WHOIS privacy. | Kartu Debit/Kredit, PayPal, Crypto |
| **Domainesia / Niagahoster** *(Lokal)* | Mulai **Rp 15.000 - Rp 150.000/thn** | Cocok jika **tidak memiliki kartu debit/kredit internasional**; bisa bayar lewat QRIS, GoPay, OVO, atau transfer bank lokal. | QRIS, GoPay, Transfer Bank BCA/Mandiri/BRI |

---

## 🚀 2. Panduan Langkah Demi Langkah: Pembelian via Cloudflare

Cloudflare adalah opsi tercepat karena Anda tidak perlu memindahkan nameserver:

### Langkah A: Pendaftaran Akun
1. Buka [https://dash.cloudflare.com/sign-up](https://dash.cloudflare.com/sign-up).
2. Buat akun menggunakan email Anda dan login ke dashboard.

### Langkah B: Cari & Beli Domain
1. Di bilah navigasi kiri, pilih **Domain Registration** &rarr; **Register Domains**.
2. Ketik nama domain yang diinginkan (contoh yang terlihat profesional untuk AI/DevTool):
   - `[namaproject]pulse.com`
   - `[namaproject]dev.com`
   - `[namaproject].dev`
   - `[namaproject]ai.tech`
3. Klik **Purchase**.
4. Isi data pendaftaran (nama & alamat). *Catatan: Data pribadi Anda otomatis disembunyikan gratis oleh Cloudflare WHOIS Redaction.*
5. Masukkan pembayaran kartu debit online (pastikan fitur debit online / transaksi luar negeri aktif di aplikasi bank Anda: misal Bank Jago, Jenius BTPN, BCA Debit Mastercard, atau Blu BCA).
6. Konfirmasi pembayaran. Domain akan aktif seketika (kurang dari 1 menit).

---

## 📬 3. Panduan Setup Cloudflare Email Routing (100% Gratis)

Setelah domain aktif di Cloudflare:

1. Di dashboard Cloudflare, klik domain yang baru saja Anda beli.
2. Di menu sebelah kiri, klik **Email** &rarr; **Email Routing**.
3. Klik tombol **Get Started** atau **Enable Email Routing**.
4. Cloudflare akan menampilkan konfirmasi untuk menambahkan DNS Record (MX dan TXT). Klik **Add records and enable**.
5. Di bagian **Destination addresses**:
   - Masukkan alamat Gmail pribadi Anda (misal: `namasaya@gmail.com`).
   - Buka inbox Gmail Anda, cari email dari Cloudflare, dan klik tombol **Verify email address**.
6. Di bagian **Routing rules**:
   - Klik **Create address**.
   - Masukkan custom address: `contact` (sehingga menjadi `contact@domainanda.com`).
   - Pilih destination address: Gmail Anda yang sudah terverifikasi.
   - Klik **Save**.
7. **Uji Coba:** Kirim email dari akun lain ke `contact@domainanda.com`. Email akan langsung masuk ke inbox Gmail Anda!

---

## 💡 Alternatif jika Membeli di Registrar Lokal (Niagahoster/Domainesia)

Jika Anda membeli lewat registrar lokal:
1. Daftarkan akun gratis di Cloudflare.
2. Klik **Add a site** di Cloudflare dan masukkan nama domain Anda.
3. Pilih paket **Free ($0)**.
4. Salin 2 Nameserver yang diberikan Cloudflare (contoh: `alec.ns.cloudflare.com` & `zoe.ns.cloudflare.com`).
5. Buka dashboard domain registrar lokal Anda (Niagahoster/Domainesia), masuk ke menu **DNS Management / Nameserver**, dan ganti nameserver lama dengan kedua nameserver Cloudflare tersebut.
6. Tunggu propagasi DNS (sekitar 5–15 menit). Setelah aktif, lanjutkan setup **Email Routing** seperti pada Bagian 3 di atas.
