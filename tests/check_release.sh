#!/usr/bin/env bash
# check_release.sh - Tes blackbox untuk rilis Fishing OS yang sudah terbit.
#
# Tes ini tidak mem-build apa pun: ia memeriksa artefak yang benar-benar
# diterima pengguna, dari luar, memakai jaringan.
#
# Yang diperiksa:
#   1. Rilis GitHub punya seluruh aset wajib (ISO, ISO.sig, sha256sums.txt,
#      sha256sums.txt.sig, ci-key.asc, ci-key-fingerprint.txt).
#   2. Rantai kepercayaan: ci-key.asc berfingerprint benar, tanda tangan
#      sha256sums.txt valid, dan hash ISO di sha256sums.txt sama dengan digest
#      aset GitHub (tanpa mengunduh ISO 1,7 GiB).
#   3. Mirror Cloudflare R2 menyajikan berkas yang byte-identik dengan GitHub.
#   4. (opsional) WKD mdhiyaulatha.me bisa menemukan kunci yang sama.
#
# Pemakaian:
#   tests/check_release.sh                # rilis terbaru
#   tests/check_release.sh v2026.10.4     # tag tertentu
#   TAG=v2026.10.4 VERIFY_ISO=1 tests/check_release.sh   # unduh + hash ISO
#
# Variabel lingkungan:
#   TAG           tag rilis (default: rilis terbaru)
#   REPO          owner/repo (default: Bangkahdev/Fishing-OS)
#   MIRROR_BASE   basis mirror R2 (default: https://dl.fishingos.bangkah.tech)
#   EXPECTED_FPR  fingerprint kunci rilis
#   WKD_UID       uid untuk uji WKD
#   VERIFY_ISO    1 = unduh ISO dari mirror dan cocokkan sha256
#   SKIP_WKD      1 = lewati uji WKD
#
# Dibutuhkan: curl, jq, gpg, sha256sum, awk.

set -euo pipefail

REPO="${REPO:-Bangkahdev/Fishing-OS}"
TAG="${TAG:-${1:-}}"
MIRROR_BASE="${MIRROR_BASE:-https://dl.fishingos.bangkah.tech}"
EXPECTED_FPR="${EXPECTED_FPR:-69AA973A33A3930BB1C83850F713BCD7D6E8F591}"
WKD_UID="${WKD_UID:-bangkah@mdhiyaulatha.me}"
VERIFY_ISO="${VERIFY_ISO:-0}"
SKIP_WKD="${SKIP_WKD:-0}"
API="https://api.github.com/repos/${REPO}"

SMALL_FILES=(
    sha256sums.txt
    sha256sums.txt.sig
    ci-key.asc
    ci-key-fingerprint.txt
)

WORKDIR="$(mktemp -d)"
GNUPGHOME_CI="${WORKDIR}/gnupg"

cleanup() {
    gpgconf --homedir "$GNUPGHOME_CI" --kill all 2>/dev/null || true
    rm -rf "$WORKDIR"
}
trap cleanup EXIT

log() { printf '%s\n' "$*"; }
pass() { printf '[PASS] %s\n' "$*"; }
warn() { printf '[WARN] %s\n' "$*"; }
fail() {
    printf '[FAIL] %s\n' "$*"
    exit 1
}

for cmd in curl jq gpg sha256sum; do
    command -v "$cmd" >/dev/null 2>&1 || fail "$cmd tidak terpasang"
done

normalize_fpr() { printf '%s' "$1" | tr -d '[:space:]' | tr '[:upper:]' '[:lower:]'; }
EXPECTED_NORM="$(normalize_fpr "$EXPECTED_FPR")"

# --- 1. Resolusi rilis -------------------------------------------------------
if [[ -z "$TAG" ]]; then
    log "Mencari rilis terbaru ${REPO}..."
    TAG="$(curl -fsSL "${API}/releases/latest" | jq -r '.tag_name // empty')" ||
        fail "Gagal menghubungi GitHub API"
    [[ -n "$TAG" ]] || fail "Tidak ada rilis terbaru"
fi
log "Rilis: ${TAG} (${REPO})"

RELEASE_JSON="${WORKDIR}/release.json"
curl -fsSL "${API}/releases/tags/${TAG}" -o "$RELEASE_JSON" ||
    fail "Rilis ${TAG} tidak ditemukan di GitHub"

asset_url() {
    jq -r --arg n "$1" \
        '.assets[] | select(.name == $n) | .browser_download_url' "$RELEASE_JSON" | head -n1
}
asset_size() {
    jq -r --arg n "$1" '.assets[] | select(.name == $n) | .size' "$RELEASE_JSON" | head -n1
}
asset_digest() {
    jq -r --arg n "$1" '.assets[] | select(.name == $n) | .digest // empty' \
        "$RELEASE_JSON" | head -n1
}

ISO_NAME="$(jq -r '.assets[].name | select(endswith(".iso"))' "$RELEASE_JSON" | head -n1)"
[[ -n "$ISO_NAME" ]] || fail "Rilis ${TAG} tidak memuat berkas .iso"
ISO_SIG="${ISO_NAME}.sig"

REQUIRED=("${SMALL_FILES[@]}" "$ISO_NAME" "$ISO_SIG")
for name in "${REQUIRED[@]}"; do
    url="$(asset_url "$name")"
    [[ -n "$url" ]] || fail "Aset wajib hilang dari rilis: ${name}"
    pass "aset GitHub ada: ${name}"
done

# --- 2. Unduh berkas kecil dan verifikasi rantai kepercayaan ------------------
for name in "${SMALL_FILES[@]}"; do
    curl -fsSL "$(asset_url "$name")" -o "${WORKDIR}/${name}" ||
        fail "Gagal mengunduh ${name}"
done

mkdir -p "$GNUPGHOME_CI"
chmod 700 "$GNUPGHOME_CI"
export GNUPGHOME="$GNUPGHOME_CI"
gpg --batch --quiet --import "${WORKDIR}/ci-key.asc" 2>/dev/null ||
    fail "ci-key.asc tidak bisa diimpor"

KEY_FPR="$(gpg --batch --with-colons --list-keys 2>/dev/null |
    awk -F: '/^fpr:/ {print $10; exit}')"
[[ -n "$KEY_FPR" ]] || fail "Tidak ada kunci publik di ci-key.asc"
if [[ "$(normalize_fpr "$KEY_FPR")" == "$EXPECTED_NORM" ]]; then
    pass "fingerprint ci-key.asc cocok (${KEY_FPR})"
else
    fail "fingerprint ci-key.asc (${KEY_FPR}) != ${EXPECTED_FPR}"
fi

FPRFILE_NORM="$(tr -d '[:space:]' < "${WORKDIR}/ci-key-fingerprint.txt" |
    tr '[:upper:]' '[:lower:]')"
if [[ "$FPRFILE_NORM" == *"$(normalize_fpr "$KEY_FPR")"* ]]; then
    pass "ci-key-fingerprint.txt menyebut kunci yang sama"
else
    warn "ci-key-fingerprint.txt tidak menyebut ${KEY_FPR}"
fi

gpg --batch --verify "${WORKDIR}/sha256sums.txt.sig" "${WORKDIR}/sha256sums.txt" \
    >/dev/null 2>&1 || fail "Tanda tangan sha256sums.txt tidak valid"
pass "tanda tangan sha256sums.txt valid"

KEY_ID="${KEY_FPR: -16}"
ISO_ENTRY="$(awk -v n="$ISO_NAME" '$2 == n || $2 == "*"n {print $1}' \
    "${WORKDIR}/sha256sums.txt")"
[[ -n "$ISO_ENTRY" ]] || fail "sha256sums.txt tidak memuat entri untuk ${ISO_NAME}"
ISO_SIZE="$(asset_size "$ISO_NAME")"
ISO_DIGEST="$(asset_digest "$ISO_NAME")"
if [[ -n "$ISO_DIGEST" ]]; then
    if [[ "$ISO_DIGEST" == "sha256:${ISO_ENTRY}" ]]; then
        pass "hash ISO di sha256sums.txt sama dengan digest aset GitHub"
    else
        fail "hash ISO sha256sums.txt (${ISO_ENTRY}) != digest GitHub (${ISO_DIGEST})"
    fi
else
    warn "GitHub tidak menyediakan digest aset; melewati pembandingan hash"
fi

curl -fsSL "$(asset_url "$ISO_SIG")" -o "${WORKDIR}/${ISO_SIG}" ||
    fail "Gagal mengunduh ${ISO_SIG}"
if gpg --batch --list-packets "${WORKDIR}/${ISO_SIG}" 2>/dev/null | grep -qi "$KEY_ID"; then
    pass "${ISO_SIG} ditandatangani kunci rilis"
else
    warn "${ISO_SIG} tidak menyebut key id ${KEY_ID} di paket tanda tangan"
fi

# --- 3. Mirror Cloudflare R2 -------------------------------------------------
MIRROR_BASE="${MIRROR_BASE%/}"
MIRROR_DIR="${MIRROR_BASE}/releases/${TAG}"

for name in "${SMALL_FILES[@]}" "$ISO_SIG"; do
    mirror_url="${MIRROR_DIR}/${name}"
    if ! curl -fsSL "$mirror_url" -o "${WORKDIR}/mirror-${name}"; then
        fail "mirror tidak menyajikan ${name}: ${mirror_url}"
    fi
    want="$(sha256sum "${WORKDIR}/${name}" | awk '{print $1}')"
    got="$(sha256sum "${WORKDIR}/mirror-${name}" | awk '{print $1}')"
    if [[ "$want" == "$got" ]]; then
        pass "mirror identik: ${name}"
    else
        fail "mirror berbeda dari GitHub: ${name}"
    fi
done

MIRROR_ISO_HEADERS="${WORKDIR}/iso-headers"
if curl -fsSI "${MIRROR_DIR}/${ISO_NAME}" -o "$MIRROR_ISO_HEADERS"; then
    MIRROR_ISO_SIZE="$(awk 'BEGIN{IGNORECASE=1} /^content-length:/ {gsub(/\r/, "", $2); print $2}' \
        "$MIRROR_ISO_HEADERS")"
    if [[ -n "$MIRROR_ISO_SIZE" && "$MIRROR_ISO_SIZE" == "$ISO_SIZE" ]]; then
        pass "ukuran ISO di mirror sama dengan GitHub (${ISO_SIZE} byte)"
    elif [[ -n "$MIRROR_ISO_SIZE" ]]; then
        fail "ukuran ISO mirror (${MIRROR_ISO_SIZE}) != GitHub (${ISO_SIZE})"
    else
        warn "mirror tidak mengirim Content-Length untuk ISO"
    fi
else
    fail "mirror tidak menyajikan ISO: ${MIRROR_DIR}/${ISO_NAME}"
fi

if [[ "$VERIFY_ISO" == "1" ]]; then
    log "Mengunduh ISO dari mirror untuk verifikasi sha256..."
    curl -fsSL "${MIRROR_DIR}/${ISO_NAME}" -o "${WORKDIR}/${ISO_NAME}" ||
        fail "Gagal mengunduh ISO dari mirror"
    (cd "$WORKDIR" && sha256sum -c --ignore-missing sha256sums.txt) >/dev/null ||
        fail "sha256 ISO mirror tidak cocok"
    pass "sha256 ISO mirror cocok"
fi

# --- 4. WKD (peringatan saja) ------------------------------------------------
if [[ "$SKIP_WKD" != "1" ]]; then
    WKD_HOME="${WORKDIR}/gnupg-wkd"
    mkdir -p "$WKD_HOME"
    chmod 700 "$WKD_HOME"
    WKD_FPR=""
    if GNUPGHOME="$WKD_HOME" gpg --batch --quiet \
        --auto-key-locate clear,wkd --locate-keys "$WKD_UID" >/dev/null 2>&1; then
        WKD_FPR="$(GNUPGHOME="$WKD_HOME" gpg --batch --with-colons --list-keys 2>/dev/null |
            awk -F: '/^fpr:/ {print $10; exit}')"
    fi
    if [[ -n "$WKD_FPR" && "$(normalize_fpr "$WKD_FPR")" == "$EXPECTED_NORM" ]]; then
        pass "WKD ${WKD_UID} mengembalikan kunci rilis"
    else
        warn "WKD ${WKD_UID} belum mengembalikan kunci rilis (cadangan: ci-key.asc)"
    fi
fi

log "[PASS] Rilis ${TAG} lolos verifikasi blackbox"
