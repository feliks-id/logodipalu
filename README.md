# Logodipalu — Feliks Logo Designer

Situs portofolio untuk **Feliks**, jasa desain logo profesional yang melayani area Palu dan Kendari. Situs ini merupakan hasil ekspor statis (mirror) dari WordPress, dan di-hosting sebagai situs statis melalui **GitHub Pages**.

🔗 Live: https://feliks-id.github.io/logodipalu/

## Struktur Proyek
logodipalu/
├── index.html                     # Halaman utama
├── pricelist/                     # Halaman daftar harga paket desain logo
│   └── index.html
├── jasa-desain-logo-kendari/      # Halaman layanan khusus area Kendari
│   └── index.html
├── work-gallery/                  # Galeri hasil kerja (2 halaman, dengan paginasi)
│   ├── index.html
│   └── gallery-page-2.html
├── wp-content/                    # Aset tema & plugin WordPress (CSS, JS, gambar upload)
├── wp-includes/                   # Aset inti WordPress yang masih digunakan
├── wp-json/                       # Snapshot data REST API WordPress
└── sitemap.xml                    # Peta situs untuk mesin pencari

## Riwayat & Catatan Teknis

Situs asli dibangun di WordPress (tema Astra) lalu di-mirror menjadi HTML statis menggunakan HTTrack Website Copier. Struktur sebelumnya sempat membingungkan karena proses mirroring; sudah dirapikan (folder duplikat dihapus, nama slug acak diganti jadi deskriptif, link internal diperbaiki).

## Deploy

Situs ini di-hosting via GitHub Pages.