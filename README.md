# Fishing OS

[![CI](https://github.com/Bangkahdev/Fishing-OS/actions/workflows/ci.yml/badge.svg)](https://github.com/Bangkahdev/Fishing-OS/actions/workflows/ci.yml)
[![Lint](https://github.com/Bangkahdev/Fishing-OS/actions/workflows/lint.yml/badge.svg)](https://github.com/Bangkahdev/Fishing-OS/actions/workflows/lint.yml)
[![Rilis terbaru](https://img.shields.io/github/v/release/Bangkahdev/Fishing-OS)](https://github.com/Bangkahdev/Fishing-OS/releases/latest)

**Fishing OS** adalah live/rescue ISO berbasis Arch Linux untuk pengembang dan
engineer DevOps. Boot dari USB atau mesin virtual, lalu langsung punya git,
Docker, kubectl, Helm, Terraform, Ansible, toolchain pemrograman, dan desktop
XFCE dengan Firefox tanpa instalasi apa pun.

> Status: pengembangan aktif. ISO menyediakan **live medium konsol (zsh) plus
> desktop XFCE** (autologin `liveuser`). Installer ke disk masih rencana fase 2.

---

## Isi

- [Unduh](#unduh)
- [Verifikasi unduhan](#verifikasi-unduhan)
- [Menjalankan ISO](#menjalankan-iso)
- [Memulai](#memulai)
- [Alat siap pakai](#alat-siap-pakai)
- [Keterbatasan](#keterbatasan)
- [Membangun ISO](#membangun-iso)
- [Struktur repositori](#struktur-repositori)
- [CI/CD dan rilis](#cicd-dan-rilis)
- [Masukan dan kontribusi](#masukan-dan-kontribusi)
- [Lisensi](#lisensi)

---

## Unduh

Ambil rilis terbaru di halaman
[Releases](https://github.com/Bangkahdev/Fishing-OS/releases/latest).
Setiap rilis berisi:

| Berkas | Fungsi |
|---|---|
| `fishing-os-VERSI-x86_64.iso` | Image live (BIOS dan UEFI) |
| `fishing-os-VERSI-x86_64.iso.sig` | Tanda tangan GPG untuk ISO |
| `sha256sums.txt` | Checksum SHA-256 |
| `sha256sums.txt.sig` | Tanda tangan GPG untuk checksum |
| `ci-key-fingerprint.txt` | Fingerprint kunci penandatangan |

`VERSI` mengikuti tag rilis `vAAAA.BB.N` (misalnya tag `v2026.10.3` menghasilkan
`fishing-os-2026.10.3-x86_64.iso`). Jika rilis menyertakan tautan mirror
(Cloudflare R2), tautannya ada di catatan rilis.

---

## Verifikasi unduhan

**Selalu verifikasi ISO sebelum dipakai.** Rilis ditandatangani oleh kunci CI
Fishing OS. Kunci publiknya diambil lewat WKD dari domain `mdhiyaulatha.me`.

| | |
|---|---|
| Identitas | `Fishing OS CI <bangkah@mdhiyaulatha.me>` |
| Jenis kunci | RSA 4096 |
| **Fingerprint** | `69AA 973A 33A3 930B B1C8 3850 F713 BCD7 D6E8 F591` |

Di Linux, macOS, atau WSL (ganti `VERSI` dengan versi yang kamu unduh):

```bash
VERSI=2026.10.3

# 1. Ambil kunci publik lewat WKD
gpg --auto-key-locate clear,wkd --locate-keys bangkah@mdhiyaulatha.me

# 2. Cocokkan fingerprint dengan tabel di atas
gpg --fingerprint bangkah@mdhiyaulatha.me

# 3. Verifikasi tanda tangan pada checksum
gpg --verify sha256sums.txt.sig sha256sums.txt

# 4. Cocokkan checksum ISO
sha256sum -c --ignore-missing sha256sums.txt

# 5. (Opsional) verifikasi tanda tangan ISO secara langsung
gpg --verify fishing-os-$VERSI-x86_64.iso.sig fishing-os-$VERSI-x86_64.iso
```

Hasil yang benar pada langkah 3 dan 5 adalah
`Good signature from "Fishing OS CI <bangkah@mdhiyaulatha.me>"`.

Peringatan `The key's User ID is not certified with a trusted signature` itu
**normal** untuk kunci yang baru kamu ambil: artinya kamu belum menyatakan
mempercayainya, bukan tanda tangannya salah. Yang penting, baris
`Primary key fingerprint` harus sama persis dengan fingerprint di atas.

Di Windows tanpa `gpg`, kamu bisa mencocokkan checksum dengan PowerShell:

```powershell
Get-FileHash .\fishing-os-VERSI-x86_64.iso -Algorithm SHA256
```

Hasilnya harus sama dengan baris untuk ISO di `sha256sums.txt`. Untuk
memverifikasi tanda tangan, pakai [Gpg4win](https://www.gpg4win.org/) atau WSL.

> **Cocokkan fingerprint dari sedikitnya dua sumber yang berbeda**, misalnya
> README ini dan halaman rilis (`ci-key-fingerprint.txt`). Kunci yang diambil
> dari satu tempat saja belum membuktikan apa-apa. Kunci CI dirotasi berkala;
> pengumuman rotasi dan fingerprint baru dipublikasikan di halaman rilis.

---

## Menjalankan ISO

**Mesin virtual (disarankan untuk mencoba).** RAM 2 GB atau lebih, satu CPU
atau lebih. Contoh dengan QEMU (mode BIOS):

```bash
qemu-system-x86_64 -enable-kvm -m 4G -smp 2 \
  -cdrom fishing-os-VERSI-x86_64.iso -boot d
```

Untuk mode UEFI tambahkan firmware OVMF sesuai distro kamu. Di VirtualBox,
VMware, atau Hyper-V, pasang ISO sebagai DVD.

**USB.** Tulis ISO sebagai image mentah (jangan sekadar menyalin berkas):

```bash
sudo dd if=fishing-os-VERSI-x86_64.iso of=/dev/sdX bs=4M status=progress oflag=sync
```

Ganti `/dev/sdX` dengan perangkat USB yang benar; perintah ini menghapus
seluruh isinya. Di Windows gunakan Rufus dengan mode **DD Image**, atau Ventoy.

**Secure Boot harus dimatikan** di firmware, karena bootloader belum
ditandatangani untuk Secure Boot.

Menu boot menyediakan entri live, opsi `with speech` (pembaca layar), memtest86+,
dan HDT (informasi perangkat keras). Setelah login, LightDM masuk otomatis ke
sesi XFCE sebagai `liveuser`.

---

## Memulai

Setelah boot, LightDM masuk otomatis ke **desktop XFCE** sebagai `liveuser`.
Untuk bekerja di konsol, buka terminal (mis. `xfce4-terminal`) atau tekan
`Ctrl+Alt+F2` untuk TTY; shell default adalah zsh.

```bash
# Cek versi semua alat pemrograman
fishing-check

# Jalankan Docker daemon
sudo fishing-container up

# Setup awal: user dev, layanan, sudo
sudo fishing-setup
```

| Perintah | Fungsi |
|---|---|
| `fishing-check` | Menampilkan alat yang terpasang beserta versinya |
| `fishing-container up \| down \| status` | Mengelola Docker daemon |
| `fishing-setup` | Mengaktifkan layanan jaringan dan membuat user `dev` (wheel, docker) |

**Jaringan.** Ethernet, WLAN, dan WWAN memakai `systemd-networkd` dan DHCP
otomatis. Untuk Wi-Fi pakai `iwctl`:

```bash
iwctl
# di dalam iwctl: station wlan0 scan, station wlan0 get-networks,
#                 station wlan0 connect NAMA-WIFI
```

**Catatan Docker.** Daemon dijalankan manual dan image disimpan di RAM
(tmpfs), jadi image besar menghabiskan memori. Periksa dengan
`sudo fishing-container status`.

---

## Alat siap pakai

| Kategori | Alat |
|---|---|
| Version control | git, gh |
| Kontainer | docker, docker-compose |
| Orkestrasi | kubectl, helm |
| IaC dan konfigurasi | terraform, ansible (ansible-core) |
| Bahasa | python3 dan pip, nodejs dan npm, go |
| Build | make, cmake, gcc, gdb |
| Jaringan dan debug | curl, wget, jq, tcpdump, nmap, socat, mtr, traceroute, ssh, iproute2 |
| Shell dan editor | zsh, fish, bash, vim, neovim, nano, tmux, fzf, bat, fd, ripgrep, htop |
| Desktop | XFCE (xfce4, xfce4-goodies), LightDM, Firefox |
| Informasi sistem | fastfetch (logo huruf F), htop, dmidecode |
| Perangkat keras | dmidecode, pciutils, usbutils, memtest86+ |
| Aksesibilitas | espeak-ng dan espeakup (opsi boot `with speech`) |

Ansible dibawa sebagai `ansible-core` (tanpa koleksi lengkap) supaya ISO tetap
kecil. Pasang koleksi yang kamu perlukan dengan `ansible-galaxy collection install`.

---

## Keterbatasan

Fishing OS adalah **live/rescue medium**, bukan sistem yang dipasang ke disk.

- `root` dan `liveuser` tanpa password adalah perilaku bawaan live medium
  (sama seperti Arch ISO). Layanan `sshd` aktif secara bawaan. User `dev` dari
  `fishing-setup` memakai password yang kamu atur dan sudo tanpa password.
  **Jangan pakai di jaringan yang tidak tepercaya** tanpa mengganti kredensial.
- Semua perubahan hilang setelah reboot. Installer ke disk belum ada (fase 2).
- Batas ukuran ISO 2000 MiB mengikuti batas berkas GitHub Releases; penambahan
  desktop dan Firefox masih berada dalam batas ini.
- Secure Boot tidak didukung (lihat bagian menjalankan ISO).
- ISO tidak memuat repositori paket sendiri; `pacman` memakai mirror Arch resmi.

---

## Membangun ISO

Butuh Arch Linux (atau container Arch) dengan paket `archiso`:

```bash
sudo pacman -S archiso
sudo mkarchiso -v -w work -o out profile
```

Hasilnya ada di `out/`. Build lokal memakai nilai `rolling` pada `/etc/os-release`;
build CI mengisinya dengan versi ISO.

Uji cepat sebelum merilis (butuh `qemu-system-x86_64` dan `xorriso`):

```bash
bash tests/check_bootmenu.sh        # validasi label/entri menu boot
bash tests/test_iso.sh out/*.iso    # boot ISO di QEMU + smoke test internal
```

`test_iso.sh` mengekstrak kernel dan initramfs dari ISO, mem-boot-nya di QEMU
dengan `fishing.test=1`, lalu mewajibkan penanda `FISHING-SMOKETEST: PASS` dari
`fishing-smoketest.service` di konsol serial.

---

## Struktur repositori

```
.
├── profile/                   Profil archiso
│   ├── profiledef.sh          Metadata ISO
│   ├── packages.x86_64        Daftar paket
│   ├── pacman.conf
│   ├── airootfs/              Isi sistem live (konfigurasi, skrip fishing-*)
│   ├── syslinux/              Menu boot BIOS
│   ├── efiboot/               Menu boot UEFI (systemd-boot)
│   └── grub/                  Konfigurasi GRUB
├── tests/                     check_bootmenu.sh, test_iso.sh
├── docs/SRS.md                Spesifikasi kebutuhan perangkat lunak
└── .github/workflows/         Pipeline CI/CD
```

---

## CI/CD dan rilis

| Workflow | Pemicu | Isi |
|---|---|---|
| `lint.yml` | push dan PR ke `main` | shellcheck, yamllint, berkas kosong, branding menu boot, validasi menu boot, ketersediaan paket |
| `ci.yml` | push dan PR ke `main` | build ISO (batas 2000 MiB) dan smoke test di QEMU |
| `nightly.yml` | mingguan | build dengan repositori Arch terbaru; membuka issue otomatis bila gagal |
| `release.yml` | tag `v*` | build, smoke test, tanda tangan GPG, mirror R2 (opsional), publikasi GitHub Release |
| `build.yml` | dipanggil workflow lain | build dan smoke test (reusable) |

Untuk merilis: pastikan CI di `main` hijau, lalu beri tag dan push.

```bash
git tag v2026.10.4
git push origin v2026.10.4
```

### Mirror Cloudflare R2 (opsional)

Rilis GitHub tetap menjadi kanal utama. Jika secrets R2 terisi, `release.yml`
juga mengunggah artefak ke `releases/<tag>/` di bucket R2 dan menambahkan
tautan mirror ke catatan rilis. Jika belum diisi, job mirror dilewati dengan
peringatan dan rilis GitHub tetap berjalan.

| Tipe | Nama | Isi |
|---|---|---|
| Secret | `R2_ACCOUNT_ID` | Account ID Cloudflare |
| Secret | `R2_ACCESS_KEY_ID` | Access Key ID token R2 |
| Secret | `R2_SECRET_ACCESS_KEY` | Secret Access Key token R2 |
| Secret | `R2_BUCKET` | Nama bucket |
| Variable | `R2_PUBLIC_BASE_URL` | URL publik bucket, tanpa slash akhir |

Verifikasi unduhan dari mirror sama dengan kanal GitHub: checksum dan tanda
tangan GPG yang sama.

---

## Masukan dan kontribusi

Proyek ini terbuka untuk masukan, kritik, dan saran. Silakan buka
[GitHub Issues](https://github.com/Bangkahdev/Fishing-OS/issues), atau kirim
Pull Request ke `main`. Sebelum mengirim PR, jalankan `shellcheck` pada skrip
yang kamu ubah dan `bash tests/check_bootmenu.sh`; `lint.yml` memeriksa hal yang
sama.

Rencana dan keputusan desain ada di [`docs/SRS.md`](docs/SRS.md).

---

## Lisensi

Kode dan konfigurasi profil ini dilisensikan di bawah **GNU GPL v3**
(lihat [`LICENSE`](LICENSE)). Paket-paket di dalam ISO memiliki lisensi
masing-masing dari repositori Arch Linux.