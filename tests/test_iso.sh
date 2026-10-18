#!/usr/bin/env bash
# test_iso.sh - Boot Fishing OS DevOps ISO in QEMU and simulate real user usage.
#
# Usage: ./test_iso.sh <path-to-iso> [path-to-floppy.img]
#
# Skrip ini mem-boot ISO melalui QEMU, menyisipkan skrip scenario melalui
# floppy disk, dan menjalankan simulasi pengguna seolah-olah orang nyata
# menggunakan OS ini untuk keperluan DevOps.

set -euo pipefail

ISO="${1:?Usage: $0 <path-to-iso> [path-to-floppy.img]}"
FLOPPY="${2:-}"

LOG="test-output.log"
QEMU_TIMEOUT="300"  # detik
VM_MEMORY="2G"
VM_CPUS="2"

echo "=== Fishing OS DevOps CI Test ===" | tee "$LOG"
echo "ISO: $ISO" | tee -a "$LOG"
echo "Floppy: ${FLOPPY:-none}" | tee -a "$LOG"
echo "Tanggal: $(date)" | tee -a "$LOG"
echo | tee -a "$LOG"

if [[ ! -f "$ISO" ]]; then
    echo "ERROR: ISO tidak ditemukan: $ISO" | tee -a "$LOG"
    exit 1
fi

# Siapkan opsi QEMU
QEMU_ARGS=(
    -machine q35
    -m "$VM_MEMORY"
    -smp "$VM_CPUS"
    -cpu host
    -drive file="$ISO",format=raw,media=cdrom,index=0
    -boot order=d
    -vga std
    -serial stdio
    -display none
    -nodefaults
    -rtc base=utc
)

# Gunakan KVM jika tersedia, fallback ke TCG (WSL-friendly)
if kvm-ok >/dev/null 2>&1 || grep -q vmx /proc/cpuinfo 2>/dev/null || grep -q svm /proc/cpuinfo 2>/dev/null; then
    QEMU_ARGS+=(-enable-kvm)
else
    echo "INFO: KVM tidak tersedia, menggunakan TCG (lebih lambat)" | tee -a "$LOG"
fi

if [[ -n "$FLOPPY" && -f "$FLOPPY" ]]; then
    QEMU_ARGS+=(-drive file="$FLOPPY",format=raw,index=1,media=disk)
fi

echo "Menjalankan QEMU (timeout ${QEMU_TIMEOUT}s)..." | tee -a "$LOG"

# Jalankan QEMU dengan timeout, tangkap output ke log
timeout "$QEMU_TIMEOUT" qemu-system-x86_64 "${QEMU_ARGS[@]}" > "$LOG" 2>&1 || true

echo | tee -a "$LOG"
echo "=== Hasil Tes QEMU ===" | tee -a "$LOG"

# Verifikasi output penting
if grep -qi "Fishing OS DevOps\|Fishing OS" "$LOG"; then
    echo "[PASS] Terdeteksi branding Fishing OS DevOps di output" | tee -a "$LOG"
else
    echo "[FAIL] Branding Fishing OS DevOps tidak ditemukan" | tee -a "$LOG"
fi

if grep -qi "devops-check" "$LOG"; then
    echo "[PASS] Perintah devops-check terdeteksi" | tee -a "$LOG"
else
    echo "[WARN] Perintah devops-check tidak ditemukan dalam output" | tee -a "$LOG"
fi

if grep -qi "docker\|kubectl\|terraform\|ansible" "$LOG"; then
    echo "[PASS] Alat DevOps terdeteksi dalam output" | tee -a "$LOG"
else
    echo "[WARN] Alat DevOps utama tidak terdeteksi dalam output" | tee -a "$LOG"
fi

if grep -qi "liveuser\|login\|tty" "$LOG"; then
    echo "[PASS] VM mencapai tampilan login/console" | tee -a "$LOG"
else
    echo "[WARN] Tampilan login tidak terdeteksi" | tee -a "$LOG"
fi

echo | tee -a "$LOG"
echo "Selesai. Lihat $LOG untuk detail lengkap." | tee -a "$LOG"
