#!/usr/bin/env bash
# check_installer.sh - Tes whitebox untuk jalur "LiveOS -> terpasang".
#
# Memeriksa hal-hal yang mudah rusak tanpa terlihat:
#   * paket installer (archinstall + alat partisi/format) ada di packages.x86_64
#   * skrip fishingos-install valid, punya shebang bash, dan bisa dijalankan
#   * mode --check/--dry-run/--help berjalan tanpa root
#   * entri desktop ada di skel dan menu aplikasi, menunjuk berkas yang ada
#   * profil memberi mode 755 pada skrip installer
#
# Tidak butuh archinstall terpasang: mode --check hanya melaporkan prasyarat.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INSTALLER_REL="profile/airootfs/usr/local/bin/fishingos-install"
INSTALLER="${ROOT}/${INSTALLER_REL}"
SKEL_DESKTOP="${ROOT}/profile/airootfs/etc/skel/Desktop/fishingos-install.desktop"
MENU_DESKTOP="${ROOT}/profile/airootfs/usr/share/applications/fishingos-install.desktop"
PACKAGES="${ROOT}/profile/packages.x86_64"
PROFILEDEF="${ROOT}/profile/profiledef.sh"

status=0

err() {
    printf '::error::%s\n' "$*"
    status=1
}

pass_msg() {
    printf '[ok] %s\n' "$*"
}

# Paket wajib untuk memasang sistem ke disk.
REQUIRED_PACKAGES=(
    archinstall
    arch-install-scripts
    parted
    dosfstools
    e2fsprogs
    btrfs-progs
    ntfs-3g
    exfatprogs
)

check_packages() {
    local pkg found
    local -a available=()
    [[ -f "$PACKAGES" ]] || { err "packages.x86_64 tidak ditemukan"; return; }

    while IFS= read -r pkg; do
        pkg="${pkg%%#*}"
        pkg="$(printf '%s' "$pkg" | tr -d '[:space:]')"
        [[ -n "$pkg" ]] && available+=("$pkg")
    done < "$PACKAGES"

    for pkg in "${REQUIRED_PACKAGES[@]}"; do
        found=0
        for candidate in "${available[@]}"; do
            if [[ "$candidate" == "$pkg" ]]; then
                found=1
                break
            fi
        done
        if (( found )); then
            pass_msg "paket installer tersedia: ${pkg}"
        else
            err "packages.x86_64 tidak memuat paket installer '${pkg}'"
        fi
    done
}

check_script() {
    [[ -f "$INSTALLER" ]] || { err "${INSTALLER_REL} tidak ada"; return; }

    if head -n 1 "$INSTALLER" | grep -q '^#!/usr/bin/env bash$'; then
        pass_msg "shebang bash benar"
    else
        err "${INSTALLER_REL}: shebang harus '#!/usr/bin/env bash'"
    fi

    if bash -n "$INSTALLER" 2>/dev/null; then
        pass_msg "sintaks bash valid"
    else
        err "${INSTALLER_REL}: sintaks bash tidak valid"
    fi

    if grep -q $'\r' "$INSTALLER"; then
        err "${INSTALLER_REL}: memakai CRLF (harus LF)"
    fi
    if [[ "$(head -c 3 "$INSTALLER" | od -An -tx1 | tr -d ' \n')" == "efbbbf" ]]; then
        err "${INSTALLER_REL}: memakai BOM UTF-8"
    fi
}

check_modes() {
    local out
    [[ -f "$INSTALLER" ]] || return

    if out="$(bash "$INSTALLER" --help 2>&1)"; then
        pass_msg "mode --help keluar 0"
    else
        err "${INSTALLER_REL} --help gagal"
    fi
    if grep -qi 'liveos' <<< "$out" && grep -qi 'archinstall' <<< "$out"; then
        pass_msg "--help menjelaskan LiveOS dan archinstall"
    else
        err "--help tidak menjelaskan LiveOS/archinstall"
    fi

    if out="$(bash "$INSTALLER" --check 2>&1)"; then
        pass_msg "mode --check keluar 0 tanpa root"
    else
        err "${INSTALLER_REL} --check gagal"
    fi
    if grep -q 'archinstall' <<< "$out"; then
        pass_msg "--check melaporkan archinstall"
    else
        err "--check tidak melaporkan status archinstall"
    fi

    if out="$(bash "$INSTALLER" --dry-run 2>&1)"; then
        pass_msg "mode --dry-run keluar 0"
    else
        err "${INSTALLER_REL} --dry-run gagal"
    fi
    if grep -q '^  archinstall$' <<< "$out"; then
        pass_msg "--dry-run menampilkan perintah archinstall"
    else
        err "--dry-run tidak menampilkan perintah archinstall"
    fi

    if bash "$INSTALLER" --tidak-dikenal >/dev/null 2>&1; then
        err "argumen tak dikenal seharusnya gagal dengan kode != 0"
    else
        pass_msg "argumen tak dikenal ditolak"
    fi
}

check_desktop() {
    local file
    for file in "$SKEL_DESKTOP" "$MENU_DESKTOP"; do
        if [[ -f "$file" ]]; then
            pass_msg "entri desktop ada: ${file#"${ROOT}/"}"
        else
            err "entri desktop tidak ada: ${file#"${ROOT}/"}"
            continue
        fi

        if grep -q '^\[Desktop Entry\]$' "$file" &&
            grep -q '^Type=Application$' "$file" &&
            grep -q '^Name=.' "$file" &&
            grep -q '^Exec=pkexec /usr/local/bin/fishingos-install$' "$file"; then
            pass_msg "kunci desktop lengkap: ${file#"${ROOT}/"}"
        else
            err "entri desktop tidak lengkap: ${file#"${ROOT}/"}"
        fi

        if grep -q '^NoDisplay=true$' "$file"; then
            err "entri installer tidak boleh NoDisplay=true: ${file#"${ROOT}/"}"
        fi
        if grep -q $'\r' "$file"; then
            err "entri desktop memakai CRLF: ${file#"${ROOT}/"}"
        fi
    done

    if [[ -f "$SKEL_DESKTOP" && -f "$MENU_DESKTOP" ]]; then
        if cmp -s "$SKEL_DESKTOP" "$MENU_DESKTOP"; then
            pass_msg "entri skel dan menu identik"
        else
            err "entri skel dan menu berbeda isi"
        fi
    fi

    # Exec dan TryExec harus menunjuk berkas yang benar-benar ada di ISO.
    if [[ -f "$INSTALLER" ]]; then
        pass_msg "Exec menunjuk /usr/local/bin/fishingos-install yang ada"
    else
        err "Exec menunjuk berkas yang tidak ada di airootfs"
    fi
}

check_profiledef() {
    [[ -f "$PROFILEDEF" ]] || { err "profiledef.sh tidak ditemukan"; return; }

    if grep -qF '["/usr/local/bin/fishingos-install"]="0:0:755"' "$PROFILEDEF"; then
        pass_msg "profiledef.sh memberi mode 755 pada installer"
    else
        err "profiledef.sh tidak mengatur izin /usr/local/bin/fishingos-install"
    fi
}

check_packages
check_script
check_modes
check_desktop
check_profiledef

if (( status == 0 )); then
    echo "[PASS] Jalur installer LiveOS -> terpasang konsisten"
fi
exit "${status}"
