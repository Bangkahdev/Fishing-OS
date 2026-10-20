# Fishing OS

> Sebuah proyek sistem operasi berbasis Arch Linux (live ISO, archiso) untuk pengembangan dan eksplorasi.

---

Proyek ini masih dalam tahap pengembangan aktif.
Kami terbuka terhadap masukan, kritik, maupun saran demi perbaikan yang lebih baik ke depannya.

Jika Anda memiliki masukan, silakan hubungi saya melalui [GitHub Issues](https://github.com/Bangkahdev/Fishing-OS/issues) atau platform lain yang tersedia.

---

## Tentang Fishing OS

Fishing OS adalah proyek sistem operasi berbasis Arch Linux yang dikembangkan untuk tujuan:
- Pembelajaran sistem operasi
- Eksperimen personal
- Platform siap pakai untuk pengembang, termasuk kebutuhan DevOps dan infrastruktur as code

Dibangun menggunakan [archiso](https://wiki.archlinux.org/title/Archiso) dengan profil `releng` sebagai basis.

---

## Alat Siap Pakai

| Kategori | Alat |
|---|---|
| Version control | git, gh |
| Kontainer | docker, docker-compose |
| Orkestrasi | kubectl, helm |
| IaC & Config Mgmt | terraform, ansible |
| Bahasa | python3, nodejs, go |
| Build | make, cmake, gcc, gdb |
| Jaringan & Debug | curl, jq, tcpdump, nmap, ssh, mtr |
| Shell & Terminal | zsh, fish, vim, neovim, tmux, fzf, bat, ripgrep |
| Aksesibilitas | speakup (espeak-ng) via opsi boot `with speech` |
| Diagnostik | memtest86+, HDT (Hardware Detection Tool) |

---

## Memulai

Setelah boot ke live ISO (autologin sebagai `liveuser`):

```bash
# Cek versi semua alat pemrograman
fishing-check

# Jalankan Docker daemon
sudo fishing-container up

# Setup awal (user dev, layanan, sudo)
sudo fishing-setup
```

Boot didukung baik mode BIOS (syslinux) maupun UEFI (systemd-boot).
Menu boot diuji otomatis: `tests/check_bootmenu.sh` memastikan entri default
(syslinux `DEFAULT`, GRUB `default=`, systemd-boot `loader.conf`) benar-benar ada.

Catatan Docker: daemon dijalankan manual dan image disimpan di RAM (tmpfs),
jadi image besar akan menghabiskan memori. Jalankan `sudo fishing-container status`
untuk memeriksa status.

---

## Keterbatasan live medium

Ini adalah live/Rescue medium, bukan sistem yang di-install ke disk:

- `root` dan `liveuser` tanpa password adalah perilaku bawaan live medium
  (sama seperti Arch ISO). Ganti kredensial sebelum dipakai di jaringan publik.
- Secure Boot tidak ditandatangani (bootloader tidak di-sign dengan kunci
  Microsoft/`shim`), jadi Secure Boot harus dimatikan di firmware.
- Semua perubahan hilang setelah reboot; tidak ada installer ke disk (fase 2).
- Ukuran ISO dibatasi 2000 MiB agar bisa diunggah ke GitHub Releases, sehingga
  desktop environment dan browser tidak disertakan.
- ISO tidak memuat repositori paket sendiri; `pacman` memakai mirror Arch resmi.

---

## Membangun ISO

Pastikan Anda sedang menjalankan Arch Linux dan telah memasang paket `archiso`:

```bash
sudo pacman -S archiso
mkarchiso -v -w work -o out profile
```

Hasilnya berupa berkas ISO di `out/` siap dibakar ke USB atau dijalankan dalam mesin virtual.

Build CI juga menuliskan versi ISO ke `/etc/os-release` (`VERSION`, `VERSION_ID`,
`BUILD_ID`); build lokal memakai nilai `rolling`.

Uji cepat sebelum merilis:

```bash
bash tests/check_bootmenu.sh          # validasi label/entry menu boot
bash tests/test_iso.sh out/*.iso      # boot ISO di QEMU + smoke test internal
```

---

## Rilis & Verifikasi (SRS)

Build rilis dilakukan di CI (GitHub Actions) dan ditandatangani dengan GPG CI key. Artefak rilis mencakup:

- `*.iso` — image live
- `*.iso.sig` — tanda tangan terpasang ISO
- `sha256sums.txt` — checksum
- `sha256sums.txt.sig` — tanda tangan checksum
- `ci-key-fingerprint.txt` — fingerprint kunci CI

Verifikasi oleh pengguna:

```bash
gpg --locate-keys bangkah@mdhiyaulatha.me
gpg --verify nama.iso.sig nama.iso
```

Fingerprint dipublikasikan melalui WKD (`openpgpkey.mdhiyaulatha.me`) dan halaman `/verifikasi` di situs resmi.

### Mirror Cloudflare R2

Rilis GitHub tetap menjadi kanal utama (ISO < 2000 MiB, `.sig`, checksum).
Sebagai mirror, workflow `release.yml` mengunggah artefak yang sama ke
Cloudflare R2 pada path `releases/<tag>/` dan menambahkan tautan mirror ke
catatan rilis. Jika secrets R2 belum diisi, job mirror dilewati dengan warning
dan rilis GitHub tetap berjalan.

Konfigurasi sekali saja:

1. Cloudflare Dashboard → **R2** → buat bucket, misalnya `fishing-os`.
2. Bucket → **Settings** → **Public access** → hubungkan **Custom domain**
   (misalnya `dl.mdhiyaulatha.me`).
3. **Manage R2 API Tokens** → buat token dengan izin **Object Read & Write**
   untuk bucket tersebut.
4. Isi GitHub repository:

| Tipe | Nama | Isi |
|---|---|---|
| Secret | `R2_ACCOUNT_ID` | Account ID Cloudflare |
| Secret | `R2_ACCESS_KEY_ID` | Access Key ID token R2 |
| Secret | `R2_SECRET_ACCESS_KEY` | Secret Access Key token R2 |
| Secret | `R2_BUCKET` | Nama bucket (`fishing-os`) |
| Variable | `R2_PUBLIC_BASE_URL` | `https://dl.mdhiyaulatha.me` (tanpa slash akhir) |

Setelah rilis bertag `vX`, unduhan tersedia di
`https://dl.mdhiyaulatha.me/releases/vX/` beserta `mirrors.txt` yang memuat
daftar berkas dan URL-nya. Verifikasi tetap memakai checksum + tanda tangan GPG
yang sama seperti kanal GitHub.

---

## Lisensi

Kode dan konfigurasi profil ini dilisensikan di bawah **GNU GPL v3**
(lihat berkas [`LICENSE`](LICENSE)). Paket-paket yang disertakan di dalam ISO
memiliki lisensi masing-masing dari repositori Arch Linux.
