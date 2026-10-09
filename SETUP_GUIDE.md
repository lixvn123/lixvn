# Panduan Eksekusi Step-by-Step: Mendapatkan $1,000 Claude API Credits

Ikuti langkah-langkah praktis dan gratis di bawah ini untuk memenuhi semua kriteria verifikasi otomatis Anthropic.

---

## 🛠️ Langkah 1: Siapkan Domain & Email Bisnis Kustom (Gratis 100%)

Anthropic menolak otomatis email publik (`@gmail.com`). Anda butuh email kustom seperti `contact@namaproject.dev`.

### A. Membeli Domain Murah
- Beli domain murah di **Cloudflare Registrar**, **Namecheap**, atau **Porkbun**.
- Ekstensi yang disukai untuk developer: `.dev`, `.tech`, atau `.com` ($2 - $10 / tahun).

### B. Setup Email Forwarding Gratis via Cloudflare Email Routing
Anda **tidak perlu** membayar Google Workspace ($6/bulan):
1. Arahkan Nameserver domain Anda ke **Cloudflare** (Free Plan).
2. Di dashboard Cloudflare, buka menu **Email** &rarr; **Email Routing**.
3. Klik **Enable Email Routing** dan biarkan Cloudflare menambahkan DNS record MX & TXT secara otomatis.
4. Buat **Custom Address**:
   - Contoh: `contact@namaproject.dev`
   - Destination address: Masukkan email Gmail pribadi Anda (misal: `emailanda@gmail.com`).
5. Verifikasi email tujuan dari inbox Gmail Anda.
6. Sekarang, setiap email yang dikirim ke `contact@namaproject.dev` akan otomatis masuk ke inbox Gmail Anda!

---

## 🚀 Langkah 2: Deploy Landing Page (Gratis via Vercel)

File `index.html` yang telah dibuat adalah file statis mandiri (zero-dependency, Tailwind via CDN).

### Cara Deploy via Vercel CLI (Super Cepat):
```bash
cd /Users/felixvalentino/.gemini/antigravity/scratch/claude-startup-kit
npx vercel deploy --prod
```
1. Pilih `Y` untuk setup project.
2. Hubungkan domain kustom Anda di dashboard Vercel:
   - Masuk ke **Settings** &rarr; **Domains** di Vercel.
   - Tambahkan domain kustom Anda (misal `namaproject.dev` atau `www.namaproject.dev`).
   - Tambahkan CNAME record di Cloudflare sesuai instruksi Vercel.
   - Vercel akan otomatis menerbitkan SSL certificate gratis.

*Alternatif: Anda juga bisa mengupload file `index.html` ini ke repo GitHub Anda dan aktifkan **GitHub Pages**.*

---

## 📝 Langkah 3: Registrasi & Pengajuan Form Anthropic

1. **Buat Akun Claude Console:**
   - Kunjungi [https://console.anthropic.com](https://console.anthropic.com).
   - Daftar menggunakan email kustom Anda (`contact@namaproject.dev`).
   - Kode verifikasi akan masuk ke Gmail pribadi Anda lewat Cloudflare Email Routing.
2. **Kunjungi Form Claude for Startups:**
   - Akses form aplikasi Claude for Startups di website Anthropic ([anthropic.com/startups](https://www.anthropic.com/startups)).
3. **Isi Form:**
   - Salin informasi yang telah disiapkan di file [`APPLICATION_PITCH.md`](./APPLICATION_PITCH.md).
   - Pastikan URL landing page dan GitHub repo berstatus public dan aktif.
4. **Submit:**
   - Sistem pengecekan otomatis biasanya menyetujui dalam hitungan jam hingga 24–48 jam kerja.

---

## 💡 Hal Penting Mengenai Kredit $1,000

- **Masa Berlaku:** Kredit $1,000 valid selama **6 bulan** sejak disetujui.
- **Cakupan API:** Hanya berlaku untuk API resmi di **Claude Console** (direct endpoint `api.anthropic.com`), tidak berlaku untuk AWS Bedrock atau Google Cloud Vertex AI.
- **Claude Code & Claude Team:** Anda juga mendapatkan akses 1 tahun Claude Team (hingga 5 kursi) dan perk partner senilai hingga $45k.
