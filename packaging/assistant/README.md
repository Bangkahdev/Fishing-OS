# Computer-Use Assistant — Integrasi OS (Fishing OS)

Direktori ini memuat artefak integrasi OS untuk **Computer-Use Assistant**.
Artefak di sini **tidak** masuk ke Live ISO (SRS §2.2/§9.5, AC-01, NFR-02);
paket ini hanya dipasang ke **Fishing OS yang terpasang ke disk**.

## Isi

| Berkas | Fungsi |
|---|---|
| `fishing-assistant` | Launcher resmi (`/usr/bin/fishing-assistant`) yang menjalankan `python -m fishing_agent`. |
| `fishing-assistant.desktop` | Entri menu aplikasi untuk membuka GUI control panel. |
| `fishing-assistant.service` | Systemd **user** service untuk control plane (IPC) — berjalan sebagai user, bukan root. |
| `install.sh` | Pemasangan pasca-boot ke sistem terpasang (menyalin modul, launcher, desktop, service). |
| `PKGBUILD` | Paket Arch resmi (`makepkg -si`) untuk maintainer/distribusi. |

## Prasyarat runtime (opsional, sesuai backend)

- `xdotool` (input X11) **atau** `ydotool` + `wtype` (input Wayland/Hyprland).
- `grim` (Wayland) **atau** ImageMagick `import` (X11) untuk tangkapan layar.
- `python-pyatspi` untuk grounding AT-SPI2 (aksesibilitas).
- `gnupg` untuk verifikasi signature manifest model.

Tanpa backend input, jalankan dengan `--dry-run` (tidak menyentuh keyboard/mouse).

## Pemasangan

```bash
# Dari root repo, sebagai root pada Fishing OS terpasang:
cd packaging/assistant
sudo ./install.sh

# Atau bangun paket resmi:
cd packaging/assistant
makepkg -si
```

Setelah terpasang:

```bash
fishing-assistant gui        # control panel (Tkinter)
fishing-assistant tui        # antarmuka terminal
fishing-assistant assist "buat presentasi tentang Fishing OS"
fishing-assistant --help     # semua kapabilitas
```

## Batas keamanan (sama dengan runtime agent)

- Control service, model, GUI, dan CLI/TUI berjalan sebagai **user biasa**
  (NFR-18). Operasi administratif meminta autentikasi native OS (`sudo`) dan
  tidak menyimpan password (NFR-20/23).
- Tidak ada aturan `NOPASSWD` atau perubahan sudoers oleh pemasangan.
- Live ISO tetap bersih: `agent/tests/test_packaging_guard.py` (di `agent/tests/`)
  memverifikasi artefak di sini tidak bocor ke `profile/airootfs`.

## Yang masih terbuka (butuh target Linux nyata)

- Aset model LLM/VLM + manifest/checksum/signature (langkah berikutnya).
- Integrasi opsi installer (archinstall) sebagai optional feature.
- Benchmark RAM/VRAM pada hardware referensi dan penguncian runtime inferensi.
- ` fishing-assistant.service` menyediakan control plane IPC; GUI/TUI yang
  menghubungkan diri ke service via IPC (saat ini GUI/TUI membuat
  ControlService lokal — lihat catatan implementasi).