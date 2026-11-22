#!/usr/bin/env bash
# install.sh - pasang Computer-Use Assistant ke Fishing OS yang sudah terpasang.
#
# Jalankan sebagai root pada sistem Fishing OS terpasang (BUKAN di Live ISO).
# Skrip menyalin artefak ke lokasi resmi lalu mengaktifkan user service.
# Tidak mengubah sudoers, tidak menyimpan password, tidak membuat NOPASSWD
# (NFR-23). Pengguna tetap mengautentikasi lewat sudo/Polkit native.
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST_LIB="/usr/lib/fishing-assistant"
DEST_BIN="/usr/bin/fishing-assistant"
DEST_DESKTOP="/usr/share/applications/fishing-assistant.desktop"
DEST_SERVICE="/usr/lib/systemd/user/fishing-assistant.service"
DEST_DOC="/usr/share/doc/fishing-assistant"

if [[ "${EUID}" -ne 0 ]]; then
    echo "install.sh harus dijalankan sebagai root (sudo ./install.sh)." >&2
    exit 1
fi

# Garda: jangan pasang di dalam Live ISO (Assistant hanya untuk instalasi ke disk).
if grep -qE 'archiso|CDLABEL=[Ff]ISHING|jesus' /proc/cmdline 2>/dev/null; then
    echo "Terdeteksi sesi Live ISO. Assistant hanya untuk instalasi ke disk." >&2
    exit 1
fi

echo "Memasang modul Python ke ${DEST_LIB} ..."
install -d -m 0755 "${DEST_LIB}"
rm -rf "${DEST_LIB}/fishing_agent"
cp -r "${SRC}/../../agent/fishing_agent" "${DEST_LIB}/fishing_agent"
find "${DEST_LIB}" -name '__pycache__' -type d -prune -exec rm -rf {} +

echo "Memasang launcher ke ${DEST_BIN} ..."
install -m 0755 "${SRC}/fishing-assistant" "${DEST_BIN}"

echo "Memasang entri desktop ke ${DEST_DESKTOP} ..."
install -m 0644 "${SRC}/fishing-assistant.desktop" "${DEST_DESKTOP}"

echo "Memasang user service ke ${DEST_SERVICE} ..."
install -d -m 0755 "$(dirname "${DEST_SERVICE}")"
install -m 0644 "${SRC}/fishing-assistant.service" "${DEST_SERVICE}"

echo "Memasang dokumentasi ke ${DEST_DOC} ..."
install -d -m 0755 "${DEST_DOC}"
install -m 0644 "${SRC}/README.md" "${DEST_DOC}/README.md" 2>/dev/null || true

echo "Mengaktifkan user service (jika systemd tersedia) ..."
if command -v systemctl >/dev/null 2>&1; then
    if [[ -n "${SUDO_USER:-}" ]]; then
        runuser -u "${SUDO_USER}" -- systemctl --user daemon-reload || true
        runuser -u "${SUDO_USER}" -- systemctl --user enable --now fishing-assistant.service || true
    fi
fi

echo "Selesai. Jalankan: fishing-assistant gui   (atau: fishing-assistant tui)"
echo "Catatan: model LLM/VLM belum dipaketkan; lihat README untuk langkah berikutnya."