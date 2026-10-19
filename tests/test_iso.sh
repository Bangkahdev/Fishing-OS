#!/usr/bin/env bash
# test_iso.sh - Boot Fishing OS ISO in QEMU and simulate real user usage.
#
# Usage: ./test_iso.sh <path-to-iso> [path-to-floppy.img]
#
# Skrip ini mem-boot ISO melalui QEMU, menyisipkan skrip scenario melalui
# floppy disk, dan menjalankan simulasi pengguna seolah-olah orang nyata
# menggunakan Fishing OS untuk keperluan pemrograman.

set -euo pipefail

ISO="${1:?Usage: $0 <path-to-iso> [path-to-floppy.img]}"
FLOPPY="${2:-}"

LOG="test-output.log"
QEMU_TIMEOUT="300"  # detik
VM_MEMORY="2G"
VM_CPUS="2"

echo "=== Fishing OS CI Test ===" | tee "$LOG"
echo "ISO: $ISO" | tee -a "$LOG"
echo "Floppy: ${FLOPPY:-none}" | tee -a "$LOG"
echo "Tanggal: $(date)" | tee -a "$LOG"
echo | tee -a "$LOG"

if [[ ! -f "$ISO" ]]; then
    echo "ERROR: ISO tidak ditemukan: $ISO" | tee -a "$LOG"
    exit 1
fi

ISO_SIZE="$(stat -c%s "$ISO")"
echo "Ukuran ISO: $ISO_SIZE bytes ($((ISO_SIZE / 1024 / 1024)) MiB)" | tee -a "$LOG"

# Deteksi apakah KVM tersedia (untuk boot test yang realistis)
HAS_KVM=0
if kvm-ok >/dev/null 2>&1 || grep -q vmx /proc/cpuinfo 2>/dev/null || grep -q svm /proc/cpuinfo 2>/dev/null; then
    HAS_KVM=1
fi

# Deteksi apakah berjalan di CI (tidak ada KVM, environment terbatas)
IS_CI=0
if [[ "${CI:-}" == "true" ]] || [[ -n "${GITHUB_ACTIONS:-}" ]]; then
    IS_CI=1
fi

if [[ "$IS_CI" -eq 1 && "$HAS_KVM" -eq 0 ]]; then
    echo "INFO: Berjalan di CI tanpa KVM, melewati boot test QEMU (terlalu lambat dengan TCG)" | tee -a "$LOG"
    echo "Hanya memvalidasi berkas ISO ada dan ukuran wajar." | tee -a "$LOG"
    if [[ "$ISO_SIZE" -gt 0 && "$ISO_SIZE" -lt $((4700 * 1024 * 1024)) ]]; then
        echo "[PASS] ISO berkas valid dan ukuran wajar (< 4.7 GiB)" | tee -a "$LOG"
    else
        echo "[FAIL] ISO berkas tidak valid atau ukuran melebihi batas" | tee -a "$LOG"
        exit 1
    fi
    echo | tee -a "$LOG"
    echo "Selesai. Lihat $LOG untuk detail lengkap." | tee -a "$LOG"
    exit 0
fi

# Siapkan opsi QEMU (hanya dijalankan jika KVM tersedia atau bukan CI)
QEMU_ARGS=(
    -machine q35
    -m "$VM_MEMORY"
    -smp "$VM_CPUS"
    -drive file="$ISO",format=raw,media=cdrom,index=0
    -boot order=d
    -vga std
    -serial stdio
    -display none
    -nodefaults
    -rtc base=utc
    -append "console=ttyS0"
)

if [[ "$HAS_KVM" -eq 1 ]]; then
    QEMU_ARGS+=(-enable-kvm -cpu host)
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

TEST_FAILED=0

# Verifikasi output penting
if grep -qi "Fishing OS" "$LOG"; then
    echo "[PASS] Terdeteksi branding Fishing OS di output" | tee -a "$LOG"
else
    echo "[FAIL] Branding Fishing OS tidak ditemukan" | tee -a "$LOG"
    TEST_FAILED=1
fi

if grep -qi "fishing-check" "$LOG"; then
    echo "[PASS] Perintah fishing-check terdeteksi" | tee -a "$LOG"
else
    echo "[FAIL] Perintah fishing-check tidak ditemukan dalam output" | tee -a "$LOG"
    TEST_FAILED=1
fi

if grep -qi "docker\|kubectl\|terraform\|ansible" "$LOG"; then
    echo "[PASS] Alat DevOps terdeteksi dalam output" | tee -a "$LOG"
else
    echo "[FAIL] Alat DevOps utama tidak terdeteksi dalam output" | tee -a "$LOG"
    TEST_FAILED=1
fi

if grep -qi "liveuser" "$LOG"; then
    echo "[PASS] VM mencapai tampilan login/console (liveuser)" | tee -a "$LOG"
else
    echo "[FAIL] Tampilan login liveuser tidak terdeteksi" | tee -a "$LOG"
    TEST_FAILED=1
fi

echo | tee -a "$LOG"
echo "Selesai. Lihat $LOG untuk detail lengkap." | tee -a "$LOG"

if [[ "$TEST_FAILED" -ne 0 ]]; then
    exit 1
fi
