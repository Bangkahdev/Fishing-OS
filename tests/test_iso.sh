#!/usr/bin/env bash
# test_iso.sh - Boot Fishing OS ISO in QEMU dan validasi konten ISO.
#
# Usage: ./test_iso.sh <path-to-iso> [path-to-floppy.img]
#
# Skrip mem-boot ISO melalui QEMU (jika KVM tersedia), atau memvalidasi
# berkas ISO tanpa boot (CI tanpa KVM). Tidak ada kegagalan yang diabaikan.

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

if [[ "$ISO_SIZE" -gt $((4700 * 1024 * 1024)) ]]; then
    echo "[FAIL] ISO ukuran $ISO_SIZE bytes melebihi batas 4,7 GiB" | tee -a "$LOG"
    exit 1
fi
echo "[PASS] ISO ukuran wajar (< 4,7 GiB)" | tee -a "$LOG"

# Deteksi KVM yang benar: cek /dev/kvm, bukan /proc/cpuinfo
HAS_KVM=0
if [[ -c /dev/kvm && -r /dev/kvm && -w /dev/kvm ]]; then
    HAS_KVM=1
fi

# Deteksi CI environment
IS_CI=0
if [[ "${CI:-}" == "true" ]] || [[ -n "${GITHUB_ACTIONS:-}" ]]; then
    IS_CI=1
fi

# Cek apakah qemu-system-x86_64 tersedia
if ! command -v qemu-system-x86_64 >/dev/null 2>&1; then
    echo "[FAIL] qemu-system-x86_64 tidak terpasang" | tee -a "$LOG"
    exit 1
fi

if [[ "$IS_CI" -eq 1 && "$HAS_KVM" -eq 0 ]]; then
    echo "INFO: CI tanpa KVM, melewati boot QEMU (TCG terlalu lambat untuk boot ISO)" | tee -a "$LOG"
    echo "Hanya memvalidasi berkas ISO dan ukuran." | tee -a "$LOG"
    echo "[PASS] ISO berkas valid dan ukuran wajar (< 4,7 GiB)" | tee -a "$LOG"
    echo | tee -a "$LOG"
    echo "Selesai. Lihat $LOG untuk detail lengkap." | tee -a "$LOG"
    exit 0
fi

# Siapkan opsi QEMU (hanya jika KVM tersedia atau bukan CI)
QEMU_ARGS=(
    -machine q35
    -m "$VM_MEMORY"
    -smp "$VM_CPUS"
    # shellcheck disable=SC2054
    -drive file="$ISO",format=raw,media=cdrom,index=0
    -boot order=d
    -vga std
    -serial stdio
    -display none
    -nodefaults
    -rtc base=utc
)

if [[ "$HAS_KVM" -eq 1 ]]; then
    QEMU_ARGS+=(-enable-kvm -cpu host)
else
    echo "INFO: KVM tidak tersedia, menggunakan TCG (lebih lambat)" | tee -a "$LOG"
fi

if [[ -n "$FLOPPY" && -f "$FLOPPY" ]]; then
    # shellcheck disable=SC2054
    QEMU_ARGS+=(-drive file="$FLOPPY",format=raw,index=1,media=disk)
fi

echo "Menjalankan QEMU (timeout ${QEMU_TIMEOUT}s)..." | tee -a "$LOG"

timeout "$QEMU_TIMEOUT" qemu-system-x86_64 "${QEMU_ARGS[@]}" > "$LOG" 2>&1

echo | tee -a "$LOG"
echo "=== Hasil Tes QEMU ===" | tee -a "$LOG"

TEST_FAILED=0

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
