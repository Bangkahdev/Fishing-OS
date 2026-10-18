# Fishing OS

> Sebuah proyek sistem operasi berbasis Arch Linux (live ISO, archiso) untuk pengembangan dan eksplorasi.

---

Proyek ini masih dalam tahap pengembangan aktif.
Kami terbuka terhadap masukan, kritik, maupun saran demi perbaikan yang lebih baik ke depannya.

Jika Anda memiliki masukan, silakan hubungi saya melalui [GitHub Issues](https://github.com/Bangkah/Fishing-OS/issues) atau platform lain yang tersedia.

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
| Build | make, cmake, gcc, clang, gdb |
| Jaringan & Debug | curl, jq, tcpdump, nmap, ssh, mtr |
| Shell & Terminal | zsh, fish, vim, neovim, tmux, fzf, bat, ripgrep |

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

---

## Membangun ISO

Pastikan Anda sedang menjalankan Arch Linux dan telah memasang paket `archiso`:

```bash
sudo pacman -S archiso
mkarchiso -v -w work -o out profile
```

Hasilnya berupa berkas ISO di `out/` siap dibakar ke USB atau dijalankan dalam mesin virtual.

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

---

Lisensi: Lihat berkas `LICENSE` (jika tersedia).
