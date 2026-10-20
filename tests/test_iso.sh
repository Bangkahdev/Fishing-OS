#!/usr/bin/env bash
# test_iso.sh - Smoke test ISO Fishing OS.
#
# Usage: ./test_iso.sh <path-to-iso>
#
# Langkah:
#   1. Validasi berkas ISO: ada, ukuran <= 2000 MiB, checksum (jika
#      sha256sums.txt ada di folder yang sama).
#   2. Ekstrak kernel dan initramfs dari ISO, lalu boot langsung di QEMU
#      dengan console=ttyS0 dan fishing.test=1.
#   3. Tunggu penanda boot (login prompt) atau FISHING-SMOKETEST: PASS
#      di konsol serial.
#
# Variabel lingkungan (opsional):
#   QEMU_TIMEOUT  batas waktu boot, detik (default 300 dengan KVM, 1500 tanpa)
#   VM_MEMORY     memori VM (default 3G)
#   VM_CPUS       jumlah vCPU (default 2)
#   LOG           log hasil tes (default test-output.log)
#   SERIAL_LOG    log konsol serial VM (default qemu-serial.log)
#   QEMU_ERR_LOG  log stderr QEMU (default qemu-stderr.log)
#
# Dibutuhkan: qemu-system-x86_64, xorriso.

set -euo pipefail

ISO="${1:?Usage: $0 <path-to-iso>}"
LOG="${LOG:-test-output.log}"
SERIAL_LOG="${SERIAL_LOG:-qemu-serial.log}"
QEMU_ERR_LOG="${QEMU_ERR_LOG:-qemu-stderr.log}"
VM_MEMORY="${VM_MEMORY:-3G}"
VM_CPUS="${VM_CPUS:-2}"
MAX_SIZE=$((2000 * 1024 * 1024))
MARK="FISHING-SMOKETEST:"

WORKDIR="$(mktemp -d)"
QEMU_PID=""

cleanup() {
    if [[ -n "$QEMU_PID" ]] && kill -0 "$QEMU_PID" 2>/dev/null; then
        kill "$QEMU_PID" 2>/dev/null || true
        wait "$QEMU_PID" 2>/dev/null || true
    fi
    rm -rf "$WORKDIR"
}
trap cleanup EXIT

: > "$LOG"
: > "$SERIAL_LOG"
: > "$QEMU_ERR_LOG"

log()  { echo "$*" | tee -a "$LOG"; }
pass() { log "[PASS] $*"; }
fail() { log "[FAIL] $*"; exit 1; }

show_serial_tail() {
    log "--- 60 baris terakhir konsol serial ---"
    tail -n 60 "$SERIAL_LOG" | tee -a "$LOG" || true
    log "---------------------------------------"
}

log "=== Fishing OS smoke test ==="
log "ISO: $ISO"
log "Tanggal: $(date -u)"

# --- 1. Validasi berkas ---
[[ -f "$ISO" ]] || fail "ISO tidak ditemukan: $ISO"

ISO_SIZE="$(stat -c%s "$ISO")"
log "Ukuran ISO: $((ISO_SIZE / 1024 / 1024)) MiB"
if (( ISO_SIZE > MAX_SIZE )); then
    fail "ISO melebihi batas 2000 MiB"
fi
pass "Ukuran ISO dalam batas"

ISO_DIR="$(dirname "$ISO")"
if [[ -f "$ISO_DIR/sha256sums.txt" ]]; then
    if (cd "$ISO_DIR" && sha256sum -c --ignore-missing sha256sums.txt) >> "$LOG" 2>&1; then
        pass "Checksum SHA256 cocok"
    else
        fail "Checksum SHA256 tidak cocok"
    fi
fi

for cmd in qemu-system-x86_64 xorriso; do
    command -v "$cmd" >/dev/null 2>&1 || fail "$cmd tidak terpasang"
done

# --- 2. Ekstrak kernel dan initramfs ---
PVD="$(xorriso -indev "$ISO" -pvd_info 2>&1)" || fail "xorriso gagal membaca ISO"
LABEL="$(printf '%s\n' "$PVD" | sed -n 's/^Volume Id *: *//p' | tr -d '\r' | sed -n 1p)"
[[ -n "$LABEL" ]] || fail "Label volume ISO tidak terbaca"
log "Label ISO: $LABEL"

xorriso -osirrox on -indev "$ISO" \
    -extract /arch/boot/x86_64/vmlinuz-linux "$WORKDIR/vmlinuz-linux" \
    -extract /arch/boot/x86_64/initramfs-linux.img "$WORKDIR/initramfs-linux.img" \
    >> "$LOG" 2>&1 || fail "Gagal mengekstrak kernel/initramfs dari ISO"
[[ -s "$WORKDIR/vmlinuz-linux" && -s "$WORKDIR/initramfs-linux.img" ]] \
    || fail "Kernel atau initramfs kosong setelah ekstraksi"
pass "Kernel dan initramfs terekstrak"

# --- 3. Boot di QEMU ---
if [[ -c /dev/kvm && -r /dev/kvm && -w /dev/kvm ]]; then
    ACCEL_ARGS=(-enable-kvm -cpu host)
    QEMU_TIMEOUT="${QEMU_TIMEOUT:-300}"
    log "KVM tersedia (timeout ${QEMU_TIMEOUT}s)"
else
    ACCEL_ARGS=(-cpu max)
    QEMU_TIMEOUT="${QEMU_TIMEOUT:-1500}"
    log "KVM tidak tersedia, memakai emulasi TCG (timeout ${QEMU_TIMEOUT}s, lambat)"
fi

QEMU_ARGS=(
    -machine q35
    -m "$VM_MEMORY"
    -smp "$VM_CPUS"
    "${ACCEL_ARGS[@]}"
    -kernel "$WORKDIR/vmlinuz-linux"
    -initrd "$WORKDIR/initramfs-linux.img"
    -append "archisobasedir=arch archisolabel=$LABEL console=ttyS0 fishing.test=1"
    -drive "file=$ISO,format=raw,media=cdrom,readonly=on"
    -display none
    -monitor none
    -serial "file:$SERIAL_LOG"
    -no-reboot
)

log "Menjalankan QEMU..."
qemu-system-x86_64 "${QEMU_ARGS[@]}" > "$QEMU_ERR_LOG" 2>&1 &
QEMU_PID=$!

TIMED_OUT=0
SECONDS=0
BOOTED=0
SMOKE_PASSED=0
SMOKE_FAILED=0
while kill -0 "$QEMU_PID" 2>/dev/null; do
    if grep -qF "$MARK PASS" "$SERIAL_LOG"; then
        SMOKE_PASSED=1
        break
    fi
    if grep -qF "$MARK FAIL" "$SERIAL_LOG"; then
        SMOKE_FAILED=1
        break
    fi
    if grep -q "login:" "$SERIAL_LOG"; then
        BOOTED=1
    fi
    if (( SECONDS >= QEMU_TIMEOUT )); then
        TIMED_OUT=1
        break
    fi
    sleep 3
done

# Beri waktu singkat agar sisa output serial tertulis, lalu hentikan VM.
sleep 2
if kill -0 "$QEMU_PID" 2>/dev/null; then
    kill "$QEMU_PID" 2>/dev/null || true
 fi
wait "$QEMU_PID" 2>/dev/null || true
QEMU_PID=""

# --- 4. Evaluasi ---
grep -F "$MARK" "$SERIAL_LOG" >> "$LOG" || true

if (( TIMED_OUT )); then
    show_serial_tail
    fail "Timeout ${QEMU_TIMEOUT}s: penanda '$MARK PASS' tidak muncul"
fi

if (( SMOKE_PASSED )); then
    pass "Smoke test di dalam VM lulus"
    exit 0
fi

if (( SMOKE_FAILED )); then
    show_serial_tail
    fail "Smoke test di dalam VM melaporkan kegagalan (lihat baris MISSING/BAD)"
fi

if (( BOOTED )); then
    log "Catatan: login prompt terdeteksi, tetapi penanda '$MARK PASS' tidak muncul"
fi

show_serial_tail
fail "VM tidak melaporkan '$MARK PASS' (lihat $QEMU_ERR_LOG)"
