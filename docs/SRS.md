# Software Requirements Specification (SRS)

## Distro Live Berbasis Arch Linux (archiso)

|  |  |
| --- | --- |
| **Dokumen** | SRS-FINAL |
| **Versi** | 1.6 |
| **Status** | Final — direvisi 2026-10-21 |
| **Tanggal** | 2026-10-21 |
| **Changelog 1.1** | Nama distro: Fishing OS; domain ditandai sebagai keputusan pending |
| **Changelog 1.2** | Domain dikunci: `mdhiyaulatha.me` (D-5 final), semua placeholder terisi |
| **Changelog 1.3** | Seksi 6 disederhanakan untuk proyek satu orang — tetap ada sebagai jejak audit |
| **Changelog 1.4** | Batas ukuran ISO menjadi ≤ 2000 MiB (batas aset GitHub Releases); DE dan browser ditunda ke fase 2; validasi menu boot ditambah ke lint CI |
| **Changelog 1.5** | Mirror rilis ke Cloudflare R2 (opsional, `FR-CI-11`) |
| **Changelog 1.6** | ISO fase 1 dinyatakan live medium konsol (zsh, alat DevOps) — bukan desktop; WKD dicatat via metode direct; smoke test di VM wajib lulus sebelum rilis; backlog fase 2 (DE, installer, CLI `fishing`) dicatat di §7 |
| **Basis** | archiso (profil `releng`), target x86_64, live medium konsol |

- Distro: **Fishing OS** (`iso_name=fishing-os`)
- Domain: **`mdhiyaulatha.me`** (WKD aktif via metode direct `https://mdhiyaulatha.me/.well-known/openpgpkey/hu/<hash>`; subdomain `openpgpkey.mdhiyaulatha.me` belum dikonfigurasi)

---

# 1. Pendahuluan

## 1.1 Tujuan

Dokumen ini mendefinisikan kebutuhan fungsional dan non-fungsional untuk distribusi Linux live berbasis Arch Linux yang dibangun dengan archiso, termasuk pipeline rilis berkelanjutan di CI dengan penandatanganan kriptografis.

## 1.2 Ruang Lingkup

Termasuk: konfigurasi profil archiso, daftar paket, branding, pipeline CI (build–sign–publish), prosedur verifikasi pengguna, manajemen kunci.
Tidak termasuk pada fase 1: installer ke disk (lihat §7), lingkungan desktop & browser (fase 2, §7), repositori paket kustom, arsitektur non-x86_64.

## 1.3 Definisi

- **ISO** — berkas image live yang dihasilkan `mkarchiso`.
- **CI key** — kunci GPG khusus penandatanganan rilis otomatis, hanya ada di GitHub Secrets.
- **Cold key** — kunci GPG rilis manager, disimpan offline.
- **WKD** — Web Key Directory, metode publikasi kunci OpenPGP via HTTPS (`openpgpkey.mdhiyaulatha.me`).

---

# 2. Deskripsi Umum

## 2.1 Fungsi Produk

Distribusi live USB/Linux yang dapat di-boot langsung, berbasis konsol (zsh) dengan toolchain DevOps siap pakai, dengan kepercayaan rilis yang dapat diverifikasi secara kriptografis oleh pengguna. Lingkungan desktop ditunda ke fase 2 (§7).

## 2.2 Kelas Pengguna

1. **Pengguna akhir** — mengunduh ISO, memverifikasi, membuat live USB.
2. **Rilis manager** — memegang cold key, mengelola rotasi kunci, menyetujui rilis.
3. **Kontributor** — mengusulkan perubahan via pull request; tidak menyentuh kunci atau rilis.

## 2.3 Batasan Desain

- Build hanya di CI (GitHub Actions, runner `ubuntu-latest`), bukan di mesin pengembang.
- Tidak ada private key dalam repositori dalam bentuk apa pun.
- Semua artefak rilis harus dapat diverifikasi tanpa mempercayai satu kanal tunggal.

---

# 3. Kebutuhan Fungsional

## 3.1 Konfigurasi ISO (FR-ISO)

| ID | Kebutuhan | Prioritas | Status |
| --- | --- | --- | --- |
| FR-ISO-01 | Profil dibangun dari `releng` sebagai basis, disalin ke direktori repo `profile/` | Must | Final |
| FR-ISO-02 | `profiledef.sh` menetapkan `iso_name=fishing-os`, `iso_label=FISHINGOS_YYYYMM`, `iso_publisher` | Must | Final |
| FR-ISO-03 | Daftar paket diatur di `packages.x86_64`; tambahan wajib: editor, utilitas sistem, toolchain DevOps. Shell default zsh; DE dan browser ditunda ke fase 2 (§7) | Must | Final (revisi 1.6) |
| FR-ISO-04 | `airootfs/` berisi konfigurasi: hostname `FishingOS`, user live default, service yang di-enable | Must | Final |
| FR-ISO-05 | Bootloader menampilkan branding Fishing OS (menu GRUB/syslinux) | Should | Final |
| FR-ISO-06 | Ukuran ISO hasil build ≤ 2000 MiB (batas aset GitHub Releases) | Must | Final (revisi 1.4) |

## 3.2 Pipeline CI (FR-CI)

| ID | Kebutuhan | Prioritas | Status |
| --- | --- | --- | --- |
| FR-CI-01 | Build ISO terpicu otomatis pada setiap push ke `main` dan pull request | Must | Final |
| FR-CI-02 | Build rilis hanya terpicu pada tag `v*` | Must | Final |
| FR-CI-03 | Artefak ISO dari pull request diunggah sebagai build artifact (bukan rilis), retensi 14 hari | Must | Final |
| FR-CI-04 | Pipeline build wajib idempotent: workspace bersih setiap run | Must | Final |
| FR-CI-05 | Workflow tidak pernah mengekspor nilai secret ke log | Must | Final |
| FR-CI-06 | Build gagal jika ukuran ISO melebihi batas FR-ISO-06 | Should | Final |
| FR-CI-07 | Versi ISO mengikuti pola `YYYY.MM.N` (N = rilis ke-N dalam bulan itu) | Must | Final |
| FR-CI-08 | Halaman rilis otomatis berisi changelog dari commit sejak tag sebelumnya | Should | Final |
| FR-CI-09 | Fingerprint kunci penandatangan dipublikasikan sebagai teks plain di setiap halaman rilis | Must | Final |
| FR-CI-10 | Penandatanganan GPG & publikasi ISO — lihat §3.3 | Must | Final |
| FR-CI-11 | Mirror artefak rilis ke Cloudflare R2 bila secrets R2 tersedia; tautan mirror ditambahkan ke catatan rilis | Should | Final (revisi 1.5) |
| FR-CI-12 | Setiap halaman rilis wajib memuat `*.iso`, `*.iso.sig`, `sha256sums.txt`, `sha256sums.txt.sig`, dan `ci-key-fingerprint.txt` | Must | Final (revisi 1.6) |
| FR-CI-13 | Rilis hanya diterbitkan setelah smoke test boot di VM lulus (`FISHING-SMOKETEST: PASS`) | Must | Final (revisi 1.6) |

## 3.3 Penandatanganan GPG & Publikasi ISO — FR-CI-10 (Final)

### 1. Penyimpanan Kunci

Private key **tidak pernah** disimpan di repositori git dalam bentuk apa pun. Kunci rilis ada tepat di dua tempat:

1. **Cold key** — YubiKey/smartcard, passphrase ≥20 karakter, hanya dipegang rilis manager; dipakai untuk penandatanganan manual jika pipeline CI jebol.
2. **CI key** — kunci khusus rilis, hanya ada sebagai GitHub Secrets `GPG_PRIVATE_KEY` + `GPG_PASSPHRASE`. Tidak ada salinan lain di mesin mana pun.

### 2. Alur Rilis (Workflow CI)

1. CI build ISO via `mkarchiso`.
2. CI menghasilkan `sha256sums.txt`.
3. CI mengimpor CI key dari secrets, lalu *detach-sign* ISO dan checksum.
4. CI mengunggah `*.iso`, `*.iso.sig`, `sha256sums.txt`, `sha256sums.txt.sig`, dan fingerprint plain-text ke halaman rilis.

### 3. Kanal Publikasi Fingerprint (dua kanal independen)

- **WKD**: metode direct di `https://mdhiyaulatha.me/.well-known/openpgpkey/hu/<hash>` (hash = z-base-32 dari SHA-1 local-part) — memungkinkan `gpg --locate-keys bangkah@mdhiyaulatha.me`. Subdomain `openpgpkey.mdhiyaulatha.me` (metode advanced) belum dikonfigurasi.
- **Situs resmi**: halaman `/verifikasi` berisi fingerprint dan prosedur verifikasi.

### 4. Verifikasi oleh Pengguna

```bash
gpg --locate-keys bangkah@mdhiyaulatha.me
gpg --fingerprint bangkah@mdhiyaulatha.me   # cocokkan dengan situs resmi
gpg --verify nama.iso.sig nama.iso # harus: Good signature
```

Pesan `not certified with a trusted signature` dianggap normal; trust berasal dari pencocokan fingerprint lewat kanal independen.

### 5. Rotasi & Pencabutan

- CI key: rotasi tiap 12 bulan atau segera jika ada indikasi bocor.
- Cold key: rotasi tiap 3–5 tahun; kunci lama dipublikasikan berstatus *revoked*.
- Pengumuman rotasi ≥30 hari sebelum rilis pertama dengan kunci baru.

**Catatan kepatuhan:** tanda tangan hanya bernilai jika (a) kunci privat terisolasi dari repo, (b) fingerprint diverifikasi via kanal independen, (c) ada prosedur rotasi. Kegagalan satu syarat = tanda tangan tidak menambah kepercayaan.

## 3.4 Persyaratan Non-Fungsional

| ID | Kebutuhan | Target |
| --- | --- | --- |
| NFR-01 | Waktu build ISO di CI | ≤ 60 menit |
| NFR-02 | ISO dapat boot di mode UEFI dan Legacy BIOS | 100% rilis wajib lolos |
| NFR-03 | Boot ke login prompt konsol | ≤ 90 detik di VM (2 vCPU, 4 GiB); waktu boot desktop diukur pada fase 2 |
| NFR-04 | Reproducibility | build ulang dari commit yang sama menghasilkan checksum identik *(stretch goal — tidak menghalangi rilis fase 1)* |

---

# 4. Matriks Verifikasi

| Kebutuhan | Metode verifikasi |
| --- | --- |
| FR-ISO-01..05 | Boot ISO hasil CI di QEMU (`tests/test_iso.sh`) + lint statis menu boot (`tests/check_bootmenu.sh`) |
| FR-ISO-06 | Assertion di workflow: `stat -c%s` vs batas |
| FR-CI-01..05 | Uji pipeline: push dummy, inspeksi log (tidak ada secret bocor) |
| FR-CI-10.1 | Audit repo: `git log -p` bebas kunci; audit Secrets (hanya org admin) |
| FR-CI-10.2 | Rilis uji di repo sandbox, verifikasi artefak lengkap |
| FR-CI-10.3 | WKD: `gpg --auto-key-locate wkd --locate-keys bangkah@mdhiyaulatha.me` dari mesin bersih harus berhasil |
| FR-CI-10.4 | Prosedur verifikasi dijalankan dari mesin bersih (tanpa keyring lama) |
| FR-CI-12 | Inspeksi aset halaman rilis: ISO, `.sig`, checksum, fingerprint semuanya ada |
| FR-CI-13 | Log job smoke-test berisi `FISHING-SMOKETEST: PASS` sebelum job sign/release jalan |
| NFR-02 | Uji boot UEFI + BIOS di QEMU tiap rilis; label default menu divalidasi statis (`tests/check_bootmenu.sh`) di lint CI |

---

# 5. Asumsi & Keputusan Tercatat

| # | Keputusan | Pilihan |
| --- | --- | --- |
| D-1 | Model kunci CI | Opsi A — kunci CI di GitHub Secrets (automasi penuh) |
| D-2 | Kanal fingerprint | WKD + halaman `/verifikasi` di situs resmi |
| D-3 | Basis profil | `releng` (bukan `baseline`) |
| D-4 | Platform CI | GitHub Actions |
| D-5 | Domain resmi | `mdhiyaulatha.me` (keputusan: gunakan domain portfolio, WKD aktif) |
| D-6 | Lingkungan desktop | Ditunda ke fase 2 (§7); ISO fase 1 berbasis konsol |
| D-7 | Penomoran versi | Tag `vYYYY.MM.N` menentukan versi ISO; N = rilis ke-N dalam bulan |

---

# 6. Persetujuan

Proyek ini dikerjakan oleh satu orang; seluruh peran (pembuat produk, rilis manager, engineer) berada pada diri yang sama. Seksi ini tetap dipertahankan sebagai jejak audit — terutama untuk keputusan D-1/D-2/D-5 yang menyangkut trust model FR-CI-10.

| Peran | Nama | Tanda tangan | Tanggal |
| --- | --- | --- | --- |
| Pembuat & Rilis Manager | Muhammad Dhiyaul Atha | *Bangkah* | 2026-10-19 |
| Revisi 1.6 | Muhammad Dhiyaul Atha | *Bangkah* | 2026-10-21 |

---

# 7. Backlog Fase 2 (di luar SRS ini)

Item berikut sengaja **tidak** menjadi bagian SRS v1.6; dicatat di sini agar keputusan tidak hilang.

- **Lingkungan desktop** — pilih XFCE atau Hyprland; butuh server tampilan (Xorg/Wayland), display manager, dan konfigurasi autostart.
- **Installer ke disk** — mis. `archinstall`; butuh jaringan dan perencanaan partisi.
- **CLI `fishing`** — manajemen alat on-demand; butuh mekanisme instalasi paket (skrip atau repositori kustom).
- **Browser & aplikasi kantor ringan**.

Setiap item wajib direvisi ke SRS terpisah sebelum dikerjakan. Penambahan paket dapat menaikkan ukuran ISO, sehingga batas FR-ISO-06 (2000 MiB) perlu dievaluasi ulang.